# Testing and Quality Strategy

## Test layers

- Python unit tests: pytest and pytest-asyncio.
- TypeScript unit/component tests: Vitest and React Testing Library.
- API/contract tests: validated OpenAPI and JSON event schemas.
- Browser tests: Playwright Test.
- Desktop E2E: Windows runner with controlled virtual/test desktop where practical.
- Property tests: Hypothesis for transforms, parsers and policy invariants.
- Static checks: Ruff, mypy/pyright, ESLint and TypeScript compiler.
- Security checks: Semgrep, pip-audit, npm audit, secret scan and SBOM analysis.
- Manual exploratory tests: multi-monitor, mixed DPI, sleep/resume, audio devices and real applications.

## High-risk scenarios

1. Prompt injection from webpage, OCR text, PDF and MCP tool result.
2. Attempt to invoke a tool outside its granted capability.
3. Approval replay or approval for a different action/target.
4. Cancellation while action is pending, executing or verifying.
5. Provider timeout, rate limit and malformed streamed response.
6. Browser navigation to an untrusted origin.
7. File path traversal, symlinks, oversized and malformed documents.
8. Credential redaction from exceptions and logs.
9. Display topology change between observation and click.
10. Mixed-DPI coordinate conversion and monitor negative coordinates.
11. Agent retry/parallelism and usage-budget exhaustion.
12. Database crash, migration failure and backup restoration.
13. Malicious MCP server schema/output and unavailable server.
14. Uninstall/update while background workers are active.

## Acceptance gates

- Zero unresolved critical/high security findings at stable release.
- No unauthorized high-risk action in policy tests.
- All mandatory unit, integration, contract and E2E tests pass.
- Action cancellation and emergency stop tested under race conditions.
- All meaningful external actions have outcome verification.
- Database backup/restore and migration recovery demonstrated.
- Performance targets measured on the reference Windows hardware.
- UI automation success is measured on a versioned representative benchmark; do not claim a universal accuracy percentage.

## Performance measurements

Track cold start, idle memory, active memory, screenshot-to-observation latency, speech partial latency, first-token latency, action-to-verification latency, CPU usage, provider cost per task and recovery time. Define numeric budgets only after a reproducible baseline and workload profile are collected.
