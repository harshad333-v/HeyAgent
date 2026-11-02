# Arya — Personal AI Assistant

**Arya** is a Windows-first personal AI assistant designed to combine conversational AI, local and cloud models, voice interaction, screen understanding, controlled computer use, specialist agents, memory, and workflow automation.

This repository contains the application and its supporting backend. The target is a complete, secure desktop assistant—not a disposable prototype. Development is organized into incremental milestones, and the status below distinguishes implemented foundations from planned capabilities.

## Product architecture

| Area | Current direction |
|---|---|
| Product | Arya |
| Platform | Windows 11 x64 first |
| Desktop | Electron, React, TypeScript |
| Backend | Python, FastAPI |
| Agent architecture | Supervisory orchestrator with bounded specialist agents |
| AI execution | Hybrid cloud and optional local models |
| Initial cloud providers | Gemini and OpenAI |
| Local model runtime | Planned; provider-neutral adapter |
| Browser automation | Playwright |
| Native desktop automation | Windows UI Automation; adapter evaluation ongoing |
| Persistence | SQLite and local artifact storage |
| Computer-use safety | Explicit approval before state-changing actions |
| Voice | Push-to-talk default; hands-free mode opt-in |
| Distribution | Signed Windows installer with secure updates |

The accepted architecture and rationale are recorded in [ADR-0001](docs/decisions/0001-core-architecture.md) and the [architecture overview](docs/architecture/overview.md).

## Product capabilities

The complete product is intended to include:

1. **Desktop workspace** — assistant window, floating panel, system tray, global shortcuts, chat history, settings and notifications.
2. **Conversational voice** — push-to-talk, optional hands-free interaction, speech recognition, speech synthesis, dictation, interruption and multilingual support.
3. **Screen intelligence** — user-authorized screen capture, OCR, accessibility-tree inspection, visual understanding and sensitive-content protections.
4. **Visual teaching** — annotations, guided walkthroughs, interactive explanations, whiteboard and 2D/3D learning experiences.
5. **Controlled computer use** — browser and Windows UI automation, explicit action approvals, execution isolation, verification and recovery.
6. **Multi-agent workflows** — task planning, bounded specialist agents, delegation, checkpoints, pause/resume/cancel and background execution.
7. **Memory and knowledge** — conversation history, scoped memory, document ingestion, retrieval-augmented generation (RAG), export and deletion controls.
8. **Integrations** — user-authorized connectors and MCP servers with scoped permissions.
9. **Automation** — schedules, triggers, notifications, run history, budgets and action limits.
10. **Production operations** — audit trails, diagnostics, crash recovery, secure credential storage, signed packaging and updates.

These are product goals, not a claim that every capability is already implemented.

## Current implementation status

### Implemented foundations

- FastAPI local service with loopback-only request boundary, bearer authentication and Origin validation.
- Security foundation with fail-closed authorization, scoped grants, exact-action one-time approvals, emergency-stop support and audit events.
- Durable task lifecycle API: create, list, read and cancel queued tasks. This API does not execute tasks.
- Authenticated /v1/chat/completions endpoint with bounded message history.
- Initial Gemini and OpenAI chat adapters with explicit provider selection.
- Initial Electron + React + TypeScript desktop chat shell.
- Context-isolated preload bridge, renderer Node integration disabled, sandbox enabled, and backend startup/readiness supervision.
- Architecture decisions, product requirements, security documentation and implementation backlog.

### Not yet complete

- Production Windows installer, signing, update and rollback flow.
- Packaged Python runtime and production credential provisioning through Windows Credential Manager/DPAPI.
- Persistent chat history and streaming responses.
- Task execution worker and multi-agent orchestration.
- Local model runtime and privacy-aware hybrid routing.
- Voice, screen perception and visual teaching.
- User-facing approval workflow and computer-use execution adapters.
- Persistent memory, document RAG and integrations.
- Schedules, background routines and notifications.
- Full end-to-end validation and release hardening.

See the [implementation backlog](docs/plan/implementation-backlog.md) for the detailed delivery sequence. Features are marked complete only when implemented and appropriately validated.

## Repository structure

- apps/desktop/ — Electron desktop application and React renderer.
- backend/ — FastAPI service, security services, task lifecycle and AI provider adapters.
- tests/ — automated backend and security tests.
- docs/ — architecture, product requirements, API contracts, security, testing and release documentation.

For the detailed layout, see [repository structure](docs/architecture/repository-structure.md).

## Requirements

- Windows 11 x64
- Python 3.11+
- Node.js 20+
- npm
- A Gemini or OpenAI API key for cloud chat

## Run Arya in development

From the repository root, install the Python backend:

    python -m pip install -e ".[test]"

Configure the desktop environment:

    cd apps/desktop
    Copy-Item .env.example .env

Edit apps/desktop/.env and set one provider key.

Gemini example:

    ARYA_DEFAULT_PROVIDER=gemini
    ARYA_CHAT_MODEL=gemini-2.5-flash
    GEMINI_API_KEY=your_gemini_api_key
    OPENAI_API_KEY=

Or select OpenAI:

    ARYA_DEFAULT_PROVIDER=openai
    ARYA_CHAT_MODEL=gpt-4.1-mini
    OPENAI_API_KEY=your_openai_api_key
    GEMINI_API_KEY=

Then install and launch the desktop shell:

    npm install
    npm run dev

The Electron main process starts the local FastAPI service, generates a per-launch local bearer token, waits for authenticated health readiness, and exposes the chat operation through a narrow preload bridge. Provider keys are read by the backend process and are not exposed to renderer JavaScript.

**Development limitation:** the current desktop shell is intended for local development. Packaged mode is deliberately disabled until the Python runtime is bundled, credential storage is hardened and the Windows release pipeline is implemented. Do not expose the local API on 0.0.0.0 or a network interface.

For backend-only operation and API details, see [local API operations](docs/deployment/local-api.md) and [task lifecycle API](docs/api/task-lifecycle.md).

## Run tests

From the repository root:

    python -m pytest -q tests

The desktop renderer build/typecheck can be run from apps/desktop:

    npm install
    npm run build

A CI workflow is configured for the Windows desktop renderer build. A configured workflow is not itself evidence of a passing run; check the repository Actions page for the latest result.

## Security principles

- Bind local services to loopback only.
- Keep API credentials out of renderer code, source control and logs.
- Fail closed when authorization or approval state is missing or invalid.
- Require explicit approval before state-changing computer actions.
- Scope permissions to the exact tool, target and action.
- Treat webpages, documents, screenshots and model outputs as untrusted input.
- Keep audit records useful while redacting secrets and sensitive payloads.
- Provide clear stop, cancellation and permission-revocation paths.

Read the [security threat model](docs/security/threat-model.md) and [security implementation status](docs/security/implementation-status.md) before extending tool execution.

## Project documentation

- [Product requirements](docs/product/requirements.md)
- [Architecture overview](docs/architecture/overview.md)
- [Core architecture decision record](docs/decisions/0001-core-architecture.md)
- [Implementation backlog](docs/plan/implementation-backlog.md)
- [Task lifecycle API](docs/api/task-lifecycle.md)
- [Local API operations](docs/deployment/local-api.md)
- [Security threat model](docs/security/threat-model.md)
- [Security implementation status](docs/security/implementation-status.md)
- [Dependency policy](docs/dependencies/policy.md)
- [Testing strategy](docs/quality/testing-strategy.md)
- [Windows release plan](docs/deployment/windows-release.md)

## Project status

Arya is under active development. The repository has a working implementation foundation, but it is not yet a complete production desktop assistant. Voice, autonomous task execution, multi-agent workflows, screen understanding, computer use, persistent memory, integrations, production packaging and end-to-end release validation remain in the implementation backlog.

Contributions should preserve the accepted architecture, security boundaries and documented feature status.