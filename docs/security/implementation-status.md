# Security implementation status

## Implemented in the security foundation

- Independent fail-closed policy engine; the agent/LLM cannot supply its own trusted capability grant.
- Exact target/tool/capability checks and grant expiry.
- High/critical risk classification and explicit approval requirement.
- Single-use approval challenge bound to user, session, task, exact action digest and expiry.
- Cooperative emergency stop that cancels registered asyncio tasks and rejects new work until reset.
- Recursive audit redaction for secret-like keys and bearer tokens.
- Loopback peer, strict Origin allowlist and constant-time bearer-token validation helper.
- Provenance wrapper for webpage, email, document, OCR, MCP and model output as untrusted content.
- Automated security-focused tests for the above invariants.

## Important limitations — not production-complete yet

- Approval challenges and the audit sink currently have in-memory implementations. They are not restart-safe or multi-process safe. Before production, replace them with transactional SQLite-backed persistence, atomic one-time consumption and append-only audit storage.
- The API guard is a reusable validation function, not yet wired into a running FastAPI server. The repository does not yet contain the desktop app or API server.
- Emergency stop is cooperative: adapters must check the stop state and register every worker; OS-level process/job-object termination still needs implementation.
- Untrusted-content tagging preserves provenance; it is not a prompt-injection detector and does not make a downstream model safe by itself.
- No Windows Credential Manager/DPAPI integration, Electron hardening, sandbox worker, signed updater, screen-capture consent UI or UI approval surface exists yet.
- No test execution is claimed until CI or a local environment runs the suite.

## Next implementation gates

1. Wire API authentication and Origin validation into FastAPI middleware and provision per-installation session secrets.
2. Add transactional persistent grants, approval nonces and append-only audit storage.
3. Add process-isolated workers with OS-level termination and capability-scoped filesystem/network adapters.
4. Add Electron secure defaults, narrow IPC schemas and user-visible approval/kill-switch controls.
5. Integrate Windows credential storage, screen/audio consent, retention and deletion controls.
6. Add Windows CI and adversarial security tests; publish test results and SBOM before release.
