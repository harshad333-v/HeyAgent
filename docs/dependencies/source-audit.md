# Open-Source Source Audit

## Status

Not started. The HeyAgent repository was empty at initialization, so no existing implementation was available to inspect. This document tracks candidate upstream audits; it does not assert that the repositories have been cloned or reviewed.

## Candidate projects

| Project | Candidate use | Audit status |
|---|---|---|
| Monaw | Desktop/agent architecture reference | Not audited |
| Clicky Windows | Teaching/annotation reference | Not audited |
| Windows Computer Use MCP | Windows automation reference | Not audited |

## Audit checklist per candidate

- [ ] Confirm canonical repository owner and URL.
- [ ] Record default branch and exact commit SHA.
- [ ] Inspect repository tree, README and build instructions.
- [ ] Inspect source code and runtime permissions.
- [ ] Inspect license at pinned commit and bundled assets.
- [ ] Identify AI provider requirements and costs.
- [ ] Review secret handling and network endpoints.
- [ ] Inspect shell, file and computer-control execution boundaries.
- [ ] Inspect tests and CI status.
- [ ] Review dependencies, advisories and release cadence.
- [ ] Build and test in an isolated Windows environment.
- [ ] Decide adopt, adapt, reference-only or reject.
- [ ] Record attribution and required notices.

## Decision template

For each project, document: observed architecture, verified features, unsupported claims, security findings, license findings, dependency risks, build result, reuse boundary, modifications needed, tests added and final decision.
