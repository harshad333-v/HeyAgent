import pytest
import time

from backend.app.security.models import ActionRequest, CapabilityGrant, DecisionKind
from backend.app.security.service import AuthorizationService
from backend.app.security.sqlite_store import SQLiteSecurityStore


def make_grant():
    return CapabilityGrant(
        user_id="u1", session_id="s1",
        capabilities=frozenset({"messaging.send"}),
        allowed_tools=frozenset({"send_message"}),
        allowed_targets=frozenset({"contact:123"}),
        expires_at=time.time() + 3600,
    )


def make_action(text="hello"):
    return ActionRequest(
        task_id="task-1", tool="send_message", capability="messaging.send",
        target="contact:123", payload={"text": text}, external_side_effect=True,
    )


def test_service_requires_and_consumes_exact_approval(tmp_path):
    store = SQLiteSecurityStore(tmp_path / "arya.sqlite3")
    grant_id = store.save_grant(make_grant())
    service = AuthorizationService(store)
    challenge = service.request_approval(
        make_action(), grant_id=grant_id, user_id="u1", session_id="s1",
    )
    assert service.approve(challenge.challenge_id, user_id="u1", session_id="s1")
    decision = service.authorize(
        make_action(), grant_id=grant_id, user_id="u1", session_id="s1",
        approval_challenge_id=challenge.challenge_id,
    )
    assert decision.kind is DecisionKind.ALLOW
    replay = service.authorize(
        make_action(), grant_id=grant_id, user_id="u1", session_id="s1",
        approval_challenge_id=challenge.challenge_id,
    )
    assert replay.kind is DecisionKind.REQUIRE_APPROVAL


def test_service_rejects_changed_payload_and_wrong_principal(tmp_path):
    store = SQLiteSecurityStore(tmp_path / "arya.sqlite3")
    grant_id = store.save_grant(make_grant(), now=100)
    service = AuthorizationService(store)
    challenge = service.request_approval(
        make_action(), grant_id=grant_id, user_id="u1", session_id="s1",
    )
    assert service.approve(challenge.challenge_id, user_id="u1", session_id="s1")
    changed = service.authorize(
        make_action("different"), grant_id=grant_id, user_id="u1", session_id="s1",
        approval_challenge_id=challenge.challenge_id,
    )
    assert changed.kind is DecisionKind.REQUIRE_APPROVAL
    wrong_user = service.authorize(
        make_action(), grant_id=grant_id, user_id="attacker", session_id="s1",
    )
    assert wrong_user.kind is DecisionKind.DENY


def test_service_does_not_issue_approval_for_denied_target(tmp_path):
    store = SQLiteSecurityStore(tmp_path / "arya.sqlite3")
    grant_id = store.save_grant(make_grant(), now=100)
    service = AuthorizationService(store)
    bad = ActionRequest(
        task_id="task-1", tool="send_message", capability="messaging.send",
        target="contact:attacker", payload={"text": "hello"}, external_side_effect=True,
    )
    with pytest.raises(PermissionError):
        service.request_approval(
            bad, grant_id=grant_id, user_id="u1", session_id="s1",
        )
