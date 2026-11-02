# Architecture Overview

**Accepted architecture:** Windows-first, hybrid cloud/local AI, approval-gated computer use, push-to-talk plus opt-in hands-free voice, and bounded multi-agent orchestration.

The binding decisions and rationale are recorded in [ADR-0001](../decisions/0001-core-architecture.md). This document describes the implementation architecture; it does not imply every component is already implemented.

## 1. Architecture style and platform

Use a Windows 11 x64-first desktop modular monolith with separately supervised workers for risky or resource-intensive execution. Do not introduce network microservices without a demonstrated operational need.

- Desktop: Electron main + React/TypeScript renderer.
- Local service: Python + FastAPI, bound to loopback only.
- Orchestration: LangGraph behind an application-owned orchestrator interface.
- Browser automation: Playwright, preferably DOM/accessibility semantics.
- Native automation: Windows UI Automation behind typed adapters.
- Storage: SQLite with migrations, local artifact directory, optional FTS/vector indexes.
- Secrets: Windows Credential Manager/DPAPI; never plaintext SQLite or renderer storage.

Keep OS-specific functionality behind adapters. Windows 11 x64 is the initial release target; macOS/Linux are not part of the initial release commitment.

## 2. System topology

1. **Electron main:** lifecycle, single-instance lock, windows, tray, global shortcuts, update lifecycle and worker supervision.
2. **React renderer:** orb, chat, agent/task dashboard, voice controls, screen context, approval UI and settings.
3. **Secure preload:** narrow, typed, schema-validated IPC; context isolation, renderer sandbox, no Node integration and strict CSP.
4. **Local FastAPI service:** authenticated loopback API, versioned contracts, request limits and SSE event stream.
5. **Application core:** sessions, task state machine, provider router, multi-agent orchestrator, event bus and policy engine.
6. **Intelligence layer:** provider adapters, specialist agents, perception, voice, memory and retrieval.
7. **Execution adapters:** Playwright, Windows UI Automation and confidence-gated visual fallback.
8. **Supervised workers:** least privilege, bounded capabilities, timeouts, budgets, cancellation and process-level termination.
9. **Persistence:** SQLite metadata/security/task state, migrations, local artifacts and optional indexes.
10. **External boundary:** model outputs, AI providers, MCP servers, websites and imported documents are untrusted.

## 3. Hybrid AI execution and provider routing

Define provider-neutral contracts for:
- Text generation and streaming.
- Structured output/tool planning.
- Vision and multimodal understanding.
- Embeddings and reranking.
- Speech recognition (STT), speech synthesis (TTS) and realtime audio.

Implement cloud and optional local adapters behind the same contracts. The capability-aware router evaluates task capability, quality, privacy classification, latency, connectivity, cost, hardware availability and user preference.

Initial policy:
- Cloud is the default for tasks requiring strong reasoning or multimodal quality, subject to user configuration and privacy policy.
- Local models are optional for supported private, offline or cost-sensitive tasks.
- Never silently send content to a cloud provider when its privacy classification or user setting forbids it.
- Explain provider selection and fallback; record usage/cost without logging secrets or sensitive prompt content.
- Local model availability, memory pressure and acceleration failure must produce a clear fallback or error, not a hang.

Do not hard-code a specific model/vendor into business logic. Gemini and OpenAI are candidate cloud adapters; local runtime choice remains an implementation/configuration decision.

## 4. Voice architecture: both interaction modes

- Push-to-talk is the default and first implementation target.
- Hands-free listening is optional, disabled until the user opts in, and uses a visible microphone/listening indicator.
- Wake phrase is configurable and opt-in; provide immediate mute/stop and microphone device selection.
- Use streaming STT/TTS, partial transcripts, captions, interruption/barge-in and dictation.
- Support language auto-detection and text fallback when audio hardware, permissions, providers or network fail.
- Raw audio is not retained by default; persistence requires a clear feature need and user-facing retention/deletion controls.

## 5. Multi-agent orchestration

Use one supervisory orchestrator and a bounded set of specialist agents, not an unrestricted swarm.

- Orchestrator: intent routing, decomposition, delegation, checkpoints, conflict resolution and final synthesis.
- Specialists: research, coding, documents, data analysis and browser/computer-use roles as needed.
- Each agent has typed tool/capability allowlists, scoped context/memory, output schema, timeout and resource budget.
- Specialists cannot grant permissions, change policy or expand their own capabilities.
- Bound concurrency, delegation depth, wall-clock time, tokens, cost and tool calls.
- Persist task/run/step state; support pause, resume, retry, cancel and recovery.
- Prefer a single agent or deterministic workflow when delegation does not improve results.

All tool execution goes through the same policy engine and worker boundary. Model output is never authorization.

## 6. Approval-gated computer use

Default posture: **propose, explain, obtain approval, execute, verify**.

1. Observe only within user-authorized capture scope.
2. Prepare a typed action with exact application/site, target and payload.
3. Classify risk and validate explicit capability grants.
4. Show the user the target and material side effect.
5. Require approval before any action that changes application/external state.
6. Bind approval to user, session, task, tool, target and canonical payload; edits invalidate approval.
7. Execute through least-privilege Playwright or Windows UI Automation adapters.
8. Re-observe and verify the result; report uncertainty or failure honestly.

Provide Allow once, Deny and Cancel/Stop controls. Any future remembered grant must be a deliberate opt-in, narrow, revocable and auditable. Escape, user takeover and emergency stop interrupt execution. Never expose arbitrary shell/terminal execution to the model.

Use Playwright DOM/accessibility semantics first for supported browser workflows. Use Windows UI Automation for native controls. Screenshot/coordinate automation is a fallback only, requiring fresh observations, DPI-aware transforms, confidence thresholds and post-action verification.

## 7. Communication and contracts

- Renderer to main: typed IPC through the preload bridge.
- Desktop to backend: authenticated loopback HTTP; SSE for task and agent events; WebSocket/WebRTC only where realtime audio requires it.
- Backend modules: typed Python interfaces and domain events.
- Workers: versioned job contracts, correlation IDs, capability grants and explicit cancellation.
- MCP: approved transports, trusted server registry and per-tool policy checks.

## 8. Reliability and state

Persist task state and checkpoints. Make task/tool operations idempotent where possible. Use bounded retries with backoff only for retryable failures. Propagate cancellation to provider requests, workers and browser sessions. Never report success based solely on an LLM assertion; verify external state.

## 9. Security and privacy boundaries

- Loopback-only API; authenticated sessions, strict Origin allowlist, request limits and rate limits.
- DPAPI/Credential Manager for secrets; rotate installation/session credentials.
- Electron context isolation, sandbox, strict CSP and minimal IPC.
- Workers run with least privilege and explicit capability grants.
- No arbitrary shell tool, unbounded agent loops or unconstrained parallelism.
- No hidden continuous screen/audio capture; visible indicators and user-controlled scope.
- Redact secrets and sensitive screen/audio data from logs.
- Imported content and model outputs are untrusted; defend against prompt injection through policy and provenance boundaries.
- Signed updates, dependency/license review, SBOM and supply-chain controls before release.

## 10. Implementation status

The repository currently has the security foundation and an authenticated durable task-lifecycle API. Desktop shell, hybrid provider adapters, voice, perception, approval UI, computer-use adapters and multi-agent runtime remain planned. See the [implementation backlog](../plan/implementation-backlog.md) and [ADR-0001](../decisions/0001-core-architecture.md).
