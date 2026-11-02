"""Authenticated loopback-only FastAPI entry point for Arya."""
from __future__ import annotations

import os
from pathlib import Path
from typing import FrozenSet

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from backend.app.security.api_guard import LocalRequestRejected, validate_local_request
from backend.app.security.sqlite_store import SQLiteSecurityStore
from backend.app.security.service import AuthorizationService


def _origins_from_env() -> FrozenSet[str]:
    raw = os.environ.get("ARYA_ALLOWED_ORIGINS", "app://arya")
    return frozenset(item.strip() for item in raw.split(",") if item.strip())


def create_app(
    *,
    token: str | None = None,
    allowed_origins: FrozenSet[str] | None = None,
    database_path: str | Path | None = None,
) -> FastAPI:
    """Build the API. An absent token is deliberately fail-closed."""
    expected_token = token if token is not None else os.environ.get("ARYA_LOCAL_API_TOKEN", "")
    origins = allowed_origins if allowed_origins is not None else _origins_from_env()
    app = FastAPI(
        title="Arya Local API",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.database_path = str(
        database_path or os.environ.get(
            "ARYA_DATABASE_PATH", str(Path.home() / ".arya" / "data" / "arya.sqlite3")
        )
    )
    app.state.security_store = SQLiteSecurityStore(app.state.database_path)
    app.state.authorization_service = AuthorizationService(app.state.security_store)

    @app.middleware("http")
    async def require_local_session(request: Request, call_next):
        peer_host = request.client.host if request.client else ""
        try:
            validate_local_request(
                peer_host=peer_host,
                origin=request.headers.get("origin"),
                authorization=request.headers.get("authorization"),
                expected_token=expected_token,
                allowed_origins=origins,
            )
        except LocalRequestRejected:
            return JSONResponse(
                status_code=403,
                content={"error": "local_request_rejected"},
                headers={"Cache-Control": "no-store"},
            )
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > 1_048_576:
                    return JSONResponse(
                        status_code=413, content={"error": "request_too_large"},
                        headers={"Cache-Control": "no-store"},
                    )
            except ValueError:
                return JSONResponse(status_code=400, content={"error": "invalid_content_length"})
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "arya-local-api"}

    @app.get("/v1/security/readiness")
    async def security_readiness() -> dict[str, object]:
        return {
            "api_authentication": bool(expected_token),
            "loopback_only": True,
            "origin_allowlist_configured": bool(origins),
            "database_path_configured": bool(app.state.database_path),
            "approval_storage": "sqlite-transactional",
            "audit_storage": "sqlite-append-only",
            "authorization_service": True,
        }

    return app


app = create_app()
