# ADR-002: Agent runtime and hybrid autonomy

- Status: Accepted
- Date: 2026-11-02

## Decision

Use LangGraph for durable agent workflow orchestration, with typed tool contracts, persisted checkpoints and bounded execution. Keep action authorization in an independent policy engine. Use hybrid autonomy: low-risk actions may run automatically inside approved scopes; sensitive and high-impact operations require explicit approval.

## Consequences

- The model is a planner/proposer, not an authority.
- Tool calls require schema validation, policy evaluation, capability scoping and audit events.
- Agent loops, retries, parallelism, token usage and wall-clock duration must be bounded.
- Cancellation and checkpoint restoration are first-class requirements.
- Approval UI must display the exact action and its consequences.
