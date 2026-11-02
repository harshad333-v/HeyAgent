"""Transactional SQLite persistence for approval challenges and audit events.

The database is local application state, not a credential vault. Protect its parent
directory with the platform account ACL; store API secrets separately using DPAPI.
"""
from __future__ import annotations

import json
import secrets
import sqlite3
import time
from pathlib import Path
from typing import Any, Iterator
from contextlib import contextmanager

from .audit import AuditEvent, redact
from .models import ActionRequest, CapabilityGrant
from .policy_engine import canonical_action_digest
from .approvals import ApprovalChallenge


_SCHEMA = """
CREATE TABLE IF NOT EXISTS capability_grants (
    grant_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    capabilities_json TEXT NOT NULL,
    allowed_tools_json TEXT NOT NULL,
    allowed_targets_json TEXT NOT NULL,
    expires_at REAL NOT NULL,
    created_at REAL NOT NULL,
    revoked_at REAL
);
CREATE INDEX IF NOT EXISTS idx_grant_principal ON capability_grants(user_id, session_id, expires_at);
CREATE TABLE IF NOT EXISTS approval_challenges (
    challenge_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    action_digest TEXT NOT NULL,
    expires_at REAL NOT NULL,
    approved INTEGER NOT NULL DEFAULT 0 CHECK (approved IN (0, 1)),
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_approval_expiry ON approval_challenges(expires_at);
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    task_id TEXT NOT NULL,
    actor TEXT NOT NULL,
    outcome TEXT NOT NULL,
    details_json TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS audit_events_no_update
BEFORE UPDATE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_events_no_delete
BEFORE DELETE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit events are append-only'); END;
"""


class SQLiteSecurityStore:
    """Small synchronous store; each mutation uses an IMMEDIATE transaction."""

    def __init__(self, database_path: str | Path, *, busy_timeout_ms: int = 5000) -> None:
        self.database_path = str(Path(database_path).expanduser())
        if self.database_path == ":memory:":
            raise ValueError("A file-backed database is required for durable security state.")
        self.busy_timeout_ms = busy_timeout_ms
        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as connection:
            connection.executescript(_SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.database_path, timeout=self.busy_timeout_ms / 1000,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute(f"PRAGMA busy_timeout = {int(self.busy_timeout_ms)}")
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            yield connection
        finally:
            connection.close()

    def save_grant(self, grant: CapabilityGrant, *, now: float | None = None) -> str:
        """Persist a trusted grant and return its opaque identifier."""
        timestamp = time.time() if now is None else now
        if not grant.user_id or not grant.session_id or grant.expires_at <= timestamp:
            raise ValueError("A grant requires a principal, session and future expiry.")
        grant_id = secrets.token_urlsafe(32)
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """INSERT INTO capability_grants
                   (grant_id,user_id,session_id,capabilities_json,allowed_tools_json,
                    allowed_targets_json,expires_at,created_at)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (grant_id, grant.user_id, grant.session_id,
                 json.dumps(sorted(grant.capabilities)),
                 json.dumps(sorted(grant.allowed_tools)),
                 json.dumps(sorted(grant.allowed_targets)), grant.expires_at, timestamp),
            )
            connection.commit()
        return grant_id

    def get_grant(
        self, grant_id: str, *, user_id: str, session_id: str,
        now: float | None = None,
    ) -> CapabilityGrant | None:
        timestamp = time.time() if now is None else now
        with self._connection() as connection:
            row = connection.execute(
                """SELECT * FROM capability_grants
                   WHERE grant_id=? AND user_id=? AND session_id=?
                   AND expires_at>? AND revoked_at IS NULL""",
                (grant_id, user_id, session_id, timestamp),
            ).fetchone()
        if row is None:
            return None
        return CapabilityGrant(
            user_id=row["user_id"], session_id=row["session_id"],
            capabilities=frozenset(json.loads(row["capabilities_json"])),
            allowed_tools=frozenset(json.loads(row["allowed_tools_json"])),
            allowed_targets=frozenset(json.loads(row["allowed_targets_json"])),
            expires_at=row["expires_at"],
        )

    def revoke_grant(
        self, grant_id: str, *, user_id: str, session_id: str,
        now: float | None = None,
    ) -> bool:
        timestamp = time.time() if now is None else now
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """UPDATE capability_grants SET revoked_at=?
                   WHERE grant_id=? AND user_id=? AND session_id=? AND revoked_at IS NULL""",
                (timestamp, grant_id, user_id, session_id),
            )
            connection.commit()
            return cursor.rowcount == 1

    def create_challenge(
        self, action: ActionRequest, *, user_id: str, session_id: str,
        ttl_seconds: int = 120, now: float | None = None,
    ) -> ApprovalChallenge:
        if not 1 <= ttl_seconds <= 600:
            raise ValueError("Approval TTL must be between 1 and 600 seconds.")
        timestamp = time.time() if now is None else now
        challenge = ApprovalChallenge(
            challenge_id=secrets.token_urlsafe(32), user_id=user_id,
            session_id=session_id, task_id=action.task_id,
            action_digest=canonical_action_digest(action),
            expires_at=timestamp + ttl_seconds,
        )
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """INSERT INTO approval_challenges
                   (challenge_id,user_id,session_id,task_id,action_digest,expires_at,created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                (challenge.challenge_id, challenge.user_id, challenge.session_id,
                 challenge.task_id, challenge.action_digest, challenge.expires_at, timestamp),
            )
            connection.commit()
        return challenge

    def approve_challenge(
        self, challenge_id: str, *, user_id: str, session_id: str,
        now: float | None = None,
    ) -> bool:
        timestamp = time.time() if now is None else now
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                """UPDATE approval_challenges SET approved=1
                   WHERE challenge_id=? AND user_id=? AND session_id=?
                   AND expires_at>? AND approved=0""",
                (challenge_id, user_id, session_id, timestamp),
            )
            connection.commit()
            return cursor.rowcount == 1

    def consume_approval(
        self, challenge_id: str | None, action: ActionRequest, *,
        user_id: str, session_id: str, now: float | None = None,
    ) -> bool:
        if not challenge_id:
            return False
        timestamp = time.time() if now is None else now
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM approval_challenges WHERE challenge_id=?",
                (challenge_id,),
            ).fetchone()
            # Delete regardless of validity: a challenge can never be retried.
            connection.execute(
                "DELETE FROM approval_challenges WHERE challenge_id=?", (challenge_id,)
            )
            connection.commit()
        if row is None or not row["approved"] or row["expires_at"] <= timestamp:
            return False
        return (
            row["user_id"] == user_id
            and row["session_id"] == session_id
            and row["task_id"] == action.task_id
            and row["action_digest"] == canonical_action_digest(action)
        )

    def purge_expired(self, *, now: float | None = None) -> int:
        timestamp = time.time() if now is None else now
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            cursor = connection.execute(
                "DELETE FROM approval_challenges WHERE expires_at<=?", (timestamp,)
            )
            count = cursor.rowcount
            connection.commit()
            return count

    def write(self, event: AuditEvent) -> None:
        details = redact(event.details)
        encoded = json.dumps(details, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                """INSERT INTO audit_events
                   (event_type,task_id,actor,outcome,details_json,timestamp)
                   VALUES (?,?,?,?,?,?)""",
                (event.event_type, event.task_id, event.actor, event.outcome, encoded, event.timestamp),
            )
            connection.commit()

    def list_audit_events(self, *, limit: int = 100) -> list[dict[str, Any]]:
        if not 1 <= limit <= 1000:
            raise ValueError("Audit page size must be between 1 and 1000.")
        with self._connect() as connection:
            rows = connection.execute(
                """SELECT id,event_type,task_id,actor,outcome,details_json,timestamp
                   FROM audit_events ORDER BY id DESC LIMIT ?""", (limit,)
            ).fetchall()
        return [
            {"id": row["id"], "event_type": row["event_type"], "task_id": row["task_id"],
             "actor": row["actor"], "outcome": row["outcome"],
             "details": json.loads(row["details_json"]), "timestamp": row["timestamp"]}
            for row in rows
        ]
