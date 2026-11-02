# Arya local API — development operations

## Purpose and current scope

The local FastAPI process is the authenticated boundary between the Electron desktop shell and the Python backend. At this milestone it exposes:

- `GET /health` — process health.
- `GET /v1/security/readiness` — reports configured boundary and storage properties.
- `POST /v1/chat/completions` — bounded chat history routed to the explicitly configured Gemini or OpenAI provider.
- `POST/GET /v1/tasks`, `GET /v1/tasks/{id}`, `POST /v1/tasks/{id}/cancel` — durable task lifecycle only; no task execution.

Chat is a non-streaming development vertical slice. Provider selection is explicit (`ARYA_DEFAULT_PROVIDER=gemini|openai`); the service does not silently fall back to another provider. Configure `GEMINI_API_KEY` or `OPENAI_API_KEY` in the backend process environment. The API does not execute tools or computer automation.

## Development setup

Use Python 3.11 or newer:

```powershell
python -m pip install -e ".[test]"
$env:ARYA_LOCAL_API_TOKEN = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:ARYA_ALLOWED_ORIGINS = "app://arya"
$env:ARYA_DATABASE_PATH = "$env:LOCALAPPDATA\Arya\data\arya.sqlite3"
uvicorn backend.app.api.main:app --host 127.0.0.1 --port 8765
```

The token is intentionally supplied out-of-band. Do not commit it, place it in frontend source, put it in command-line arguments, or log it. The environment-variable approach is for development only; the Windows desktop installer must provision and retrieve the token using Windows Credential Manager/DPAPI.

## Request contract

Every request must:

1. originate from a loopback peer address;
2. include an exact allowlisted `Origin` (default: `app://arya`);
3. include `Authorization: Bearer <ARYA_LOCAL_API_TOKEN>`.

Example:

```powershell
$headers = @{
  Origin = "app://arya"
  Authorization = "Bearer $env:ARYA_LOCAL_API_TOKEN"
}
Invoke-RestMethod http://127.0.0.1:8765/health -Headers $headers
Invoke-RestMethod http://127.0.0.1:8765/v1/security/readiness -Headers $headers
$body = @{ messages = @(@{ role = "user"; content = "Explain recursion simply." }) } | ConvertTo-Json -Depth 5
Invoke-RestMethod http://127.0.0.1:8765/v1/chat/completions -Method Post -Headers $headers -ContentType "application/json" -Body $body
```

The middleware rejects invalid authentication, origin and peer address with a generic response. It rejects declared request bodies larger than 1 MiB. The service disables interactive API documentation and OpenAPI endpoints.

**Never bind this development service to `0.0.0.0`, a LAN address or a public interface.** Do not add permissive CORS as a workaround.

## Persistence

The SQLite database contains trusted capability grants, one-time approval challenges and append-only audit events. Mutations use explicit IMMEDIATE transactions. A matching approval challenge is consumed once, including when the action payload no longer matches. A challenge belonging to a different user/session cannot be consumed or invalidated by that principal.

The database is not a secret vault. Do not store API keys, bearer tokens, raw screenshots, audio or document contents in these tables. Production must add Windows ACL verification, backup/restore, retention controls and protected token storage.

## Validation

Run the complete suite:

```powershell
python -m pytest -q tests
```

The CI workflow runs this command on pushes to `main` and feature branches. A green CI run is required before claiming a change is validated.
