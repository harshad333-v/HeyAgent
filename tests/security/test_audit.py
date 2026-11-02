from backend.app.security.audit import AuditEvent, redact


def test_recursive_secret_redaction_and_bearer_redaction():
    safe = redact({"api_key": "abc", "nested": {"password": "pw"}, "message": "Authorization: Bearer abc.def"})
    assert safe["api_key"] == "[REDACTED]"
    assert safe["nested"]["password"] == "[REDACTED]"
    assert "abc.def" not in safe["message"]


def test_audit_event_redacts_details():
    event = AuditEvent.build("tool", "t1", "agent", "denied", {"token": "secret"})
    assert event.details["token"] == "[REDACTED]"
