# Security Threat Model

## Security objectives

Arya must operate with least privilege, make consequential actions reviewable, and remain controllable by the user. Model output is untrusted proposal data. Authorization is performed by independent application code and trusted user-configured grants.

## Assets

Provider credentials, connector tokens, user files, screen contents, microphone audio, personal memory, browser sessions, local API sessions, task history and OS control capabilities.

## Trust boundaries

1. Electron renderer <-> main process.
2. Desktop application <-> loopback Python backend.
3. Agent planner <-> policy engine.
4. Policy engine <-> execution workers.
5. Application <-> cloud AI providers.
6. Application <-> websites, documents and MCP servers.
7. Application <-> local user filesystem and OS.

## Primary threats and controls

| Threat | Required controls |
|---|---|
| Renderer compromise | Context isolation, sandbox, no Node integration, narrow preload API, CSP |
| Local API abuse | Loopback bind, unpredictable per-session credential, strict Origin checks, rate and size limits |
| Prompt injection in webpages/documents/screenshots | Preserve untrusted provenance; content is never policy; independently authorize every tool call |
| Malicious MCP server/tool | Explicit trust, schema validation, per-tool grants, timeouts, output limits, audit |
| Credential leakage | Windows Credential Manager/DPAPI, redaction, no plaintext logs or renderer exposure |
| Runaway agent | Step/time/cost/concurrency limits, cancellation and emergency stop |
| Dangerous computer action | Risk classification, scoped capabilities, exact-action confirmation, post-action verification |
| Data exfiltration | Domain/app scopes, outbound controls where feasible, user confirmation for sharing |
| Malicious document | Safe parser configuration, size limits, isolated worker, no macro execution |
| Supply-chain compromise | Pinned dependencies, lockfiles, SBOM, signature verification, vulnerability scanning |
| Screen privacy breach | Event-driven capture, visible indicator, window/region scope, redaction, retention controls |
| Unsafe update | Signed artifacts, verified update metadata, staged rollout and rollback |
| Approval replay/tampering | Short-lived challenge bound to user/session/task/action digest; atomic one-time consumption |
| Unauthorized local API caller | Loopback peer validation, strict Origin allowlist and constant-time session-token comparison |

## Implemented security foundation

The feature/security-safety-foundation branch currently adds:

- Independent fail-closed policy evaluation using trusted capability grants.
- Denial of generic shell, terminal, PowerShell, command and arbitrary-code tools.
- Exact tool/target/capability checks and grant expiration.
- Risk classification and approval requirement for high/critical actions.
- One-time, expiring approval challenge primitives bound to the exact action digest.
- Cooperative cancellation registry for emergency stop.
- Audit event redaction and local API request validation helpers.
- Untrusted-content provenance types for external sources.

See [implementation status](implementation-status.md) for limitations and remaining work. These primitives are not yet integrated into an application runtime.

## Mandatory rules

- Never expose arbitrary shell execution as an LLM tool.
- Never accept instructions embedded in untrusted content as higher-priority policy.
- Never grant a tool permissions based solely on model output.
- Require fresh, exact-action approval for external send/share/publish/upload and high-impact operations; block prohibited operations.
- Provide a global stop control and user takeover.
- Audit who/what requested an action, policy result, approval and execution outcome without storing secrets.
- Do not log raw screenshots/audio by default.
- Provide user-visible retention, export and deletion controls.
- Approval must be bound to actor, session, task, tool, target, payload digest, risk and expiry; changed payload invalidates approval.
- Every adapter must check cancellation before and during long-running work and verify outcomes from observed state.

## Security test cases

Include prompt injection, forged IPC messages, API origin/auth failure, malicious MCP output, path traversal, symlink handling, oversized documents, credential redaction, cancellation races, approval replay, approval payload mutation and unauthorized external actions.
