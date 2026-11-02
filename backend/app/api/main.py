"""Authenticated loopback-only FastAPI entry point for Arya."""
from __future__ import annotations

import os
from pathlib import Path
from typing import FrozenSet

from fastapi import FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.app.providers.chat import ChatMessage, ChatService, ProviderNotConfigured, ProviderRequestFailed

from backend.app.security.api_guard import LocalRequestRejected, validate_local_request
from backend.app.security.sqlite_store import SQLiteSecurityStore
from backend.app.security.service import AuthorizationService
from backend.app.tasks import IdempotencyConflict, TaskNotFound, TaskStateConflict, TaskStore


class ChatMessageBody(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=12000)


class ChatBody(BaseModel):
    messages: list[ChatMessageBody] = Field(min_length=1, max_length=40)


class TaskCreateBody(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    instruction: str = Field(min_length=1, max_length=12000)


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
    task_database = Path(app.state.database_path).with_name(
        Path(app.state.database_path).name + ".tasks.sqlite3"
    )
    app.state.task_store = TaskStore(task_database)
    app.state.chat_service = ChatService()

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

    @app.post("/v1/chat/completions")
    async def chat_completion(body: ChatBody) -> dict[str, str]:
        try:
            messages = [ChatMessage(role=item.role, content=item.content) for item in body.messages]
            return await app.state.chat_service.complete(messages)
        except ProviderNotConfigured as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except ProviderRequestFailed as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    @app.post("/v1/tasks", status_code=201)
    async def create_task(
        body: TaskCreateBody,
        response: Response,
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> dict[str, object]:
        if idempotency_key is not None and not 8 <= len(idempotency_key) <= 128:
            raise HTTPException(status_code=422, detail="Idempotency-Key must be 8-128 characters.")
        title = body.title.strip()
        instruction = body.instruction.strip()
        if not title or not instruction:
            raise HTTPException(status_code=422, detail="Title and instruction cannot be blank.")
        try:
            task, created = app.state.task_store.create(
                title=title,
                instruction=instruction,
                idempotency_key=idempotency_key,
            )
        except IdempotencyConflict as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        response.status_code = 201 if created else 200
        return task

    @app.get("/v1/tasks")
    async def list_tasks(
        limit: int = Query(default=50, ge=1, le=100),
        before: str | None = Query(default=None, max_length=64),
    ) -> dict[str, object]:
        return {"tasks": app.state.task_store.list(limit=limit, before=before)}

    @app.get("/v1/tasks/{task_id}")
    async def get_task(task_id: str) -> dict[str, object]:
        try:
            return app.state.task_store.get(task_id)
        except TaskNotFound as exc:
            raise HTTPException(status_code=404, detail="Task not found.") from exc

    @app.post("/v1/tasks/{task_id}/cancel")
    async def cancel_task(task_id: str) -> dict[str, object]:
        try:
            return app.state.task_store.cancel(task_id)
        except TaskNotFound as exc:
            raise HTTPException(status_code=404, detail="Task not found.") from exc
        except TaskStateConflict as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    return app


app = create_app()
