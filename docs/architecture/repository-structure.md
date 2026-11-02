# Repository Structure

The structure below is the target layout. Directories are created as their owning modules are implemented; empty placeholder packages are not considered functionality.

```text
heyagent/
  apps/desktop/
    electron/{main,preload,windows}/
    renderer/{components,features,hooks,stores,services,pages}/
    assets/
  backend/
    app/
      api/ core/ config/ security/ events/
      agents/{runtime,planner,supervisor,specialists}/
      providers/{llm,vision,voice,embeddings}/
      perception/ computer/ teaching/ memory/
      integrations/ skills/ scheduler/ files/
      database/ observability/
    migrations/
  workers/{agent_worker,automation_worker,document_worker}/
  shared/{contracts,schemas,types}/
  tests/{unit,integration,contract,e2e,security,performance}/
  infrastructure/{packaging,signing,updates,ci}/
  docs/{architecture,api,security,deployment,decisions,dependencies,plan,quality,product}/
```

## Ownership boundaries

- `apps/desktop`: presentation and OS lifecycle; no AI business logic.
- `backend/app/api`: transport and schema validation; no provider-specific business logic.
- `backend/app/agents`: orchestration and task state; no direct unrestricted OS access.
- `backend/app/providers`: third-party AI provider adapters.
- `backend/app/computer`: policy-gated computer-use interfaces and adapters.
- `backend/app/security`: identity, capability checks, approval, redaction and audit.
- `workers`: isolated execution boundaries.
- `shared/contracts`: versioned API/event schemas shared across languages.
- `tests`: tests organized by contract and risk, not just by implementation folder.
- `infrastructure`: build, signing and update automation.

## Naming

Python packages use snake_case. TypeScript modules use the established feature convention. Public contracts are versioned and backward-compatible where possible. Architectural exceptions require an ADR.
