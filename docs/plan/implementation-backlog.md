# Implementation Backlog — Full Product

## Delivery policy

The complete product scope is retained. Work is sequenced by dependencies and risk; no milestone is a disposable demo. A capability is marked done only when implementation, tests, security review and user-facing behavior meet acceptance criteria.

## Workstream 0 — Foundation and source audit

- [ ] Inspect candidate repositories at pinned commits.
- [ ] Record exact licenses and notices for copied code/assets.
- [ ] Generate source/dependency comparison and reuse decisions.
- [ ] Set up branch protection and CI workflows.
- [ ] Establish Python/Node version policy and lockfiles.
- [ ] Define versioned API/event contracts.
- [ ] Establish migrations, structured logging and redaction.
- [ ] Add threat model and ADR review process.

## Workstream 1 — Desktop platform

- [ ] Electron main lifecycle and process supervision.
- [ ] Secure preload bridge and IPC schemas.
- [ ] React application shell and design tokens.
- [ ] Floating orb and state animation.
- [ ] System tray and global shortcut.
- [ ] Chat, agent dashboard and settings.
- [ ] Multi-monitor and mixed-DPI window placement.
- [ ] Notifications, accessibility and reduced-motion settings.
- [ ] Crash recovery and diagnostic bundle.

## Workstream 2 — Backend and cloud providers

- [ ] FastAPI service bound to loopback.
- [ ] Local session authentication and request controls.
- [ ] Typed provider capability registry.
- [ ] Gemini adapter.
- [ ] OpenAI adapter.
- [ ] Structured output and streaming normalization.
- [ ] Provider routing and fallback.
- [ ] Cost, token and latency usage ledger.
- [ ] User-configurable quotas and alerts.
- [ ] Secret storage integration.

## Workstream 3 — Perception and vision

- [ ] Screen/window/region capture with clear user controls.
- [ ] Capture indicator and privacy settings.
- [ ] OCR adapter and confidence output.
- [ ] Windows accessibility tree adapter.
- [ ] Visual grounding interface and model adapter.
- [ ] Display topology/DPI transform service.
- [ ] Sensitive-window and redaction policies.
- [ ] Screen change detection and event-based context reuse.
- [ ] Perception evaluation dataset and benchmarks.

## Workstream 4 — Voice

- [ ] Audio device enumeration and selection.
- [ ] STT provider adapter and streaming transcript.
- [ ] TTS provider adapter and streaming playback.
- [ ] Realtime audio session adapter where supported.
- [ ] VAD, interruption and barge-in.
- [ ] Dictation insertion with user-controlled focus.
- [ ] English/Hindi/Hinglish language handling.
- [ ] Audio permission, retention and text fallback.

## Workstream 5 — Computer use

- [ ] Typed common action and observation contracts.
- [ ] Playwright browser adapter with isolated profiles.
- [ ] Windows UI Automation adapter.
- [ ] Visual coordinate fallback.
- [ ] Action risk classifier and policy engine.
- [ ] Approval UI and replay protection.
- [ ] Worker isolation and capability grants.
- [ ] Verification and bounded recovery.
- [ ] Cancellation and emergency stop.
- [ ] Supported-application benchmark suite.

## Workstream 6 — Visual teaching

- [ ] Overlay lifecycle and input-through behavior.
- [ ] Shared coordinate transforms.
- [ ] Arrow, circle, highlight, labels and freehand tools.
- [ ] Annotation history/clear/undo.
- [ ] Guided walkthrough state machine.
- [ ] Interactive whiteboard.
- [ ] 2D diagram and chart renderer.
- [ ] Three.js 3D visualization renderer.
- [ ] Quiz/practice and lesson recording controls.
- [ ] Overlay E2E and multi-monitor tests.

## Workstream 7 — Agent platform

- [ ] LangGraph runtime and persistent checkpointer.
- [ ] Plan/task/run/step domain model.
- [ ] Typed tool registry and schema validation.
- [ ] Agent event stream and progress UI.
- [ ] Specialist profiles and scoped context.
- [ ] Delegation and bounded parallel execution.
- [ ] Pause/resume/retry/cancel.
- [ ] Per-run action, time and cost budgets.
- [ ] Failure diagnostics and verified completion criteria.

## Workstream 8 — Memory, documents and knowledge

- [ ] Conversation and task history.
- [ ] Scoped memory model and inspect/edit/delete UI.
- [ ] FTS search.
- [ ] Embedding/vector retrieval evaluation.
- [ ] Document ingestion workers for PDF/DOCX/XLSX/PPTX/CSV.
- [ ] Chunk provenance and retrieval citations.
- [ ] Workspace/project knowledge.
- [ ] Export, backup and restore.
- [ ] Sensitive data exclusion and retention controls.

## Workstream 9 — Integrations and skills

- [ ] MCP client with approved transports.
- [ ] MCP server registry and trust controls.
- [ ] Per-server and per-tool permissions.
- [ ] Connector authorization/revocation.
- [ ] Versioned skill format and validator.
- [ ] Skill execution policy and test harness.
- [ ] Connector health and audit history.

## Workstream 10 — Scheduling and background tasks

- [ ] Durable scheduler and timezone model.
- [ ] Event triggers and recurring jobs.
- [ ] Worker lifecycle supervision.
- [ ] Missed-run, retry and concurrency policies.
- [ ] Notifications and run history.
- [ ] Pause/disable/delete controls.
- [ ] Resource, cost and autonomy limits.

## Workstream 11 — Production release

- [ ] Full unit/integration/contract/E2E/security suite.
- [ ] Prompt injection and abuse testing.
- [ ] Windows 11 clean-install/upgrade/uninstall matrix.
- [ ] SQLite migration and rollback tests.
- [ ] Performance and memory benchmarks on reference hardware.
- [ ] SBOM and third-party notices.
- [ ] Installer and backend packaging.
- [ ] Code signing and secure update verification.
- [ ] Crash reporting/privacy review.
- [ ] Release runbook and support diagnostics.

## Definition of done

No item is complete based solely on a UI surface, stub, mocked response or happy-path manual test. Each capability needs automated tests, failure handling, documented permissions and user-visible controls. Release gates are defined in [testing-strategy.md](../quality/testing-strategy.md).
