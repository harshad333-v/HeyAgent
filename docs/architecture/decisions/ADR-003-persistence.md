# ADR-003: Local persistence

- Status: Accepted
- Date: 2026-11-02

## Decision

Use SQLite with explicit migrations for local single-user application data. Store artifacts in an application-owned local directory. Use Windows-protected credential storage for provider and connector secrets. Use FTS5 for lexical search; add a vector index only where evaluation demonstrates value.

## Consequences

- Backups, restore and migration rollback require tests.
- SQLite writes must be serialized appropriately and transactions used for state transitions.
- Large binary data must not be placed directly in ordinary relational rows.
- Sensitive data retention and deletion must be implemented, not merely documented.
