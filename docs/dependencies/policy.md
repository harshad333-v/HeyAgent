# Dependency and Open-Source Reuse Policy

## Purpose

Third-party projects may be used as references, dependencies or code foundations only after an explicit review. Repository popularity is not a substitute for source, license, security and maintenance review.

## Required review record

For every dependency, record:

- Canonical repository and package name.
- Exact version/tag/commit and package hash where available.
- License identifier and license text for the pinned release.
- Copyright and attribution requirements.
- Whether modifications or distribution create source-disclosure obligations.
- Maintainer and release activity.
- Open security advisories and known vulnerabilities.
- Transitive dependency inventory.
- Windows 11 compatibility and architecture.
- Runtime permissions, network behavior and data handling.
- Build/test evidence and decision owner.

## License handling

Do not assume a project's current default-branch license applies to every release or bundled asset. Inspect the exact pinned version. Preserve required notices. Escalate ambiguous, copyleft, dual-license, model-weight, dataset, font and asset licensing for review before distribution.

A package's license does not necessarily cover model weights, voice assets, datasets, browser binaries, icons or sample content.

## Security handling

- Pin versions and commit references.
- Commit lockfiles.
- Generate an SBOM for release artifacts.
- Run Python and npm vulnerability audits in CI.
- Prefer maintained official packages.
- Do not execute install scripts from unknown repositories without review.
- Keep optional/insecure dependencies out of the trusted core.
- Review every MCP server and skill independently.

## Reuse decision states

- Accepted: reviewed and approved for a specified use/version.
- Conditional: approved only after listed mitigations.
- Reference-only: may inform design, not copied or imported.
- Rejected: do not use.

## Initial candidates (not yet audited)

| Candidate | Intended evaluation | Current state |
|---|---|---|
| Monaw | Desktop shell/agent architecture | Reference-only pending source audit |
| Clicky Windows | Visual teaching patterns | Reference-only pending source audit |
| Windows Computer Use MCP | Windows automation patterns | Reference-only pending source audit |
| Electron | Desktop shell | Candidate; pin and verify release |
| React | Renderer UI | Candidate; pin and verify release |
| FastAPI | Backend API | Candidate; pin and verify release |
| LangGraph | Agent runtime | Candidate; pin and verify release |
| Playwright | Browser automation | Candidate; pin and verify release |
| pywinauto | Native UI automation | Candidate; pin and verify release |
| SQLite | Local database | Candidate; verify bundled/runtime notices |
| Three.js | 3D teaching | Candidate; pin and verify release |

No dependency in this table is represented as fully audited or approved for release.
