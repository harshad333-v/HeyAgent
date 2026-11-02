# ADR-004: Computer-use adapters

- Status: Accepted
- Date: 2026-11-02

## Decision

Use Playwright for browser DOM automation, Windows UI Automation for native accessible controls, and visual screenshot grounding as a fallback. All adapters implement a common typed interface and run behind the policy engine and constrained workers.

## Consequences

- DOM and accessibility semantics are preferred over coordinates.
- Coordinates require monitor/DPI transforms and fresh observations.
- All meaningful actions require post-action verification.
- Browser and desktop sessions must be isolated and cancellable.
- No model-generated arbitrary shell execution.
