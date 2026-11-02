# HeyAgent — Arya

**Arya** is the product identity and user-facing assistant name. **HeyAgent** remains the GitHub repository name.

A Windows-first, cloud-AI desktop agent with screen understanding, voice interaction, visual teaching, controlled computer use, autonomous workflows, memory, integrations, and background automation.

> **Product scope:** Full production-grade product. This repository is not scoped as a demo or disposable MVP. Work is delivered in dependency-ordered, testable milestones while retaining the complete approved product scope.

## Product decisions

| Area | Decision |
|---|---|
| Product | Arya |
| Repository | HeyAgent |
| Platform | Windows 11 x64 first |
| Desktop | Electron + React + TypeScript |
| Backend | Python + FastAPI |
| Agent orchestration | LangGraph |
| AI strategy | Cloud-first; provider-independent adapters |
| Initial providers | Gemini and OpenAI adapters, subject to capability and cost evaluation |
| Browser automation | Playwright |
| Native desktop automation | Windows UI Automation, evaluated adapters such as pywinauto |
| Persistence | SQLite with migrations; local files for artifacts |
| Autonomy | Hybrid: automatic low-risk actions, approval for sensitive/high-impact actions |
| Architecture | Modular monolith with isolated execution workers |
| Distribution | Signed Windows installer, updates and rollback |

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

## Security and local API status

The security foundation is now on `main`. It includes fail-closed authorization, explicit tool/target grants, exact-action one-time approvals, cooperative emergency stop, audit redaction, persistent SQLite grants/approvals/audit events, a trusted authorization service that binds policy decisions to one-time approvals, and a FastAPI request boundary that rejects non-loopback peers, untrusted Origins and invalid bearer tokens.

The local API currently exposes health and security-readiness endpoints only. It is not yet a chat service or autonomous task executor. The token is supplied through `ARYA_LOCAL_API_TOKEN` for development; production Windows builds must move token provisioning to Windows Credential Manager/DPAPI. Desktop runtime, worker isolation, user-facing permissions/approval UI, Windows-specific hardening and signed updates remain open.

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

The repository is being implemented in milestones. The security foundation can be installed with `python -m pip install -e ".[test]"` and tested with `python -m pytest -q tests/security` using Python 3.11+. The desktop app and API server are not yet implemented; do not assume an executable application exists.

## Project status

Architecture and requirements are documented; the first security foundation is on a feature branch. Desktop runtime, API integration, persistent security storage, Windows-specific controls, full product implementation, end-to-end validation, packaging and release are **not yet complete**.

See:
- [Product requirements](docs/product/requirements.md)
- [Architecture](docs/architecture/overview.md)
- [Security model](docs/security/threat-model.md)
- [Security implementation status](docs/security/implementation-status.md)
- [Dependency policy](docs/dependencies/policy.md)
- [Implementation backlog](docs/plan/implementation-backlog.md)
- [Testing strategy](docs/quality/testing-strategy.md)
- [Release and deployment](docs/deployment/windows-release.md)
