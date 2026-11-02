"""Single-use, exact-action approval challenges.

The in-memory store is suitable for unit tests and a single-process prototype only.
Production must replace it with a transactional persistent store so replay protection
survives restarts and multiple workers.
"""
from __future__ import annotations

import secrets
import time
from dataclasses import dataclass
from threading import RLock

from .models import ActionRequest
from .policy_engine import canonical_action_digest


@dataclass(frozen=True, slots=True)
class ApprovalChallenge:
    challenge_id: str
    user_id: str
    session_id: str
    task_id: str
    action_digest: str
    expires_at: float


class ApprovalManager:
    def __init__(self, *, ttl_seconds: int = 120) -> None:
        if ttl_seconds < 1 or ttl_seconds > 600:
            raise ValueError("Approval TTL must be between 1 and 600 seconds.")
        self._ttl = ttl_seconds
        self._pending: dict[str, ApprovalChallenge] = {}
        self._approved: set[str] = set()
        self._lock = RLock()

    def create(self, action: ActionRequest, *, user_id: str, session_id: str, now: float | None = None) -> ApprovalChallenge:
        timestamp = time.time() if now is None else now
        challenge = ApprovalChallenge(
            challenge_id=secrets.token_urlsafe(32), user_id=user_id, session_id=session_id,
            task_id=action.task_id, action_digest=canonical_action_digest(action),
            expires_at=timestamp + self._ttl,
        )
        with self._lock:
            self._pending[challenge.challenge_id] = challenge
        return challenge

    def approve(self, challenge_id: str, *, user_id: str, session_id: str, now: float | None = None) -> bool:
        timestamp = time.time() if now is None else now
        with self._lock:
            challenge = self._pending.get(challenge_id)
            if challenge is None or challenge.expires_at <= timestamp:
                self._pending.pop(challenge_id, None)
                return False
            if challenge.user_id != user_id or challenge.session_id != session_id:
                return False
            self._approved.add(challenge_id)
            return True

    def consume(self, challenge_id: str | None, action: ActionRequest, *, user_id: str, session_id: str, now: float | None = None) -> bool:
        if not challenge_id:
            return False
        timestamp = time.time() if now is None else now
        with self._lock:
            challenge = self._pending.pop(challenge_id, None)
            approved = challenge_id in self._approved
            self._approved.discard(challenge_id)
            if not approved or challenge is None or challenge.expires_at <= timestamp:
                return False
            return (
                challenge.user_id == user_id
                and challenge.session_id == session_id
                and challenge.task_id == action.task_id
                and challenge.action_digest == canonical_action_digest(action)
            )

    def purge_expired(self, *, now: float | None = None) -> int:
        timestamp = time.time() if now is None else now
        with self._lock:
            expired = [key for key, value in self._pending.items() if value.expires_at <= timestamp]
            for key in expired:
                self._pending.pop(key, None)
                self._approved.discard(key)
            return len(expired)
