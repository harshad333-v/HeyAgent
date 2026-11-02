# Architecture Overview

## 1. Architecture style

Use a modular monolith for the desktop product, with separately supervised workers for risky or resource-intensive execution (computer control, document parsing and long-running agents). Do not split into network microservices without a demonstrated operational need.

## 2. Topology

1. Electron main process: lifecycle, windows, tray, hotkeys, updates, secure process supervision.
2. React renderer: chat, orb, overlays, task dashboard, settings and approval UI.
3. Preload bridge: minimal typed and validated IPC surface; no generic Node access.
4. Python FastAPI service: loopback-only API, authenticated session, request validation, streaming events.
5. Application core: configuration, sessions, provider router, policy engine, task state and event bus.
6. Intelligence modules: LangGraph runtime, vision, voice, planning, memory and retrieval.
7. Execution adapters: Playwright, Windows UI Automation and visual fallback, each behind typed interfaces.
8. Workers: least-privileged processes with bounded capabilities, timeouts and cancellation.
9. Persistence: SQLite with migrations; local artifact directory; Windows-protected credential storage.
10. External boundary: AI providers, MCP servers, websites and imported documents are untrusted.

## 3. Communication

- Electron renderer to main: typed IPC through a narrow preload bridge.
- Desktop app to backend: authenticated loopback HTTP; SSE for durable application events; WebSocket/WebRTC only where realtime audio requires it.
- Backend modules: typed Python interfaces and domain events.
- Agent runtime: checkpointed state graph; no direct access to arbitrary OS APIs.
- Workers: bounded job contracts and explicit capability grants.
- MCP: supported protocol transports, allowlisted servers and per-tool policy checks.

## 4. Provider abstraction

Define independent interfaces for text generation, structured output, vision, embeddings, speech recognition, speech synthesis and realtime audio. Provider adapters normalize errors, streaming, usage and capability declarations. The router selects models by task capability, latency, cost, privacy and user preference. Do not couple business logic to a provider SDK.

## 5. Computer-use strategy

Prefer browser DOM semantics through Playwright when a supported browser session is available. Use Windows UI Automation for native controls. Use screenshot grounding only as a fallback, with fresh observation, coordinate transforms, confidence thresholds and verification. Never treat model-generated coordinates as inherently trustworthy.

## 6. Data flow

User intent -> risk classification -> task plan -> observation -> proposed action -> policy authorization -> optional approval -> constrained execution -> new observation -> verification -> persisted result.

The LLM is an untrusted planner. Authorization and execution are deterministic application responsibilities.

## 7. Reliability

Persist task state and checkpoints. Make task and tool operations idempotent where possible. Apply bounded retries with backoff only to retryable operations. Cancellation must propagate to provider requests, workers and browser sessions. Never report success based solely on a model assertion; verify external state.

## 8. Process and network boundaries

Bind local API only to loopback. Generate per-installation/session secrets and protect them with Windows facilities. Validate Origin and request authentication, limit request sizes and rate, and reject remote network access to the local service. Electron renderer must use context isolation and sandboxing; disable Node integration.

## 9. Storage

SQLite is the initial single-user store, with migration tooling and backup/restore. Use FTS for lexical retrieval and an optional vector index for semantic retrieval. Keep large artifacts outside the relational database. Credentials belong in Windows Credential Manager/DPAPI-backed storage, not SQLite plaintext.

## 10. Architecture constraints

- No direct provider SDK calls in UI components.
- No arbitrary shell tool exposed to the LLM.
- No unbounded agent loops or unconstrained parallelism.
- No background screen capture without visible user-configured controls.
- No secret or raw sensitive-screen logging.
- No dependency adoption without license and security review.
