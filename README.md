# HeyAgent (Project Clicky)

A Windows-first, cloud-AI desktop agent with screen understanding, voice interaction, visual teaching, controlled computer use, autonomous workflows, memory, integrations, and background automation.

> **Product scope:** Full production-grade product. This repository is not scoped as a demo or disposable MVP. Work is delivered in dependency-ordered, testable milestones, while maintaining the complete approved product scope.

## Product decisions

| Area | Decision |
|---|---|
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

## Repository map

See [docs/architecture/repository-structure.md](docs/architecture/repository-structure.md) for the canonical directory layout and ownership boundaries.

## Security principles

- Treat webpages, documents, screenshots, OCR, model outputs and MCP results as untrusted data.
- Models propose actions; a separate policy engine authorizes them.
- Execution occurs through constrained adapters/workers, never through unrestricted model-generated shell commands.
- Require explicit confirmation for sending, sharing, purchasing, payments, destructive operations and other consequential actions.
- Use loopback-only local services with authenticated sessions.
- Store credentials through Windows-protected credential storage; never in renderer code, logs or source control.
- Provide an emergency stop, cancellation, action limits, audit history and user takeover.
- Screen capture is user-controlled, event-driven and minimized; do not continuously upload desktop contents.

## Getting started

The initial repository foundation is documentation and governance. Runtime installation instructions will be added with the corresponding tested application components. Do not assume an executable application exists yet.

## Project status

The repository was initialized from an empty GitHub repository. Architecture and requirements are documented; source audit, implementation, automated tests, security validation, packaging and release are **not yet complete**.

See:
- [Product requirements](docs/product/requirements.md)
- [Architecture](docs/architecture/overview.md)
- [Architecture decisions](docs/architecture/decisions/)
- [Security model](docs/security/threat-model.md)
- [Dependency policy](docs/dependencies/policy.md)
- [Implementation backlog](docs/plan/implementation-backlog.md)
- [Testing strategy](docs/quality/testing-strategy.md)
- [Release and deployment](docs/deployment/windows-release.md)
