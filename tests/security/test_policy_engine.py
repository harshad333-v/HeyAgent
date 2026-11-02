import pytest

from backend.app.security.models import ActionRequest, CapabilityGrant, DecisionKind, RiskLevel
from backend.app.security.policy_engine import ActionPolicy, canonical_action_digest


def grant(**overrides):
    values = dict(user_id="u1", session_id="s1", capabilities=frozenset({"files.read", "browser.navigate", "email.send"}), allowed_tools=frozenset({"read_document", "browser_navigate", "send_email"}), allowed_targets=frozenset({"", "person@example.com"}), expires_at=5000)
    values.update(overrides)
    return CapabilityGrant(**values)


def evaluate(action, capability_grant, **kwargs):
    return ActionPolicy().evaluate(action, capability_grant, actor_user_id="u1", session_id="s1", now=1000, **kwargs)


def test_read_only_action_allowed_with_grant():
    action = ActionRequest("t1", "read_document", "files.read")
    decision = evaluate(action, grant())
    assert decision.kind is DecisionKind.ALLOW
    assert decision.risk is RiskLevel.LOW


def test_external_side_effect_requires_approval():
    action = ActionRequest("t1", "send_email", "email.send", target="person@example.com", external_side_effect=True)
    decision = evaluate(action, grant())
    assert decision.kind is DecisionKind.REQUIRE_APPROVAL
    assert evaluate(action, grant(), approval_valid=True).allowed


def test_missing_grant_fails_closed():
    action = ActionRequest("t1", "read_document", "files.read")
    assert ActionPolicy().evaluate(action, None, now=1000).kind is DecisionKind.DENY


def test_expired_grant_denied():
    action = ActionRequest("t1", "read_document", "files.read")
    assert evaluate(action, grant(expires_at=10)).kind is DecisionKind.DENY


def test_arbitrary_shell_is_always_denied():
    action = ActionRequest("t1", "powershell", "system.execute")
    assert evaluate(action, grant(), approval_valid=True).kind is DecisionKind.DENY


def test_target_allowlist_is_exact():
    action = ActionRequest("t1", "send_email", "email.send", target="attacker@example.com", external_side_effect=True)
    assert evaluate(action, grant(), approval_valid=True).kind is DecisionKind.DENY


def test_empty_tool_allowlist_is_not_a_wildcard():
    action = ActionRequest("t1", "read_document", "files.read")
    assert evaluate(action, grant(allowed_tools=frozenset())).kind is DecisionKind.DENY


def test_grant_must_match_authenticated_principal():
    action = ActionRequest("t1", "read_document", "files.read")
    decision = ActionPolicy().evaluate(action, grant(), actor_user_id="other", session_id="s1", now=1000)
    assert decision.kind is DecisionKind.DENY


def test_digest_changes_when_payload_changes():
    a = ActionRequest("t1", "send_email", "email.send", "person@example.com", {"body": "hello"}, True)
    b = ActionRequest("t1", "send_email", "email.send", "person@example.com", {"body": "changed"}, True)
    assert canonical_action_digest(a) != canonical_action_digest(b)

def test_empty_target_must_be_explicitly_granted():
    action = ActionRequest("t1", "read_document", "files.read")
    assert evaluate(action, grant(allowed_targets=frozenset())).kind is DecisionKind.DENY


def test_digest_rejects_non_json_payload_values():
    action = ActionRequest("t1", "read_document", "files.read", payload={"bad": object()})
    with pytest.raises(ValueError, match="JSON-compatible"):
        canonical_action_digest(action)


def test_digest_rejects_non_finite_numbers():
    action = ActionRequest("t1", "read_document", "files.read", payload={"bad": float("nan")})
    with pytest.raises(ValueError, match="JSON-compatible"):
        canonical_action_digest(action)
