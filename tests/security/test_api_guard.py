import pytest
from backend.app.security.api_guard import LocalRequestRejected, validate_local_request


def test_valid_loopback_request_passes():
    validate_local_request(peer_host="127.0.0.1", origin="app://arya", authorization="Bearer secret", expected_token="secret", allowed_origins=frozenset({"app://arya"}))


@pytest.mark.parametrize("peer,origin,auth", [
    ("8.8.8.8", "app://arya", "Bearer secret"),
    ("127.0.0.1", "https://evil.example", "Bearer secret"),
    ("127.0.0.1", "app://arya", "Bearer wrong"),
    ("127.0.0.1", None, "Bearer secret"),
])
def test_invalid_local_requests_rejected(peer, origin, auth):
    with pytest.raises(LocalRequestRejected):
        validate_local_request(peer_host=peer, origin=origin, authorization=auth, expected_token="secret", allowed_origins=frozenset({"app://arya"}))
