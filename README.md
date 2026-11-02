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

## Security status

The feature/security-safety-foundation branch contains an initial executable Python security foundation and automated security tests. It currently implements:

- Independent, fail-closed authorization based on trusted capability grants (not model output).
- Exact tool/target checks, grant expiry and risk classification.
- Single-use approval challenges bound to user, session, task, exact action digest and expiry.
- Cooperative emergency stop for registered asyncio tasks.
- Recursive audit redaction and loopback/Origin/bearer-token validation helpers.
- Provenance tagging for external content as untrusted.

**This is not yet a production security certification.** Approval and audit adapters are currently in-memory; API validation is not yet wired into a running FastAPI service; OS-level worker isolation, Windows credential storage, Electron hardening, capture-consent UI and signed updates remain outstanding. See [security implementation status](docs/security/implementation-status.md) and [threat model](docs/security/threat-model.md).

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
