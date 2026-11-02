from fastapi.testclient import TestClient

from backend.app.api.main import create_app
from backend.app.tasks import IdempotencyConflict, TaskStore


def _client(tmp_path):
    app = create_app(
        token="task-test-token",
        allowed_origins=frozenset({"app://arya"}),
        database_path=tmp_path / "arya.sqlite3",
    )
    client = TestClient(app, client=("127.0.0.1", 51001))
    headers = {
        "Origin": "app://arya",
        "Authorization": "Bearer task-test-token",
    }
    return client, headers


def test_task_store_persists_and_reuses_idempotency_key(tmp_path):
    path = tmp_path / "tasks.sqlite3"
    first_store = TaskStore(path)
    task, created = first_store.create(
        title="Research topic",
        instruction="Compare three sources",
        idempotency_key="research-run-001",
    )
    second_store = TaskStore(path)
    repeated, repeated_created = second_store.create(
        title="Research topic",
        instruction="Compare three sources",
        idempotency_key="research-run-001",
    )

    assert created is True
    assert repeated_created is False
    assert repeated["id"] == task["id"]
    assert second_store.get(task["id"])["status"] == "queued"


def test_idempotency_key_cannot_be_reused_for_different_payload(tmp_path):
    store = TaskStore(tmp_path / "tasks.sqlite3")
    store.create(
        title="Original",
        instruction="Original instruction",
        idempotency_key="same-request-key",
    )

    try:
        store.create(
            title="Changed",
            instruction="Different instruction",
            idempotency_key="same-request-key",
        )
    except IdempotencyConflict:
        pass
    else:
        raise AssertionError("Expected IdempotencyConflict")


def test_queued_task_can_be_cancelled_and_cancellation_is_idempotent(tmp_path):
    store = TaskStore(tmp_path / "tasks.sqlite3")
    task, _ = store.create(title="Task", instruction="Do work")

    cancelled = store.cancel(task["id"])
    repeated = store.cancel(task["id"])

    assert cancelled["status"] == "cancelled"
    assert repeated["status"] == "cancelled"


def test_create_task_endpoint_requires_local_authentication(tmp_path):
    client, _ = _client(tmp_path)
    response = client.post(
        "/v1/tasks",
        json={"title": "Research", "instruction": "Summarize sources"},
    )
    assert response.status_code == 403


def test_task_api_create_list_get_and_cancel(tmp_path):
    client, headers = _client(tmp_path)
    created = client.post(
        "/v1/tasks",
        headers={**headers, "Idempotency-Key": "api-task-key-001"},
        json={"title": "Research", "instruction": "Summarize three sources"},
    )
    assert created.status_code == 201
    task_id = created.json()["id"]
    assert created.json()["status"] == "queued"

    repeated = client.post(
        "/v1/tasks",
        headers={**headers, "Idempotency-Key": "api-task-key-001"},
        json={"title": "Research", "instruction": "Summarize three sources"},
    )
    assert repeated.status_code == 200
    assert repeated.json()["id"] == task_id

    listed = client.get("/v1/tasks", headers=headers)
    assert listed.status_code == 200
    assert any(item["id"] == task_id for item in listed.json()["tasks"])

    fetched = client.get(f"/v1/tasks/{task_id}", headers=headers)
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Research"

    cancelled = client.post(f"/v1/tasks/{task_id}/cancel", headers=headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["status"] == "cancelled"


def test_task_api_rejects_idempotency_key_payload_mismatch(tmp_path):
    client, headers = _client(tmp_path)
    key_headers = {**headers, "Idempotency-Key": "api-task-key-002"}
    first = client.post(
        "/v1/tasks", headers=key_headers,
        json={"title": "First", "instruction": "Do first"},
    )
    second = client.post(
        "/v1/tasks", headers=key_headers,
        json={"title": "Second", "instruction": "Do second"},
    )
    assert first.status_code == 201
    assert second.status_code == 409


def test_task_api_rejects_blank_and_oversized_fields(tmp_path):
    client, headers = _client(tmp_path)
    blank = client.post(
        "/v1/tasks", headers=headers,
        json={"title": "   ", "instruction": "   "},
    )
    oversized = client.post(
        "/v1/tasks", headers=headers,
        json={"title": "x" * 161, "instruction": "instruction"},
    )
    assert blank.status_code == 422
    assert oversized.status_code == 422


def test_task_api_returns_404_for_unknown_task(tmp_path):
    client, headers = _client(tmp_path)
    response = client.get(
        "/v1/tasks/00000000-0000-0000-0000-000000000000",
        headers=headers,
    )
    assert response.status_code == 404
