# Security Threat Model

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
| Local API abuse | Loopback bind, unpredictable per-session credential, Origin checks, rate and size limits |
| Prompt injection in webpages/documents/screenshots | Treat content as data, never as policy; tool calls independently authorized |
| Malicious MCP server/tool | Explicit trust, schema validation, per-tool grants, timeouts, output limits, audit |
| Credential leakage | Windows Credential Manager/DPAPI, redaction, no plaintext logs or renderer exposure |
| Runaway agent | Step/time/cost/concurrency limits, cancellation and emergency stop |
| Dangerous computer action | Risk classification, scoped capabilities, explicit confirmation, verification |
| Data exfiltration | Domain/app scopes, outbound controls where feasible, user confirmation for sharing |
| Malicious document | Safe parser configuration, size limits, isolated worker, no macro execution |
| Supply-chain compromise | Pinned dependencies, lockfiles, SBOM, signature verification, vulnerability scanning |
| Screen privacy breach | Event-driven capture, visible indicator, region/window scope, redaction, retention controls |
| Unsafe update | Signed artifacts, verified update metadata, staged rollout and rollback |

## Mandatory rules

- Never expose arbitrary shell execution as an LLM tool.
- Never accept instructions embedded in untrusted content as higher-priority policy.
- Never grant a tool permissions based solely on model output.
- Require explicit approval for external send/share/publish and high-impact actions.
- Provide a global stop control and user takeover.
- Audit who/what requested an action, policy result, approval and execution outcome without storing secrets.
- Do not log raw screenshots/audio by default.
- Provide user-visible retention, export and deletion controls.

## Security test cases

Include prompt injection, forged IPC messages, API origin/auth failure, malicious MCP output, path traversal, symlink handling, oversized documents, credential redaction, cancellation races, approval replay and unauthorized external actions.
