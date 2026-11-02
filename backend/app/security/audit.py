"""Structured audit events with recursive secret redaction."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Protocol

_SECRET_KEYS = re.compile(r"(password|passwd|secret|token|api[_-]?key|authorization|cookie|credential)", re.I)
_BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+")


def redact(value: Any, *, key: str = "") -> Any:
    if _SECRET_KEYS.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(k): redact(v, key=str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(item) for item in value]
    if isinstance(value, str):
        return _BEARER.sub("Bearer [REDACTED]", value)[:4000]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)[:4000]


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_type: str
    task_id: str
    actor: str
    outcome: str
    details: dict[str, Any]
    timestamp: str

    @classmethod
    def build(cls, event_type: str, task_id: str, actor: str, outcome: str, details: dict[str, Any]) -> "AuditEvent":
        return cls(event_type, task_id, actor, outcome, redact(details), datetime.now(timezone.utc).isoformat())


class AuditSink(Protocol):
    def write(self, event: AuditEvent) -> None: ...


class AuditLogger:
    def __init__(self, sink: AuditSink) -> None:
        self._sink = sink

    def record(self, event_type: str, *, task_id: str, actor: str, outcome: str, details: dict[str, Any]) -> None:
        self._sink.write(AuditEvent.build(event_type, task_id, actor, outcome, details))


class InMemoryAuditSink:
    """Test adapter only. Production must use an append-only, access-controlled store."""
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    def write(self, event: AuditEvent) -> None:
        self.events.append(event)
