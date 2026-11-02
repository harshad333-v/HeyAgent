import pytest

from backend.app.security.audit import AuditEvent, AuditLogger
from backend.app.security.models import ActionRequest
from backend.app.security.sqlite_store import SQLiteSecurityStore


def action():
    return ActionRequest(
        task_id="task-1", tool="send_message", capability="messaging",
        target="contact:42", payload={"text": "hello"}, external_side_effect=True,
    )


def test_approval_survives_store_recreation_and_is_single_use(tmp_path):
    db = tmp_path / "arya.sqlite3"
    store = SQLiteSecurityStore(db)
    challenge = store.create_challenge(
        action(), user_id="user-1", session_id="session-1", ttl_seconds=90, now=100,
    )
    # A fresh store instance represents an application restart/new worker.
    restarted = SQLiteSecurityStore(db)
    assert restarted.approve_challenge(
        challenge.challenge_id, user_id="user-1", session_id="session-1", now=101,
    )
    assert restarted.consume_approval(
        challenge.challenge_id, action(), user_id="user-1", session_id="session-1", now=102,
    )
    assert not restarted.consume_approval(
        challenge.challenge_id, action(), user_id="user-1", session_id="session-1", now=102,
    )


def test_approval_is_bound_to_actor_session_and_exact_action(tmp_path):
    store = SQLiteSecurityStore(tmp_path / "arya.sqlite3")
    original = action()
    challenge = store.create_challenge(original, user_id="u", session_id="s", now=1)
    assert not store.approve_challenge(challenge.challenge_id, user_id="other", session_id="s", now=2)
    assert store.approve_challenge(challenge.challenge_id, user_id="u", session_id="s", now=2)
    changed = ActionRequest(
        task_id="task-1", tool="send_message", capability="messaging",
        target="contact:43", payload={"text": "hello"}, external_side_effect=True,
    )
    assert not store.consume_approval(
        challenge.challenge_id, changed, user_id="u", session_id="s", now=3,
    )


def test_expired_approval_cannot_be_approved_or_consumed(tmp_path):
    store = SQLiteSecurityStore(tmp_path / "arya.sqlite3")
    challenge = store.create_challenge(
        action(), user_id="u", session_id="s", ttl_seconds=2, now=10,
    )
    assert not store.approve_challenge(challenge.challenge_id, user_id="u", session_id="s", now=12)
    assert not store.consume_approval(
        challenge.challenge_id, action(), user_id="u", session_id="s", now=12,
    )


def test_audit_events_persist_redacted_and_are_append_only(tmp_path):
    store = SQLiteSecurityStore(tmp_path / "arya.sqlite3")
    logger = AuditLogger(store)
    logger.record(
        "action.denied", task_id="t-1", actor="local-user", outcome="deny",
        details={"api_key": "do-not-store", "message": "Authorization: Bearer abc123"},
    )
    restarted = SQLiteSecurityStore(tmp_path / "arya.sqlite3")
    events = restarted.list_audit_events()
    assert len(events) == 1
    assert events[0]["details"]["api_key"] == "[REDACTED]"
    assert "abc123" not in str(events[0]["details"])
    with sqlite3_connection(tmp_path / "arya.sqlite3") as connection:
        with pytest.raises(Exception, match="append-only"):
            connection.execute("UPDATE audit_events SET outcome='changed' WHERE id=1")


from contextlib import contextmanager
import sqlite3


@contextmanager
def sqlite3_connection(path):
    connection = sqlite3.connect(path)
    try:
        yield connection
    finally:
        connection.close()
