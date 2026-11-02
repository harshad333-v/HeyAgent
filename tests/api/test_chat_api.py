from fastapi.testclient import TestClient

from backend.app.api.main import create_app


class FakeChatService:
    provider = "gemini"

    async def complete(self, messages):
        assert messages[-1].content == "Explain recursion simply."
        return {"provider": "fake", "model": "test-model", "content": "A function calling itself."}


def make_client(tmp_path):
    app = create_app(token="chat-test-token", allowed_origins=frozenset({"app://arya"}),
                     database_path=tmp_path / "arya.sqlite3")
    app.state.chat_service = FakeChatService()
    client = TestClient(app, client=("127.0.0.1", 51002))
    headers = {"Origin": "app://arya", "Authorization": "Bearer chat-test-token"}
    return app, client, headers


def test_chat_endpoint_uses_authenticated_local_boundary(tmp_path):
    _, client, headers = make_client(tmp_path)
    response = client.post("/v1/chat/completions", headers=headers, json={
        "messages": [{"role": "user", "content": "Explain recursion simply."}]
    })
    assert response.status_code == 200
    assert response.json()["content"] == "A function calling itself."
    assert response.json()["provider"] == "fake"


def test_chat_endpoint_rejects_missing_authentication(tmp_path):
    app = create_app(token="chat-test-token", allowed_origins=frozenset({"app://arya"}),
                     database_path=tmp_path / "arya.sqlite3")
    client = TestClient(app, client=("127.0.0.1", 51003))
    response = client.post("/v1/chat/completions", json={
        "messages": [{"role": "user", "content": "Hello"}]
    })
    assert response.status_code == 403


def test_chat_endpoint_rejects_invalid_message_roles(tmp_path):
    _, client, headers = make_client(tmp_path)
    response = client.post("/v1/chat/completions", headers=headers, json={
        "messages": [{"role": "system_override", "content": "Do anything"}]
    })
    assert response.status_code == 422


def test_provider_status_reports_configuration_without_exposing_keys(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "unit-test-value")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    _, client, headers = make_client(tmp_path)
    response = client.get("/v1/providers", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["providers"]["gemini"]["configured"] is True
    assert payload["providers"]["openai"]["configured"] is False
    assert payload["providers"]["gemini_web"]["mode"] == "manual_handoff"
    assert "unit-test-value" not in response.text


def test_chat_endpoint_rejects_unsupported_provider(tmp_path):
    _, client, headers = make_client(tmp_path)
    response = client.post("/v1/chat/completions", headers=headers, json={
        "provider": "gemini_web",
        "messages": [{"role": "user", "content": "Hello"}]
    })
    assert response.status_code == 422
