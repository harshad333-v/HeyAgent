"""Durable, idempotent task lifecycle storage.

This module deliberately does not execute tasks. It provides the persistence and
state-transition boundary that the future supervised agent runtime will consume.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator


class IdempotencyConflict(ValueError):
    """An idempotency key was reused for a different task payload."""


class TaskNotFound(LookupError):
    """The requested task does not exist."""


class TaskStateConflict(ValueError):
    """The requested state transition is not valid."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _fingerprint(title: str, instruction: str) -> str:
    encoded = json.dumps(
        {"title": title, "instruction": instruction},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class TaskStore:
    """SQLite-backed task records with idempotent creation and guarded cancellation."""

    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 10000")
        return connection

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = self._connect()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute("PRAGMA journal_mode = WAL")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    idempotency_key TEXT UNIQUE,
                    request_fingerprint TEXT NOT NULL,
                    title TEXT NOT NULL,
                    instruction TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (
                        status IN ('queued', 'running', 'waiting_approval',
                                   'succeeded', 'failed', 'cancelled')
                    ),
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    result_json TEXT,
                    error_code TEXT
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at DESC)"
            )

    @staticmethod
    def _serialize(row: sqlite3.Row) -> dict[str, Any]:
        return {
            "id": row["id"],
            "title": row["title"],
            "instruction": row["instruction"],
            "status": row["status"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "result": json.loads(row["result_json"]) if row["result_json"] else None,
            "error_code": row["error_code"],
        }

    def create(
        self, *, title: str, instruction: str, idempotency_key: str | None = None,
    ) -> tuple[dict[str, Any], bool]:
        fingerprint = _fingerprint(title, instruction)
        now = _now()
        task_id = str(uuid.uuid4())
        with self._connection() as connection:
            try:
                connection.execute(
                    """
                    INSERT INTO tasks (
                        id, idempotency_key, request_fingerprint, title, instruction,
                        status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, 'queued', ?, ?)
                    """,
                    (task_id, idempotency_key, fingerprint, title, instruction, now, now),
                )
                row = connection.execute(
                    "SELECT * FROM tasks WHERE id = ?", (task_id,)
                ).fetchone()
                return self._serialize(row), True
            except sqlite3.IntegrityError:
                if not idempotency_key:
                    raise
                row = connection.execute(
                    "SELECT * FROM tasks WHERE idempotency_key = ?",
                    (idempotency_key,),
                ).fetchone()
                if row is None:
                    raise
                if row["request_fingerprint"] != fingerprint:
                    raise IdempotencyConflict(
                        "Idempotency key was already used with a different task payload."
                    )
                return self._serialize(row), False

    def get(self, task_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        if row is None:
            raise TaskNotFound(task_id)
        return self._serialize(row)

    def list(self, *, limit: int = 50, before: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM tasks"
        parameters: list[Any] = []
        if before:
            query += " WHERE created_at < ?"
            parameters.append(before)
        query += " ORDER BY created_at DESC, id DESC LIMIT ?"
        parameters.append(limit)
        with self._connection() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [self._serialize(row) for row in rows]

    def cancel(self, task_id: str) -> dict[str, Any]:
        now = _now()
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            if row is None:
                raise TaskNotFound(task_id)
            if row["status"] == "cancelled":
                return self._serialize(row)
            if row["status"] != "queued":
                raise TaskStateConflict(
                    "Only queued tasks can be cancelled through this endpoint."
                )
            connection.execute(
                "UPDATE tasks SET status = 'cancelled', updated_at = ? WHERE id = ?",
                (now, task_id),
            )
            updated = connection.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            return self._serialize(updated)
