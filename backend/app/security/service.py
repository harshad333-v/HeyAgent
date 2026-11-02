"""Trusted authorization orchestration over persistent grants and approvals.

This service decides whether an action may proceed. It never executes tools.
Only trusted application code may issue grants; LLM output is treated as a proposal.
"""
from __future__ import annotations

import hashlib

from backend.app.security.audit import AuditLogger
from backend.app.security.models import ActionRequest, DecisionKind, PolicyDecision
from backend.app.security.policy_engine import ActionPolicy
from backend.app.security.sqlite_store import SQLiteSecurityStore
from backend.app.security.approvals import ApprovalChallenge


class AuthorizationService:
    def __init__(
        self,
        store: SQLiteSecurityStore,
        *,
        policy: ActionPolicy | None = None,
        audit: AuditLogger | None = None,
        approval_ttl_seconds: int = 120,
    ) -> None:
        if not 1 <= approval_ttl_seconds <= 600:
            raise ValueError("Approval TTL must be between 1 and 600 seconds.")
        self.store = store
        self.policy = policy or ActionPolicy()
        self.audit = audit or AuditLogger(store)
        self.approval_ttl_seconds = approval_ttl_seconds

    def request_approval(
        self,
        action: ActionRequest,
        *,
        grant_id: str,
        user_id: str,
        session_id: str,
    ) -> ApprovalChallenge:
        grant = self.store.get_grant(
            grant_id, user_id=user_id, session_id=session_id,
        )
        decision = self.policy.evaluate(
            action, grant, actor_user_id=user_id, session_id=session_id,
        )
        if decision.kind is not DecisionKind.REQUIRE_APPROVAL:
            raise PermissionError("This action is not eligible for an approval challenge.")
        return self.store.create_challenge(
            action, user_id=user_id, session_id=session_id,
            ttl_seconds=self.approval_ttl_seconds,
        )

    def approve(
        self, challenge_id: str, *, user_id: str, session_id: str,
    ) -> bool:
        return self.store.approve_challenge(
            challenge_id, user_id=user_id, session_id=session_id,
        )

    def authorize(
        self,
        action: ActionRequest,
        *,
        grant_id: str,
        user_id: str,
        session_id: str,
        approval_challenge_id: str | None = None,
    ) -> PolicyDecision:
        grant = self.store.get_grant(
            grant_id, user_id=user_id, session_id=session_id,
        )
        decision = self.policy.evaluate(
            action, grant, actor_user_id=user_id, session_id=session_id,
        )
        if decision.kind is DecisionKind.REQUIRE_APPROVAL:
            approved = self.store.consume_approval(
                approval_challenge_id, action, user_id=user_id, session_id=session_id,
            )
            decision = self.policy.evaluate(
                action, grant, actor_user_id=user_id, session_id=session_id,
                approval_valid=approved,
            )
        target_digest = hashlib.sha256(action.target.encode("utf-8")).hexdigest()
        self.audit.record(
            "action.authorization",
            task_id=action.task_id,
            actor=user_id,
            outcome=decision.kind.value,
            details={
                "tool": action.tool,
                "risk": decision.risk.value,
                "reason": decision.reason,
                "target_sha256": target_digest,
                "action_digest": decision.action_digest,
            },
        )
        return decision
