# ADR-001: Windows-first platform and desktop shell

- Status: Accepted
- Date: 2026-11-02

## Context

The initial product target is Windows 11. The desktop experience requires floating windows, tray, global shortcuts, audio, overlays and a mature UI ecosystem.

## Decision

Use Electron + React + TypeScript for the desktop shell and Python + FastAPI for the application backend. Use a narrow, validated preload IPC bridge. Python owns AI, orchestration, perception and automation business logic.

## Consequences

- Shared TypeScript skills and UI ecosystem.
- Explicit process boundary and IPC security are mandatory.
- Application packaging must bundle and supervise a Python backend.
- PySide6 is not part of the primary desktop shell to avoid two competing GUI runtimes.
- Windows-specific functionality remains behind adapters to support later platform expansion.
