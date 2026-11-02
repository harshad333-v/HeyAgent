from backend.app.security.approvals import ApprovalManager
from backend.app.security.models import ActionRequest


def test_approval_is_bound_to_exact_action_and_single_use():
    manager = ApprovalManager(ttl_seconds=60)
    action = ActionRequest("t1", "send_email", "email.send", "a@example.com", {"body": "hello"}, True)
    challenge = manager.create(action, user_id="u1", session_id="s1", now=100)
    assert manager.approve(challenge.challenge_id, user_id="u1", session_id="s1", now=110)
    changed = ActionRequest("t1", "send_email", "email.send", "b@example.com", {"body": "hello"}, True)
    assert not manager.consume(challenge.challenge_id, changed, user_id="u1", session_id="s1", now=111)


def test_approval_cannot_be_replayed():
    manager = ApprovalManager()
    action = ActionRequest("t1", "send_email", "email.send", "a@example.com", {"body": "hello"}, True)
    challenge = manager.create(action, user_id="u1", session_id="s1", now=100)
    assert manager.approve(challenge.challenge_id, user_id="u1", session_id="s1", now=101)
    assert manager.consume(challenge.challenge_id, action, user_id="u1", session_id="s1", now=102)
    assert not manager.consume(challenge.challenge_id, action, user_id="u1", session_id="s1", now=103)


def test_wrong_session_and_expiry_rejected():
    manager = ApprovalManager(ttl_seconds=10)
    action = ActionRequest("t1", "send_email", "email.send", "a@example.com", {}, True)
    challenge = manager.create(action, user_id="u1", session_id="s1", now=100)
    assert not manager.approve(challenge.challenge_id, user_id="u1", session_id="other", now=101)
    assert not manager.approve(challenge.challenge_id, user_id="u1", session_id="s1", now=111)
