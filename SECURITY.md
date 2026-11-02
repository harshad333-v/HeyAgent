# Security Policy

## Reporting

Do not publish credentials, exploit details or sensitive user data in public issues. Report suspected vulnerabilities privately through the GitHub repository's security reporting feature when enabled, or contact the repository maintainer through a private channel.

## Supported versions

Security support applies to the latest stable release. Older releases may require upgrading before a fix is provided.

## Security principles

- Least privilege and explicit capability grants.
- Model output is untrusted and cannot authorize actions.
- Sensitive actions require explicit confirmation.
- No unrestricted shell execution exposed to agents.
- Local APIs are authenticated and loopback-only.
- Credentials are protected by Windows facilities and excluded from logs/source control.
- Screen/audio capture is user-controlled with visible indicators and retention settings.
- Dependencies are pinned, scanned and included in the release SBOM.
