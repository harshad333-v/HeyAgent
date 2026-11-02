# Implementation Backlog — Arya Full Product and HeyClicky Parity

## Accepted core architecture (2026-11-02)

The implementation plan is governed by [ADR-0001: Core Architecture](../decisions/0001-core-architecture.md):

- **Platform:** Windows 11 x64 first; Electron + React + TypeScript desktop, Python + FastAPI local service. No initial macOS/Linux release commitment.
- **AI execution:** hybrid cloud + optional local models behind provider-neutral capability interfaces and a privacy-aware router. Cloud is the initial default where policy permits; local execution is available when supported and selected.
- **Computer use:** approval-gated by default. Every state-changing computer-use action requires exact-action approval; any remembered grants are opt-in, narrow, revocable and audited.
- **Voice:** both push-to-talk (default) and opt-in hands-free/wake phrase, with visible microphone state and immediate mute/stop.
- **Agents:** multi-agent architecture with one supervisory orchestrator and bounded specialists; central policy controls every tool call.

These are binding architecture decisions, not shipped features. Do not mark a capability complete until implementation, tests, security review and user-visible controls exist.

## Source-of-truth audit

The public feature-parity audit is maintained in [HeyClicky Feature-Parity Audit](../product/heyclicky-feature-parity-audit.md). It records the official product sources, the verified repository baseline, parity requirements, and the implementation order. This backlog tracks delivery; the audit is the detailed acceptance reference.

**Parity status: NOT ACHIEVED.** Arya currently has a security foundation and architecture documentation. A desktop app, voice stack, perception, drawing, computer-use adapters, persistent agents, integrations and routines are not yet implemented. Do not report feature parity until the acceptance criteria in the audit are satisfied.

## Delivery policy

The complete product scope is retained. Work is sequenced by dependencies and risk; no milestone is a disposable demo. A capability is marked done only when implementation, tests, security review and user-facing behavior meet acceptance criteria. Do not copy HeyClicky proprietary code, branding or assets. Any third-party reference code requires license and security review.

## Workstream 0 — Foundation, audit and contracts

- [x] Public HeyClicky feature audit and current Arya baseline recorded.
- [ ] Inspect candidate reference repositories at pinned commits.
- [ ] Record exact licenses and notices for copied code/assets; prefer original implementations.
- [ ] Set up branch protection and CI workflows.
- [ ] Establish Python/Node version policy and lockfiles.
- [x] Define initial task API request/response contract (versioned event/SSE contract remains open).
- [ ] Establish migrations, structured logging and redaction.
- [ ] Define parity traceability: requirement -> implementation -> test -> release evidence.
- [ ] Establish threat model and ADR review process.

## Workstream 0A — Security foundation (implemented foundation on main; hardening remains)

- [x] Independent fail-closed policy engine and trusted capability grant model.
- [x] Exact tool/target checks, grant expiry and conservative risk classification.
- [x] One-time exact-action approval challenge primitive.
- [x] Cooperative asyncio emergency stop for registered tasks.
- [x] Audit redaction helper and loopback request validation helper.
- [x] Untrusted external-content provenance wrapper.
- [x] Focused security tests and GitHub Actions workflow.
- [x] Transactional persistent approval/grant storage and append-only audit database.
- [x] Trusted authorization service binds exact-action policy decisions, one-time approvals and redacted audit records.
- [x] Wire bearer auth, loopback/Origin checks and request-size limits into FastAPI middleware.
- [ ] Process-isolated workers, filesystem/network capability adapters and OS-level kill.
- [ ] Electron context isolation, secure preload/IPC, CSP and approval/kill-switch UI.
- [ ] Windows Credential Manager/DPAPI integration.
- [ ] Screen/audio capture consent indicators, privacy controls and retention/deletion UI.
- [ ] Signed update verification, SBOM and supply-chain policy enforcement.
- [ ] Adversarial Windows security testing and independent review.

## Workstream 1 — Windows 11 desktop shell and interaction model

- [ ] Windows 11 x64 support matrix, installer lifecycle and OS capability abstraction.

- [ ] Electron main lifecycle, single-instance lock and process supervision.
- [ ] Secure preload bridge, strict IPC schemas and renderer sandbox.
- [x] React application shell and initial dark chat workspace (development vertical slice).
- [x] Electron main/preload with context isolation, renderer Node disabled, sandbox enabled and narrow chat IPC.
- [ ] Production Electron lifecycle: single-instance lock, tray, hotkeys, persistent window state and signed packaging.
- [ ] Compact floating Arya surface with peek/expand/collapse behavior.
- [ ] Resizable full window with sidebar, chats, agents, settings and document pane.
- [ ] Persistent window size/position/state; multi-monitor and mixed-DPI support.
- [ ] System tray, global hotkeys, shortcut recorder and Escape handling.
- [ ] Orb/assistant states and agent cards with status, names, unread state and quick follow-up.
- [ ] Chat search, pin, archive/unarchive, mark read/unread and per-chat drafts.
- [ ] Long-chat pagination, lazy history loading and stable scroll position.
- [ ] Notifications, quiet mode, accessibility, keyboard navigation and reduced motion.
- [ ] Onboarding tour, user-preference interview and replayable setup.
- [ ] Crash recovery and redacted diagnostic bundle.

## Workstream 2 — Backend, provider abstraction and streaming

- [x] FastAPI local service skeleton bound to loopback with health/readiness and authenticated task lifecycle endpoints (no executor yet).
- [x] Local bearer authentication, Origin allowlist and request-size controls (development token provisioning only).
- [ ] DPAPI-backed per-installation/session token generation and rotation.
- [x] Authenticated `/v1/chat/completions` endpoint with bounded message history.
- [ ] Typed versioned API, SSE event stream, correlation IDs and reconnect behavior.
- [x] Initial provider-neutral text-chat contract with explicit Gemini/OpenAI selection.
- [ ] Capability registry and privacy-aware routing for structured output, vision, embeddings, STT, TTS and realtime audio.
- [x] Gemini cloud chat adapter (non-streaming initial vertical slice).
- [x] OpenAI chat-completions adapter (non-streaming initial vertical slice).
- [ ] Local model runtime adapter with model discovery, capability metadata, hardware/resource checks and offline behavior.
- [ ] Explicit provider selection/fallback explanation and privacy-policy enforcement (no prohibited cloud egress).
- [ ] Structured output and streaming normalization.
- [ ] Hybrid provider routing, fallback and region/network/local-runtime error handling.
- [ ] Cost, token, latency and usage ledger.
- [ ] User-configurable quotas, budgets and alerts.
- [ ] Secret storage integration and provider-key rotation.

## Workstream 3 — Screen perception and privacy

- [ ] Explicit hotkey/request-based display, active-window and region capture.
- [ ] Capture indicator, consent UI and privacy settings; no continuous hidden capture.
- [ ] Multi-monitor capture with physical/logical pixel and DPI metadata.
- [ ] Active application/window detection and conversation-scoped context.
- [ ] OCR adapter with confidence and language support.
- [ ] Windows accessibility tree adapter.
- [ ] Multimodal vision provider adapter and typed observation schema.
- [ ] Visual grounding interface with confidence thresholds and fresh observations.
- [ ] Display topology/DPI transform service.
- [ ] Sensitive-window detection, exclusion rules and redaction.
- [ ] Screenshot non-retention by default; inspect/delete capture-derived context.
- [ ] Screen perception evaluation dataset and benchmark suite.

## Workstream 4 — Voice, dictation and language parity

- [ ] Push-to-talk is the default voice interaction and ships before hands-free mode.
- [ ] Opt-in hands-free mode with visible microphone/listening indicator, configurable wake phrase and immediate mute/stop.

- [ ] Audio device enumeration, selection and hot-plug recovery.
- [ ] Hold-to-talk and configurable global shortcut/double-tap modes.
- [ ] Wake phrase detection is disabled until explicitly enabled; visible microphone state and immediate mute/stop are mandatory.
- [ ] Streaming STT with partial transcript, language auto-detection and mid-utterance switching.
- [ ] Streaming TTS with interruption/barge-in and immediate stop.
- [ ] Voice picker, preview, rate and language settings.
- [ ] Captions synchronized with voice output and chat.
- [ ] Dictation insertion into the focused app with clipboard-safe restoration.
- [ ] Terminal-safe dictation insertion (collapse newlines; never execute dictated text).
- [ ] Multilingual speech acceptance target: 130+ languages; dictation target: 83 languages.
- [ ] English/Hindi/Hinglish end-to-end test matrix.
- [ ] Text fallback for mic, speaker, provider and network failure.
- [ ] Audio permission, retention and deletion controls.

## Workstream 5 — Visual teaching and drawing

- [ ] Overlay lifecycle, transparent click-through behavior and input safety.
- [ ] Shared coordinate transforms across monitor, window, DPI and screenshot/model spaces.
- [ ] Pointer, arrow, circle, highlight, underline, label, card and freehand primitives.
- [ ] Annotation history, undo, clear and automatic lifecycle.
- [ ] Grounded image/photo cards with source attribution.
- [ ] Interactive 3D model renderer with select/rotate/zoom and GPU fallback.
- [ ] Guided walkthrough state machine with goal and completed-step log.
- [ ] Detect completion from fresh observation; never blindly repeat failed/completed steps.
- [ ] Next/continue/repeat/stop and pause/takeover controls.
- [ ] Tutor, quiz, slow pacing and IDE-aware code mode.
- [ ] Optional consent-based lesson recording with visible indicator and local transcript.
- [ ] Optional workflow capture with explicit start/stop, secret exclusions and user review.
- [ ] Overlay E2E and multi-monitor tests.

## Workstream 6 — Computer use and browser integration

- [ ] Typed common action/observation contracts.
- [ ] Chromium extension for Chrome, Edge, Brave, Arc and Vivaldi.
- [ ] Extension install, pairing, permissions and health checks.
- [ ] Playwright browser adapter with isolated task context/tab group.
- [ ] Ask whether to use current browser tab or separate context.
- [ ] Windows UI Automation adapter for native applications.
- [ ] Visual coordinate fallback with confidence and fresh screenshot.
- [ ] Integrate policy engine into every computer-use adapter; model output is never authorization.
- [ ] Approval UI for every state-changing action: show application/site, exact target, action and side-effect summary before execution.
- [ ] Allow once / Deny / Cancel-Stop flow; approval digest binds user, session, task, tool, target and exact payload.
- [ ] Optional remembered grants only after explicit opt-in; narrow scope, expiry, revocation and audit.
- [ ] Bind approval to exact conversation, task, tool, target and payload.
- [ ] Mouse/keyboard/Escape/user takeover stops active computer use; emergency stop reaches worker process.
- [ ] Worker isolation, process supervision and OS-level kill.
- [ ] Post-action observation, verification and bounded recovery.
- [ ] Supported-app/browser benchmark and adversarial permission tests.

## Workstream 7 — Persistent multi-agent orchestration

- [ ] One supervisory orchestrator owns planning, delegation, checkpoints, conflict resolution and final synthesis.
- [ ] Bounded specialist agents (research, coding, documents, data analysis, browser/computer use) with typed capabilities and output schemas.
- [ ] Specialist context/memory isolation; specialists cannot grant permissions or expand their own tool access.
- [ ] Hard limits for concurrency, delegation depth, wall-clock time, tokens, cost and tool calls.
- [ ] Route to a single agent/deterministic workflow when delegation adds no measurable value.

- [ ] LangGraph runtime and persistent checkpointer.
- [ ] Agent profile, name, purpose, scoped memory, conversation and output folder.
- [ ] Conversational agent creation with concise clarification.
- [ ] Global request routing to correct agent; duplicate prevention.
- [x] Initial durable task record, idempotent creation and queued-task cancellation API.
- [ ] Full plan/run/step model and worker state transitions.
- [ ] Typed tool registry and schema validation.
- [ ] Agent event stream and live progress UI.
- [ ] Agent cards with generated names, status, follow-up and latest output files.
- [ ] Specialist profiles, scoped context and controlled delegation under the single orchestrator.
- [ ] Bounded parallel execution and global concurrency limits.
- [ ] Pause/resume/retry/cancel and durable checkpoints.
- [ ] Per-run action, time, token and cost budgets.
- [ ] Long-running jobs with heartbeat and explicit continue/approval state.
- [ ] Follow-ups resume the same task; avoid duplicate jobs/charges.
- [ ] Retry classification, backoff, failure recovery and verified completion.
- [ ] Completion announcements, quiet modes and call/screen-share suppression.

## Workstream 8 — Files, whole-document understanding and memory

- [ ] Drag/drop, file picker, paste files/images and multiple attachments.
- [ ] PDF/DOCX/XLSX/PPTX/CSV/Markdown/TXT/image ingestion.
- [ ] Whole-document extraction for PDFs, office documents and web pages.
- [ ] Document preview pane beside chat; open externally; refresh Markdown preview.
- [ ] Per-agent output folder, artifact metadata and file history.
- [ ] Scoped conversation/task/project/preference memory.
- [ ] Memory inspect/edit/delete/export UI.
- [ ] FTS search and paginated conversation history.
- [ ] Embedding/vector retrieval evaluation and opt-in index.
- [ ] Chunk provenance and retrieval citations.
- [ ] Sensitive-data exclusion and configurable retention.
- [ ] Account deletion clears remote data and local caches/artifacts with confirmation.
- [ ] Backup/restore and portable export.

## Workstream 9 — Integrations, accounts, MCP and skills

- [ ] Built-in app catalog and connector lifecycle.
- [ ] MCP client with approved transports.
- [ ] MCP server registry, URL/local-command policy and trust controls.
- [ ] Browser OAuth and API-key connection flows.
- [ ] Per-server/per-account/per-tool permissions and revocation.
- [ ] Multiple accounts per provider with labels and explicit account routing.
- [ ] Real connector health checks; never trust token presence alone.
- [ ] Reconnect/expired-auth state and connector readiness before task execution.
- [ ] Live capability refresh after connector changes.
- [ ] Read-only app research before explicit write approval.
- [ ] Versioned skill format, validator, provenance and tests; skill text never grants permission.
- [ ] Connector health and audit history.

## Workstream 10 — Routines, suggestions and public-web research

- [ ] Natural-language routine creation and timezone-aware recurrence.
- [ ] Durable scheduler, run-now, pause, resume, edit and delete.
- [ ] Offline/sleep/app-readiness handling and single catch-up run.
- [ ] Bounded retries, repeated-failure auto-pause and concurrency policy.
- [ ] Quiet delivery to relevant agent chat with unread indicator.
- [ ] Public-web research with citations and recency metadata.
- [ ] Connected-app research with source provenance and read-only permission.
- [ ] Suggestion pipeline, source evidence, approve/skip/adjust/cancel and feedback.
- [ ] Duplicate suppression and preference learning from dismissed/approved suggestions.
- [ ] Morning suggestions respect focus, call, screen-share and quiet settings.
- [ ] Scheduler/resource/cost/autonomy limits and run history.

## Workstream 11 — Settings and product operations

- [ ] Settings for account, voice, language, shortcuts, theme, capture/privacy, agents, integrations and routines.
- [ ] Natural-language setting navigation and explanation.
- [ ] Usage/budget dashboard; Talk remains available when agent budget is exhausted.
- [ ] Optional subscription/billing layer requires a separate product decision; do not copy HeyClicky's plans or prices.
- [ ] Signed Windows installer and compatibility checks.
- [ ] Secure auto-update, idle-safe install, explicit relaunch and rollback.
- [ ] Release notes and update status in the desktop shell.
- [ ] Structured redacted logs, crash recovery and support diagnostics.
- [ ] Migrations, backups, restore and data deletion.
- [ ] SBOM, third-party notices, dependency/license scanning and supply-chain controls.
- [ ] Windows 11 x64 clean-install, upgrade, repair and uninstall matrix; assess Windows 10 separately without committing initial release support.
- [ ] Performance, accessibility, localization, sleep/resume, audio and display-change benchmarks.

## Workstream 12 — Release validation

- [ ] Windows 11 x64 reference-hardware validation, including mixed-DPI/multi-monitor, sleep/resume and audio hot-plug.
- [ ] Hybrid routing tests: cloud/local capability match, privacy no-egress rules, offline fallback and resource exhaustion.
- [ ] Voice tests for push-to-talk, hands-free opt-in, microphone indicator, mute/stop and barge-in.
- [ ] Approval tests for exact-action binding, payload tampering, replay, remembered-grant revocation and user takeover.
- [ ] Multi-agent tests for scope isolation, bounded delegation, concurrency and budget enforcement.

- [ ] Full unit/integration/contract/E2E/security suite.
- [ ] Prompt injection and untrusted-content adversarial testing.
- [ ] Computer-use approval replay/cross-agent/cross-task isolation tests.
- [ ] Capture consent, sensitive-window and retention/deletion tests.
- [ ] Windows 10/11 multi-monitor/mixed-DPI test matrix.
- [ ] Network/provider/connector outage and recovery tests.
- [ ] Long-running agent/routine idempotency and budget tests.
- [ ] SQLite migration, backup and rollback tests.
- [ ] Performance and memory benchmarks on reference hardware.
- [ ] SBOM and third-party notices.
- [ ] Installer, code signing and secure update verification.
- [ ] Release runbook and support diagnostics.

## Delivery sequence (updated for accepted decisions)

1. **Windows desktop foundation:** Electron main/renderer/preload, Windows lifecycle, secure IPC, DPAPI credentials, local API supervision and worker supervisor.
2. **Hybrid AI foundation:** provider capability contracts, Gemini/OpenAI adapters, local runtime adapter, privacy-aware routing, streaming chat and SSE events.
3. **Voice:** push-to-talk first; then opt-in hands-free/wake phrase, STT/TTS, barge-in, captions and dictation.
4. **Perception:** explicit screen capture, OCR, accessibility tree, vision and privacy controls.
5. **Approval-gated computer use:** approval UX and exact-action policy wiring before Playwright/Windows UI Automation can perform state-changing actions.
6. **Multi-agent runtime:** single orchestrator, bounded specialists, persistent task/run/step checkpoints, budgets and verified recovery.
7. **Memory and files:** document ingestion, scoped memory, RAG, history and artifacts.
8. **Integrations and automation:** MCP/connectors, account scopes, routines, suggestions and notifications.
9. **Visual teaching:** annotation overlays, guided walkthroughs and interactive 3D.
10. **Production hardening:** Windows packaging/signing/updates, accessibility, performance, adversarial security and full parity validation.

## Definition of done

No item is complete based solely on a UI surface, stub, mocked response or happy-path manual test. Each capability needs automated tests, failure handling, documented permissions and user-visible controls. The full detailed parity criteria are in [heyclicky-feature-parity-audit.md](../product/heyclicky-feature-parity-audit.md).
