# HeyAgent — Arya

**Arya** is the product identity and user-facing assistant name. **HeyAgent** remains the GitHub repository name.

A Windows-first, hybrid-AI desktop agent with screen understanding, voice interaction, visual teaching, controlled computer use, autonomous workflows, memory, integrations, and background automation.

> **Product scope:** Full production-grade product. This repository is not scoped as a demo or disposable MVP. Work is delivered in dependency-ordered, testable milestones while retaining the complete approved product scope.

## Product decisions

| Area | Decision |
|---|---|
| Product | Arya |
| Repository | HeyAgent |
| Platform | Windows 11 x64 first |
| Desktop | Electron + React + TypeScript |
| Backend | Python + FastAPI |
| Agent orchestration | Multi-agent: one supervisory orchestrator + bounded specialist agents (LangGraph) |
| AI strategy | Hybrid cloud + optional local models; privacy-aware provider routing |
| Initial providers | Gemini and OpenAI adapters, subject to capability and cost evaluation |
| Browser automation | Playwright |
| Native desktop automation | Windows UI Automation, evaluated adapters such as pywinauto |
| Persistence | SQLite with migrations; local files for artifacts |
| Computer-use autonomy | Approval required before every state-changing action; remembered grants are explicit opt-in only |
| Voice | Push-to-talk default + opt-in hands-free/wake phrase |
| Architecture | Modular monolith with isolated execution workers |
| Distribution | Signed Windows installer, updates and rollback |

The binding architecture decisions, rationale, system topology and delivery sequence are recorded in [ADR-0001](docs/decisions/0001-core-architecture.md) and [Architecture Overview](docs/architecture/overview.md). These are target decisions; planned components are not yet shipped.

## Full product capabilities

1. Desktop companion: floating orb/panel, global hotkeys, tray, chat, settings, multi-monitor and DPI support.
2. Voice: streaming conversation, STT, TTS, dictation, interruption/barge-in, device selection and multilingual operation.
3. Screen intelligence: event-driven capture, OCR, accessibility tree, multimodal understanding, visual grounding and privacy filtering.
4. Visual teaching: arrows, circles, labels, freehand annotations, tutorials, interactive whiteboard, 2D and 3D explanations.
5. Computer use: browser DOM automation, Windows UI Automation, visual fallback, file/application workflows, verification and recovery.
6. Agents: task planning, specialized agents, delegation, checkpoints, pause/resume/cancel, skills, MCP and background execution.
7. Memory and knowledge: conversations, scoped persistent memory, RAG, document ingestion, searchable history, export and deletion.
8. Integrations: user-authorized connectors and MCP servers with scoped permissions.
9. Automation: schedules, triggers, notifications, run history and spending/action limits.
10. Production operations: audit logs, cost tracking, diagnostics, crash recovery, packaging, signing, updates and rollback.

## HeyClicky feature-parity target

The official public feature audit is documented in [HeyClicky Feature-Parity Audit](docs/product/heyclicky-feature-parity-audit.md). It records the official Windows changelog feature set, detailed acceptance requirements, the verified Arya repository baseline and delivery order.

**Current status: parity is not achieved.** The repository contains the backend security foundation, architecture/product documentation, and an authenticated durable task-lifecycle API. The task API supports create/list/read/cancel for queued work, but it does not execute tasks. A development Electron + React chat shell is now present; voice, screen perception, drawing, computer-use adapters, agent runtime, integrations and routines are not yet implemented. See the [implementation backlog](docs/plan/implementation-backlog.md) for the complete task breakdown. Planned features must not be described as shipped functionality.

## Security and local API status

The security foundation is on `main`. It includes fail-closed authorization, explicit tool/target grants, exact-action one-time approvals, cooperative emergency stop, audit redaction, persistent SQLite grants/approvals/audit events, a trusted authorization service that binds policy decisions to one-time approvals, and a FastAPI request boundary that rejects non-loopback peers, untrusted Origins and invalid bearer tokens.

The local API exposes health, security-readiness and authenticated task-lifecycle endpoints (`POST/GET /v1/tasks`, `GET /v1/tasks/{id}`, and `POST /v1/tasks/{id}/cancel`). Task records are persisted in a separate SQLite database and support idempotent creation. There is not yet a chat service, task worker or autonomous task executor. The token is supplied through `ARYA_LOCAL_API_TOKEN` for development; production Windows builds must move token provisioning to Windows Credential Manager/DPAPI. Desktop runtime, worker isolation, user-facing permissions/approval UI, Windows-specific hardening and signed updates remain open.

### Run the local API (Python 3.11+)

```powershell
python -m pip install -e ".[test]"
$env:ARYA_LOCAL_API_TOKEN = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:ARYA_ALLOWED_ORIGINS = "app://arya"
uvicorn backend.app.api.main:app --host 127.0.0.1 --port 8765
```

Requests must include both `Origin: app://arya` and `Authorization: Bearer <token>`. The service deliberately rejects requests without a configured token, valid Origin and loopback peer. Do not expose it on `0.0.0.0` or a LAN interface. See [local API operations](docs/deployment/local-api.md).

Run tests:

```powershell
python -m pytest -q tests
```

## Repository map

See [docs/architecture/repository-structure.md](docs/architecture/repository-structure.md) for the canonical directory layout and ownership boundaries.

## Getting started

The repository is being implemented in milestones. The security foundation can be installed with `python -m pip install -e ".[test]"` and tested with `python -m pytest -q tests/security` using Python 3.11+. The API foundation is available, but the desktop app and task execution worker are not implemented; do not assume an executable desktop assistant exists.

## Project status

The security foundation and authenticated task-lifecycle API are on `main`. The desktop runtime, provider integration, task execution worker, user-facing permission workflow, Windows-specific controls, full product implementation, end-to-end validation, packaging and release are **not yet complete**.

See:
- [Product requirements](docs/product/requirements.md)
- [HeyClicky feature-parity audit](docs/product/heyclicky-feature-parity-audit.md)
- [Architecture](docs/architecture/overview.md)\n- [Core architecture decision record](docs/decisions/0001-core-architecture.md)
- [Task API contract](docs/api/task-lifecycle.md)
- [Security model](docs/security/threat-model.md)
- [Security implementation status](docs/security/implementation-status.md)
- [Dependency policy](docs/dependencies/policy.md)
- [Implementation backlog](docs/plan/implementation-backlog.md)
- [Testing strategy](docs/quality/testing-strategy.md)
- [Release and deployment](docs/deployment/windows-release.md)
