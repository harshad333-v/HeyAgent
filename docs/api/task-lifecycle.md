# Task Lifecycle API

**Status:** implemented persistence/API foundation; task execution is not implemented.

All routes are protected by the existing local-session middleware. Requests must originate from an allowed Origin, arrive over loopback, and include the configured bearer token.

## Create a task

`POST /v1/tasks`

Headers:
- `Origin: app://arya`
- `Authorization: Bearer <local-token>`
- Optional `Idempotency-Key: <8-128 characters>`

JSON body:

```json
{
  "title": "Research competitor products",
  "instruction": "Compare the public feature sets and cite sources."
}
```

Returns `201 Created` for a new task and `200 OK` when an identical request is replayed with the same idempotency key. Reusing a key with a different normalized payload returns `409 Conflict`.

## List tasks

`GET /v1/tasks?limit=50&before=<created_at>`

- `limit` is constrained to 1-100.
- `before` is an optional timestamp cursor.
- Returns newest task records first.

## Read a task

`GET /v1/tasks/{task_id}`

Returns `404` when the task does not exist.

## Cancel a queued task

`POST /v1/tasks/{task_id}/cancel`

Only queued tasks can be cancelled by this endpoint. Repeating cancellation of an already-cancelled task is idempotent. Other states return `409 Conflict`. Running-task cancellation must be implemented with the future worker supervisor and cooperative/OS-level cancellation; this endpoint does not claim to stop a process.

## Persistence and current limitations

- Task records live in a separate SQLite database adjacent to the configured security database.
- Creation supports an optional idempotency key bound to a SHA-256 fingerprint of title and instruction.
- SQLite transactions protect state updates; task listing is bounded.
- Current task status is initially `queued`; the agent worker, plan/run/step model, event stream, provider calls, approvals and execution adapters are not implemented.
- Do not treat task creation as task execution or tell a user work has started merely because a record was created.
- Authentication currently uses the development `ARYA_LOCAL_API_TOKEN`; production token provisioning must move to Windows Credential Manager/DPAPI.
