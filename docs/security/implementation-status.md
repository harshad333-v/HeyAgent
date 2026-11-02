# Security implementation status

## Implemented on main

- Independent fail-closed policy engine; the agent/LLM cannot supply its own trusted capability grant.
- Exact tool, capability and target checks. Empty targets must also be explicitly granted.
- Canonical action digests accept only finite JSON-compatible payloads.
- High/critical risk classification and explicit approval requirement.
- Single-use approval challenges bound to user, session, task, exact action digest and expiry.
- Cooperative emergency stop for registered asyncio tasks.
- Recursive audit redaction for secret-like keys and bearer tokens.
- Loopback peer, strict Origin allowlist and constant-time bearer-token validation.
- FastAPI middleware applies the local request guard to every route; unauthenticated, non-loopback and untrusted-Origin requests fail closed.
- SQLite-backed capability grants, approval challenges and append-only audit events. Approval consumption uses an IMMEDIATE transaction and is restart-safe across application instances.
- API startup initializes the persistent security store; API docs/OpenAPI endpoints are disabled in the local service.
- Provenance wrapper for webpage, email, document, OCR, MCP and model output as untrusted content.
- CI runs the full Python test suite, including API and persistence tests.

## Known limitations — not production-complete

- The local API currently exposes health and security-readiness endpoints only. No task execution, provider routing, chat streaming or tool registry is connected.
- The API token is currently provisioned through `ARYA_LOCAL_API_TOKEN`; production Windows builds must generate and store it using Windows Credential Manager/DPAPI and rotate it safely. Never place it in renderer code or logs.
- SQLite is transactional and audit rows are append-only at the application/database-trigger level, but database ACL hardening, encrypted backups, tamper-evident external audit export and retention controls remain to be implemented.
- Grant creation/revocation is currently a trusted backend API, not a user-facing permission-management workflow. Never let the LLM create grants.
- Emergency stop is cooperative: adapters must check the stop state and register every worker; OS-level process/job-object termination still needs implementation.
- Untrusted-content tagging preserves provenance; it is not a prompt-injection detector and does not make a downstream model safe by itself.
- No Windows Credential Manager/DPAPI integration, Electron hardening, sandbox worker, signed updater, screen-capture consent UI or UI approval surface exists yet.
- CI validation is required for every new main-branch change. A source commit is not proof that tests passed.

## Next implementation gates

1. Build the desktop shell with Electron context isolation, a narrow validated preload bridge and a visible connection/permission state.
2. Add session-token provisioning and rotation through Windows-protected credential storage.
3. Add typed versioned API/event contracts, authenticated streaming and request correlation.
4. Add process-isolated workers with OS-level termination and capability-scoped filesystem/network adapters.
5. Add user-facing capability grants, approval prompts, emergency stop and audit-history controls.
6. Add Windows CI and adversarial security tests; publish test results and SBOM before release.
