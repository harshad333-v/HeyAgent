"""Small fail-closed guard for a loopback-only local API."""
from __future__ import annotations

import hmac
import ipaddress


class LocalRequestRejected(PermissionError):
    pass


def validate_local_request(
    *, peer_host: str, origin: str | None, authorization: str | None,
    expected_token: str, allowed_origins: frozenset[str],
) -> None:
    try:
        address = ipaddress.ip_address(peer_host)
    except ValueError as exc:
        raise LocalRequestRejected("Invalid peer address.") from exc
    if not address.is_loopback:
        raise LocalRequestRejected("Local API accepts loopback connections only.")
    if origin not in allowed_origins:
        raise LocalRequestRejected("Request origin is not allowed.")
    if not expected_token or not authorization or not authorization.startswith("Bearer "):
        raise LocalRequestRejected("Missing local session authentication.")
    supplied = authorization[7:]
    if not hmac.compare_digest(supplied, expected_token):
        raise LocalRequestRejected("Invalid local session authentication.")
