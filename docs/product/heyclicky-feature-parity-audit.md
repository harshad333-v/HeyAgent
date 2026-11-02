# HeyClicky Feature-Parity Audit for Arya

**Audit date:** 2026-11-02  
**Reference product:** HeyClicky for Windows, official public website and changelog  
**Target:** Arya (repository: HeyAgent), Windows-first  
**Audit type:** Public product/feature audit. This is not a source-code audit of HeyClicky's proprietary implementation.

## 1. Executive result

Arya's current repository is a **security foundation and architecture specification**, not yet a working desktop assistant. The current README and architecture docs describe the intended full product, but the repository does not yet contain the desktop runtime, voice stack, screen-capture stack, drawing engine, computer-use adapters, agent runtime, connectors, or scheduler. The existing security code is a useful base, but it is not evidence of feature parity.

The official HeyClicky changelog identifies the current Windows release as v1.1.4 (2026-11-01). The parity target below includes the features publicly documented for Windows and the shared product experience. Mac-only implementation details are not copied literally; equivalent Windows-native behavior is the target.

**No proprietary HeyClicky code, assets, branding, UI copy, or private APIs are to be copied.** Implement original Arya code against the behaviors documented below. Review licenses before reusing any third-party reference implementation.

## 2. Source-of-truth and confidence

| Source | What it establishes | Treatment |
|---|---|---|
| [Official HeyClicky homepage](https://www.heyclicky.com/) | Product positioning, screen-capture privacy statements, Talk vs Agents, supported Windows versions, account/data deletion | Primary source |
| [Official HeyClicky changelog](https://www.heyclicky.com/changelog) | Versioned feature history; current Windows v1.1.4 features and earlier capabilities | Primary source |
| [Official trust page](https://www.heyclicky.com/trust) | Privacy/security details to be reviewed before release | Primary source; verify full policy during privacy milestone |
| [Clicky for Windows reference implementation](https://github.com/odzorp/Heyclicky-windows) | Publicly described technical patterns such as grid-based visual grounding, OCR fallback, voice activation, tutor modes and workflow capture | Secondary inspiration only; not proof that every item is an official HeyClicky feature; audit license before any code reuse |
| [Alternative Windows port](https://github.com/lefterisloukas/heyclicky-windowz) | Additional implementation ideas | Secondary inspiration only |

The official changelog's latest public Windows entry found during this audit is v1.1.4 dated November 1, 2026. Recheck it before each major parity release; this is a moving target.

## 3. Full parity requirements

### A. Desktop shell and interaction model

- [ ] Windows 10/11 desktop companion, single-instance lifecycle, startup/login preference and graceful shutdown.
- [ ] Compact floating top-edge/assistant surface analogous to the HeyClicky notch, with quick peek and expand/collapse behavior.
- [ ] Expand into a resizable full window with sidebar, conversation list, agent list, settings and document preview pane.
- [ ] Remember window size, position, open/closed state and theme across restarts; handle multi-monitor and mixed-DPI layouts.
- [ ] System tray, global hotkey configuration/recording, keyboard navigation and Escape behavior.
- [ ] Assistant presence/animation states: idle, listening, thinking, speaking, working, waiting for approval, complete and error.
- [ ] Agent cards with generated names, status, unread indicators, latest results/files, quick follow-up and previous/next navigation.
- [ ] Search, pin, archive, unarchive, mark read/unread, per-chat drafts, persistent scroll position and efficient lazy loading for long chats.
- [ ] Light/dark/system theme, accessibility labels, reduced motion, notifications and quiet/do-not-disturb behavior.
- [ ] Onboarding tour, profile/preferences interview, replayable tour and actionable permission setup.

### B. Talk, voice, dictation and language

- [ ] Separate quick Talk experience and delegated Agent jobs.
- [ ] Hold-to-talk from anywhere; configurable modifier combinations and double-tap/hands-free activation.
- [ ] Optional wake phrase only after explicit opt-in; microphone must remain visibly inactive otherwise.
- [ ] Streaming STT with partial transcript, automatic language detection and mid-sentence language switching.
- [ ] Streaming TTS with interrupt/barge-in, immediate Escape/stop, device selection and recovery after audio-device/network changes.
- [ ] Voice picker with preview; configurable speaking rate, voice and language.
- [ ] Captions while speech is playing; typed and spoken responses remain synchronized in chat.
- [ ] Dictation into the currently focused application with safe insertion, clipboard restoration and terminal newline safeguards.
- [ ] Multilingual voice target: 130+ spoken languages as documented by the current official release; dictation target: 83 languages. These are acceptance targets, not a claim about current Arya support.
- [ ] English, Hindi and Hinglish must be first-class tested paths.
- [ ] Text fallback when microphone, speaker, speech provider or network is unavailable.
- [ ] Audio never starts silently; show microphone state and retain only the minimum required data.

### C. Screen understanding and document context

- [ ] Capture only after a user hotkey/explicit request or a clearly configured user-authorized event. No continuous surveillance.
- [ ] Capture active window, selected region or chosen display; full multi-monitor support with physical/logical pixel and DPI metadata.
- [ ] Detect active app/window and maintain conversation-local screen context without attaching stale screenshots to unrelated turns.
- [ ] Multimodal vision adapter, OCR adapter and Windows accessibility/UI Automation tree adapter.
- [ ] Visual grounding with confidence scores and fresh observation before any coordinate action.
- [ ] Whole-document understanding for PDF, office documents and web pages, not just the visible viewport.
- [ ] Sensitive-window/privacy guard for password managers, authentication pages, banking, payment forms, credential files and configurable exclusions.
- [ ] Raw screenshots are not persisted by default; user-visible capture indicator, retention controls and explicit deletion.
- [ ] Screen context and text summaries must be scoped, inspectable and deletable.

### D. Drawing, visual teaching and learning

- [ ] Draw directly over the relevant screen/application while Arya explains.
- [ ] 2D annotation primitives: pointer/pointing, arrow, circle, highlight, underline, label, card and freehand sketch.
- [ ] Annotation coordinates must account for monitor origins, DPI scaling, window movement and display changes.
- [ ] Explanation cards can include grounded images/real photos where useful, with source attribution.
- [ ] 3D interactive models for suitable concepts (rotate, zoom, select parts, ask about selected part); graceful fallback on unsupported GPUs.
- [ ] Multi-step walkthroughs with explicit goal, current step, completed-step log, next/continue/repeat/stop and manual pause.
- [ ] Detect whether the user completed the instructed action; advance only after observation/verification, never by blindly repeating.
- [ ] Quiz/practice/tutor modes, including slower teacher pacing and code-specialist mode when an IDE is active.
- [ ] Optional lesson recording with user consent, local MP4 and transcript; recording indicator and retention/deletion controls.
- [ ] Optional workflow capture of clicks/keystrokes only with explicit start/stop consent, visible recording indicator, secret-field exclusions and user review before submission.

### E. Computer use and browser control

- [ ] Agent can perform tasks in native Windows apps and browsers, with user-visible progress.
- [ ] Browser extension for Chrome and compatible Chromium browsers (Edge, Brave, Arc, Vivaldi); explicit connection and scoped permissions.
- [ ] Use the user's signed-in browser profile only after explicit opt-in; isolate tasks in their own tab group/window and ask whether to use current tab or separate context.
- [ ] Playwright/DOM path first where possible; Windows UI Automation for native controls; visual grounding only as fallback.
- [ ] Before clicking/typing or otherwise controlling the computer, request scoped permission: Allow once, Always allow for the specified scope, or Not now.
- [ ] Approval is bound to the exact conversation, action, target and payload. It must not silently authorize other agents or tasks.
- [ ] User can immediately regain control by moving mouse, typing, pressing Escape or using a stop control.
- [ ] Avoid stealing focus or moving the real cursor when background/native APIs can safely operate without it.
- [ ] Fresh observation, post-action verification, bounded retries, helper-process health checks and safe recovery.
- [ ] Long walkthroughs retain goal and completed steps across pauses and never repeat failed/completed actions without a new reason.

### F. Persistent agents and task execution

- [ ] Create multiple named specialist agents from natural language; create up to a configurable bounded number in one request.
- [ ] Each agent has its own profile, purpose, chat history, scoped memory, task folder and generated artifacts.
- [ ] Create agents conversationally; ask concise clarifying questions when a missing decision materially affects execution.
- [ ] Route global voice/text requests to the correct active agent or offer creation of a new one; do not create duplicate agents from ambiguous follow-ups.
- [ ] Task planning, visible live progress, checkpoints, follow-ups, retries, pause/resume/cancel and task history.
- [ ] Multiple agents can work concurrently under global concurrency, cost, time and action budgets.
- [ ] Long-running jobs continue beyond 20 minutes only within configured budgets and with checkpoints/heartbeat.
- [ ] Jobs can ask for permission or clarification and resume the same run without charging/creating a duplicate task.
- [ ] Recover from transient DB/network/provider/connector failures; classify retryable vs permanent failures; cap retries and avoid duplicate side effects.
- [ ] Generated files appear in agent cards and a document pane; show only files produced by the latest result, while retaining historical artifacts in the task folder.
- [ ] Agent memory carries relevant previous work and current conversation context, with user inspection and deletion.
- [ ] Completion announcements, quiet hours, call/screen-share suppression and configurable spoken/text updates.

### G. Routines, suggestions and research

- [ ] Create routines from natural language (daily/weekly/interval schedules); timezone-aware recurrence.
- [ ] Routine management by conversation and UI: pause, resume, run now, edit, delete and view next run/history.
- [ ] Durable scheduler with offline/sleep handling, one catch-up run after wake, app readiness checks, bounded retries and auto-pause after repeated failures.
- [ ] Routines wait when a required app/network is unavailable or an agent is busy; do not spam repeated failure prompts.
- [ ] Results return to the relevant agent conversation with unread status; scheduled work stays quiet unless user opts in.
- [ ] Suggestions/recommendations based on recent authorized app activity and public-web research, with provenance and source evidence.
- [ ] Suggestion approval, skip, adjust, cancel, feedback and duplicate suppression; suggestions never perform writes before approval.
- [ ] Research can use connected app data and public web pages, including whole-document reading and recency windows; distinguish source facts from model synthesis.
- [ ] Morning greeting/suggestions respect calls, screen sharing, focus/quiet hours and user dismissal preferences.

### H. Integrations, accounts and MCP

- [ ] Built-in app catalog and custom MCP connections (remote URL or local command where supported).
- [ ] Browser OAuth/sign-in and API-key authentication with secure secret storage.
- [ ] Connector capability discovery and typed tool schemas; connector state must be verified against the actual service, not inferred from a saved token.
- [ ] Multiple accounts per provider with labels (e.g. Personal/Work), explicit account routing and per-account disconnect/reconnect.
- [ ] Read from multiple accounts only when permitted; identify source account in results; ask before ambiguous outbound actions.
- [ ] Connector health, reconnect flow, permissions, per-tool grants, revocation and audit history.
- [ ] App/connector changes update the live assistant capability context without requiring a new chat.
- [ ] Connected-app research should be read-only until a user approves a write/action.
- [ ] No claim of a connector being connected until a real health check succeeds.

### I. Files, outputs, history and account controls

- [ ] Drag/drop, file picker, paste image/file, multiple attachments and previews.
- [ ] Support PDF, DOCX, XLSX, PPTX, CSV, Markdown, TXT and common image formats.
- [ ] Preview documents, PDFs, images and generated artifacts next to the chat; open in external application; Markdown preview updates when file changes.
- [ ] Each agent has its own output folder and artifact history.
- [ ] Search conversations and archived agents; efficient paginated history.
- [ ] User can inspect, edit, export and delete memory; delete account/data and local agent files with clear confirmation.
- [ ] Data deletion must include local caches/artifacts and remote account data, with transparent deletion status.
- [ ] Export conversation and task records in documented portable formats.

### J. Settings, plans and product operations

- [ ] Settings for account, integrations, voices, language, shortcuts, theme, privacy, screen capture, dictation, agents, announcements, routines, storage and updates.
- [ ] User can ask Arya to navigate to the exact setting or explain current settings.
- [ ] Usage ledger for provider/API usage, task budgets and quotas; Talk remains separately available if agent budget is exhausted.
- [ ] Optional subscription/billing layer is a separate product/business decision; do not copy HeyClicky's prices, branding, plan names or commercial terms.
- [ ] Signed Windows installer, version check, secure auto-update, idle-safe restart, rollback and clear compatibility errors.
- [ ] Crash diagnostics, redacted logs, support bundle and release notes.
- [ ] Single-instance enforcement, wake/sleep/audio/display reconnection, localization-safe number/date parsing and long-session performance.

## 4. Arya repository baseline (verified from main)

The repository currently has:
- Python FastAPI local API skeleton exposing health and security-readiness only.
- Fail-closed policy engine, exact tool/target grants, one-time exact-action approvals, cooperative emergency stop, audit redaction, SQLite-backed grant/approval/audit storage and trusted authorization service.
- Loopback/Origin/bearer-token API guard.
- Architecture, product requirements, security and implementation backlog documentation.

The repository currently does **not** have:
- Electron desktop app or React renderer.
- Floating assistant shell, tray, hotkeys or full settings.
- STT, TTS, dictation, wake-word, realtime voice or multilingual voice pipeline.
- Screen capture, OCR, accessibility tree, vision provider or screen privacy UI.
- Drawing overlay, 2D/3D visualization or guided tutor engine.
- Playwright or Windows UI Automation adapters.
- Agent runtime, persistent task UI, document generation pipeline or task artifact browser.
- Routines, suggestions, web research pipeline or app connectors.
- MCP client/registry, multi-account connector model or browser extension.
- User-facing permission UI, DPAPI/Credential Manager, worker isolation, signed updater or packaged installer.

**Therefore current parity is not achieved.** The existing security foundation is not to be bypassed when adding these features.

## 5. Required implementation order

1. **Desktop/security runtime:** Electron shell, secure preload, local API session provisioning with DPAPI, typed contracts, user-facing permissions, stop control and worker supervisor.
2. **Talk and screen context:** user-triggered capture, privacy guard, active-window context, provider interfaces, STT/TTS streaming, dictation, captions and interruption.
3. **Visual teaching:** coordinate transforms, overlay, annotations, 2D cards and interactive 3D.
4. **Computer use:** browser extension/Playwright, Windows UI Automation, approval binding, verification and takeover.
5. **Agents:** persistent agent profiles/chats/folders, LangGraph runtime, event stream, task cards, progress, checkpoints, concurrency and budget enforcement.
6. **Files and knowledge:** attachment ingestion, whole-document parsing, previews, memory and retrieval.
7. **Connectors and MCP:** OAuth/API-key flows, multi-account model, health checks and revocation.
8. **Routines and suggestions:** durable scheduler, recovery, research, suggestions and quiet modes.
9. **Product completion:** settings, onboarding, update/signing, diagnostics, performance, accessibility, deletion/export and full E2E/security validation.

## 6. Definition of parity

A feature is not complete because a button, UI placeholder or mocked response exists. Each parity item needs:
1. Real implementation with the target Windows behavior.
2. Automated unit/integration/contract/E2E tests.
3. Failure, retry, cancellation and offline handling where relevant.
4. Explicit permission and privacy behavior.
5. User-facing status, controls and documentation.
6. Security review and no bypass of the policy/approval service.
7. Verified Windows 10/11 behavior, including multi-monitor and mixed-DPI where relevant.

Maintain a traceable feature-to-code-to-test matrix in this document as implementation progresses. Do not mark items complete until the definition above is met.

## 7. Public references

- Official homepage and FAQ: https://www.heyclicky.com/
- Official changelog (current Windows v1.1.4 entry and historical feature releases): https://www.heyclicky.com/changelog
- Official trust page: https://www.heyclicky.com/trust
- Secondary Windows reference (license and code reuse must be reviewed independently): https://github.com/odzorp/Heyclicky-windows
