from fastapi.testclient import TestClient

from backend.app.api.main import create_app


def client_for(app):
    return TestClient(app, client=("127.0.0.1", 51000))


def test_health_requires_valid_local_session(tmp_path):
    app = create_app(token="test-secret", allowed_origins=frozenset({"app://arya"}), database_path=tmp_path / "api.sqlite3")
    client = client_for(app)
    headers = {"Origin": "app://arya", "Authorization": "Bearer test-secret"}
    response = client.get("/health", headers=headers)
    assert response.status_code == 200
    assert response.json()["service"] == "arya-local-api"


def test_missing_or_invalid_authentication_is_rejected(tmp_path):
    app = create_app(token="test-secret", allowed_origins=frozenset({"app://arya"}), database_path=tmp_path / "api.sqlite3")
    client = client_for(app)
    assert client.get("/health", headers={"Origin": "app://arya"}).status_code == 403
    assert client.get(
        "/health", headers={"Origin": "app://arya", "Authorization": "Bearer wrong"}
    ).status_code == 403


def test_untrusted_origin_is_rejected(tmp_path):
    app = create_app(token="test-secret", allowed_origins=frozenset({"app://arya"}), database_path=tmp_path / "api.sqlite3")
    response = client_for(app).get(
        "/health",
        headers={"Origin": "https://attacker.example", "Authorization": "Bearer test-secret"},
    )
    assert response.status_code == 403


def test_api_fails_closed_without_configured_token(tmp_path):
    app = create_app(token="", allowed_origins=frozenset({"app://arya"}), database_path=tmp_path / "api.sqlite3")
    response = client_for(app).get(
        "/health", headers={"Origin": "app://arya", "Authorization": "Bearer anything"},
    )
    assert response.status_code == 403


def test_non_loopback_peer_is_rejected(tmp_path):
    app = create_app(token="test-secret", allowed_origins=frozenset({"app://arya"}), database_path=tmp_path / "api.sqlite3")
    response = TestClient(app, client=("192.0.2.10", 51000)).get(
        "/health",
        headers={"Origin": "app://arya", "Authorization": "Bearer test-secret"},
    )
    assert response.status_code == 403

def test_readiness_reports_initialized_security_components(tmp_path):
    app = create_app(
        token="test-secret", allowed_origins=frozenset({"app://arya"}),
        database_path=tmp_path / "ready.sqlite3",
    )
    response = client_for(app).get(
        "/v1/security/readiness",
        headers={"Origin": "app://arya", "Authorization": "Bearer test-secret"},
    )
    assert response.status_code == 200
    assert response.json()["approval_storage"] == "sqlite-transactional"
    assert response.json()["audit_storage"] == "sqlite-append-only"
    assert response.json()["authorization_service"] is True
