# Product Requirements

## 1. Purpose and scope

Arya is the product identity and user-facing name. HeyAgent is the GitHub repository name. Arya is a production-grade Windows desktop AI companion. It must deliver the full approved feature scope; it is not a demo, toy application or reduced MVP.

## 2. Functional requirements

### FR-01 Desktop shell
Floating assistant surface, orb states, global shortcut, system tray, multi-window chat, agent/task dashboard, settings, notification surface, always-on-top controls, multi-monitor support, DPI-aware positioning, keyboard navigation and accessible UI.

### FR-02 Voice
Streaming speech input/output, STT, TTS, dictation, push-to-talk, optional wake-word mode, interruption/barge-in, partial transcripts, device selection, language detection, English/Hindi/Hinglish support, audio privacy controls and graceful text fallback.

### FR-03 Screen perception
Capture active window/selected region/display on explicit or configured events; obtain active application/window metadata; OCR; Windows accessibility tree; multimodal image understanding; visual grounding; multi-monitor/DPI mapping; sensitive-window detection and redaction; configurable capture history and retention.

### FR-04 Visual teaching
Transparent overlay; arrows, circles, highlights, labels and freehand marks; coordinate transform service; guided, state-aware tutorials; interactive whiteboard; 2D visualizations; Three.js-based 3D explanations; quiz/practice mode; annotation undo/clear and accessibility alternatives.

### FR-05 Computer use
Playwright DOM adapter, Windows UI Automation adapter and screenshot-coordinate fallback; click/type/scroll/drag/window navigation; file/application workflows; action planning; policy checks; confirmation UI; post-action observation; outcome verification; bounded retry; cancellation and recovery checkpoints.

### FR-06 Agent platform
LangGraph workflow runtime; plan/decompose tasks; specialist agents; controlled delegation and parallelism; typed tools; run lifecycle and event stream; pause/resume/cancel; persisted checkpoints; bounded execution; cost/token budgets; run transcript and failure diagnostics.

### FR-07 Memory and knowledge
Conversation storage; task memory; project and user preference scopes; searchable memory; explicit inspect/edit/delete/export; RAG; PDF/DOCX/XLSX/PPTX/CSV ingestion; provenance and citations for retrieved documents; configurable retention; exclusion of credentials and sensitive screen contents.

### FR-08 Integrations
MCP client and server registry; connector authorization; permission scopes; tool schemas; server trust controls; connection health; revocation; audit logging and per-integration disablement.

### FR-09 Skills and profiles
Versioned reusable skills, schema validation, source/provenance, permissions, user enable/disable, per-agent profiles and tests. Skills are instructions/data, never an authorization mechanism.

### FR-10 Background automation
Schedules, event triggers, recurring tasks, notification delivery, durable run state, bounded retries, concurrency limits, missed-run policy, timezone-aware scheduling and pause/disable controls.

### FR-11 Personalization
Model/provider selection, voice, language, shortcuts, theme, privacy, screen capture, model budgets, action policy, agent profiles and accessibility settings.

### FR-12 Production operations
Structured logs, diagnostics, health, crash recovery, update service, signed artifacts, migrations/backups, rollback, SBOM and third-party notices.

### FR-13 Security and safety

- Independent fail-closed policy engine; LLM output may propose actions but never authorize them.
- Trusted, authenticated, expiring capability grants scoped to user, session, tool, target and operation.
- Risk-based action handling: low-risk actions within grants; explicit fresh approval for high-impact actions; prohibited actions blocked.
- Approval bound to exact action payload, destination, user, session, task, expiry and one-time nonce; any mutation invalidates approval.
- Global emergency stop, pause, cancellation propagation and user takeover.
- No generic shell, arbitrary code execution or implicit administrator elevation exposed to agents.
- Treat webpages, emails, documents, OCR, screenshots, model outputs and MCP responses as untrusted data.
- Redacted audit trail, secret-safe logging and user-controlled retention/export/deletion.
- Loopback-only authenticated local API, strict Origin validation, request limits and secure Electron IPC.
- Windows-protected credential storage, isolated workers, signed updates and supply-chain verification.
- Screen/microphone capture is visible, permissioned, event-driven and user-controlled.

## 3. Non-functional requirements

- Security: least privilege, authenticated local IPC/API, no secrets in renderer/logs, separate authorization from LLM planning.
- Reliability: durable task checkpoints, safe cancellation, bounded retries, clear failure states and recoverable migrations.
- Performance: instrument end-to-end latency and resource consumption; establish hardware-specific budgets through benchmarks rather than unsupported claims.
- Privacy: data minimization, clear capture indicators, configurable retention, deletion and provider disclosure.
- Compatibility: Windows 11 x64 initially; multiple monitors, mixed DPI, display topology changes, sleep/resume and common Windows input methods.
- Maintainability: typed contracts, module boundaries, migrations, lockfiles, ADRs and automated tests.
- Accessibility: keyboard operation, screen reader labels, configurable motion and visual alternatives.
- Observability: per-task trace IDs, redacted structured logs, provider usage/cost telemetry and user-visible run history.

## 4. Autonomy and risk policy

- Read-only observation and summarization: automatic subject to capture settings.
- Low-risk navigation: automatic within configured boundaries.
- Reversible changes: automatic only inside approved workspaces and with recovery support.
- Sensitive actions (send/share/publish/upload externally): explicit per-action approval.
- High-impact actions (payment/purchase, account/security changes, destructive deletion): explicit approval and additional safeguards; some operations may be disallowed.
- Credential extraction, unauthorized access, malware-like behavior and policy bypass: blocked.

The policy engine, not the model, determines authorization. Approval must identify the exact action, target, scope and relevant data.

## 5. Acceptance rule

A requirement is complete only when implementation, documented behavior, relevant automated tests, failure handling, security review and user-facing controls are present. A UI placeholder or simulated operation does not satisfy a requirement.
