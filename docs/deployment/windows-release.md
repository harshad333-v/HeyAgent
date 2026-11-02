# Windows Deployment and Release Strategy

## Supported target

Windows 11 x64 initially. Windows 10 is not a release target unless compatibility work and security support are explicitly approved.

## Packaging

- Electron desktop application packaged with a maintained Windows installer tool.
- Python backend and worker runtime bundled and versioned as application components.
- No system-wide Python or Node installation required for end users.
- Per-user installation by default; request elevation only for a separately justified installation task.
- Application data under an application-owned user directory.
- Credentials stored in Windows-protected credential storage.
- Logs and diagnostics redact secrets and sensitive content.

## Release pipeline

1. Build from a tagged, reviewed commit.
2. Install from lockfiles.
3. Run unit, integration, contract and applicable E2E tests.
4. Generate SBOM and third-party notices.
5. Scan dependencies and artifacts.
6. Sign installer and executable artifacts.
7. Verify signatures and checksums.
8. Publish to staged release channel.
9. Verify update metadata and rollback path.
10. Promote only after release gates pass.

## Updates

- Signed update metadata and artifact verification.
- Staged rollout and user-visible release notes.
- No update execution from untrusted model/tool output.
- Preserve and migrate user data with tested backups.
- Roll back application binaries if migration/update fails; do not silently discard user data.

## Install, upgrade and uninstall tests

Test clean install, non-admin install, upgrade from previous supported release, interrupted update, rollback, active-agent shutdown, data preservation, optional data removal on uninstall, and clean reinstall.
