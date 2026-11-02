# ADR-0001: Arya Core Architecture and Product Decisions

- **Status:** Accepted
- **Date:** 2026-11-02
- **Scope:** Core architecture and implementation sequencing for Arya (repository: HeyAgent)

## Context

Arya is a Windows desktop assistant targeting the public feature scope audited in the HeyClicky parity document. The product needs realtime interaction, screen understanding, controlled computer use, persistent multi-agent work, integrations and background automation. These capabilities have different latency, privacy, cost and risk profiles, so the architecture must separate model reasoning from trusted execution and permission enforcement.

## Accepted decisions

### 1. Platform: Windows-first

- Target Windows 11 x64 as the primary supported platform and reference environment.
- Use Electron + React + TypeScript for the desktop shell and Python + FastAPI for the local application service.
- Integrate Windows-native capabilities through narrow adapters (Windows UI Automation, audio/device APIs, display/DPI APIs, Credential Manager/DPAPI).
- Keep platform-specific code behind interfaces so a future platform port is possible, but do not add macOS/Linux release commitments to the initial roadmap.
- Validate mixed-DPI, multi-monitor, sleep/resume, audio-device hot-plug, installer, update and uninstall behavior on Windows.

### 2. AI execution: hybrid cloud + local

- Define provider-neutral interfaces for text generation, structured output, vision, embeddings, speech recognition, speech synthesis and realtime audio.
- Support cloud providers and optional local model runtimes through the same capability contracts.
- Use a capability-aware router that considers task quality, model capability, privacy classification, latency, connectivity, cost and user preference.
- Cloud is the initial default for tasks that need strong reasoning or multimodal quality; local models are an optional path for supported private/offline/low-cost tasks.
- The router must expose why a provider was selected and must not silently send content to a cloud provider when the applicable privacy policy forbids it.
- Local mode must degrade gracefully when model assets, memory or hardware acceleration are unavailable.
- Provider credentials belong in Windows Credential Manager/DPAPI-backed storage. Local model files are not credentials and must have provenance/license checks.

### 3. Computer-use autonomy: approval-gated

- Computer-use actions are approval-gated by default. Arya may observe and prepare a proposed action, but must not click, type, submit, upload, delete, purchase, send or otherwise change external/native application state until the required user approval is granted.
- Approval is bound to the exact user, session, task, tool, target and canonical action payload; any material change invalidates it.
- The UI must show the target application/site, action summary, relevant data being sent/changed and risk before approval.
- Provide Allow once, Deny and Cancel/Stop controls. Any future remembered grant must be an explicit opt-in, narrow by tool/target/capability, revocable and auditable; it must not silently weaken the default approval posture.
- User takeover, Escape and emergency stop must interrupt active execution. After an approved action, obtain a fresh observation and verify the result.
- No arbitrary shell/terminal execution is exposed to the model. Use typed, least-privilege adapters.

### 4. Voice: both push-to-talk and hands-free

- Support push-to-talk as the default, predictable interaction mode.
- Support optional hands-free mode with explicit opt-in, visible microphone/listening indicator, configurable wake phrase and immediate mute/stop.
- Provide streaming speech recognition and synthesis, interruption/barge-in, captions, dictation and device selection.
- Voice must fall back to text when audio hardware, permissions, network or provider services fail.
- Do not retain raw audio by default; expose clear retention and deletion controls if a feature requires persistence.

### 5. Agent architecture: multi-agent with one orchestrator

- Use one supervisory orchestrator and a bounded set of specialist agents (for example: research, coding, documents, browser/computer-use and data analysis).
- Each specialist has a typed capability/tool allowlist, scoped context and memory, task budget, timeout and output contract.
- The orchestrator owns decomposition, delegation, checkpoints, conflict resolution and final synthesis; specialists cannot grant themselves permissions or expand their own tool access.
- Bound concurrency, recursion/delegation depth, wall-clock time, tokens, cost and tool calls.
- Persist task/run/step state and support pause, resume, retry, cancel and recovery.
- All tools execute through the central policy and approval layer. An agent's recommendation is never authorization.
- Prefer deterministic workflows or a single agent when delegation adds no measurable value.

## System architecture

Use a Windows desktop modular monolith with supervised worker processes, not a network microservice fleet.

1. **Electron main process:** application lifecycle, windows, tray, hotkeys, update lifecycle and worker supervision.
2. **React renderer:** orb, chat, task/agent dashboard, voice controls, screen context, approval prompts and settings.
3. **Secure preload bridge:** minimal schema-validated IPC; context isolation, sandboxing, no Node integration in renderer and strict CSP.
4. **Local FastAPI service:** authenticated loopback-only API, typed contracts, request limits and SSE event stream.
5. **Application core:** session, task state machine, provider router, agent orchestrator, event bus and policy enforcement.
6. **Intelligence layer:** provider adapters, LangGraph orchestration, perception, voice, memory and retrieval.
7. **Execution layer:** Playwright for browser DOM automation; Windows UI Automation for native applications; visual grounding only as a confidence-gated fallback.
8. **Supervised workers:** least privilege, explicit capability grants, bounded resource budgets, cancellation and process-level termination.
9. **Persistence:** SQLite with migrations for application/task/security metadata; local artifact store; optional FTS/vector indexes.
10. **Secrets and trust boundary:** Windows Credential Manager/DPAPI for secrets; providers, websites, MCP servers, imported files and model outputs are untrusted inputs.

## Core execution flow

User request -> classify privacy and risk -> route model/provider -> orchestrator builds a bounded plan -> collect user-approved observations -> specialist proposes typed action -> policy engine checks grant and exact target -> user approves exact action -> worker executes through a constrained adapter -> fresh observation verifies outcome -> persist audit/task state -> orchestrator reports verified result.

The language model is an untrusted planner. The policy engine, approval store, worker supervisor and execution adapters are trusted application components.

## Consequences and trade-offs

- Hybrid execution adds provider/model capability negotiation and local runtime packaging complexity, but provides flexibility across privacy, cost, latency and quality.
- Approval-gated computer use adds interaction friction, but materially reduces accidental/destructive actions and prompt-injection impact.
- Multi-agent orchestration improves task specialization and parallel work, but increases cost, latency and failure modes; bounded delegation and budgets are mandatory.
- Hands-free voice improves accessibility and speed, but requires explicit consent, visible capture state and careful audio lifecycle management.
- Windows-first allows deeper OS integration and a focused validation matrix, at the cost of delaying cross-platform support.

## Implementation order

1. Secure Windows desktop shell, IPC contracts, DPAPI credentials, local service lifecycle and worker supervisor.
2. Provider abstraction and hybrid routing; text chat and streaming event contracts.
3. Voice pipeline: push-to-talk first, then opt-in hands-free/wake phrase.
4. Screen perception and privacy controls.
5. Approval UI and constrained browser/native computer-use adapters.
6. Durable orchestrator, specialist agents, checkpoints and bounded delegation.
7. Memory, files, RAG and knowledge workflows.
8. MCP/connectors, routines, suggestions and notifications.
9. Visual teaching/drawing/3D.
10. Windows packaging, signing, updates, accessibility, security and parity validation.

## Non-goals for this ADR

- No commitment to a particular local model or provider vendor.
- No copying of HeyClicky proprietary code, branding, assets or private APIs.
- No unrestricted autonomous computer use.
- No unbounded agent swarm or arbitrary shell access.
- No multi-platform release commitment for the first production milestone.
