"""Fail-closed authorization independent of the LLM planner."""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any

from .models import ActionRequest, CapabilityGrant, DecisionKind, PolicyDecision, RiskLevel


# These tools are never exposed as generic agent capabilities. Use narrow, typed adapters.
_NEVER_AGENT_TOOLS = frozenset({
    "shell", "terminal", "powershell", "cmd", "python_exec", "arbitrary_code",
    "run_command", "admin_elevation",
})
_CRITICAL_WORDS = ("payment", "purchase", "transfer", "security_change", "password_change")
_HIGH_WORDS = ("send", "share", "publish", "upload_external", "delete", "remove", "install", "format")
_LOW_TOOLS = frozenset({"read_document", "summarize", "search", "list_files", "read_screen"})


def canonical_action_digest(action: ActionRequest) -> str:
    """Stable digest binds approval to the exact tool, target, task and payload."""
    body: dict[str, Any] = {
        "task_id": action.task_id,
        "tool": action.tool,
        "capability": action.capability,
        "target": action.target,
        "payload": action.payload,
        "external_side_effect": action.external_side_effect,
        "destructive": action.destructive,
    }
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


class ActionPolicy:
    """Authorize only trusted grants; unknown or malformed actions fail closed."""

    def assess_risk(self, action: ActionRequest) -> RiskLevel:
        tool = action.tool.casefold()
        capability = action.capability.casefold()
        target = action.target.casefold()
        combined = f"{tool} {capability} {target}"
        if action.destructive or any(word in combined for word in _CRITICAL_WORDS):
            return RiskLevel.CRITICAL
        if action.external_side_effect or any(word in combined for word in _HIGH_WORDS):
            return RiskLevel.HIGH
        if tool in _LOW_TOOLS:
            return RiskLevel.LOW
        return RiskLevel.MEDIUM

    def evaluate(
        self,
        action: ActionRequest,
        grant: CapabilityGrant | None,
        *,
        approval_valid: bool = False,
        now: float | None = None,
    ) -> PolicyDecision:
        digest = canonical_action_digest(action)
        risk = self.assess_risk(action)
        timestamp = time.time() if now is None else now
        deny = lambda reason: PolicyDecision(DecisionKind.DENY, risk, reason, digest)
        require = lambda reason: PolicyDecision(DecisionKind.REQUIRE_APPROVAL, risk, reason, digest)

        if not action.task_id or not action.tool or not action.capability:
            return deny("Action is missing required identity fields.")
        if action.tool.casefold() in _NEVER_AGENT_TOOLS:
            return deny("Unrestricted command execution is not an agent capability.")
        if grant is None:
            return deny("No trusted capability grant is present.")
        if grant.expires_at <= timestamp:
            return deny("Capability grant is expired.")
        if action.capability not in grant.capabilities:
            return deny("Required capability was not granted.")
        if grant.allowed_tools and action.tool not in grant.allowed_tools:
            return deny("Tool is outside the grant's allowlist.")
        if grant.allowed_targets and action.target not in grant.allowed_targets:
            return deny("Target is outside the grant's exact allowlist.")
        if risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            if not approval_valid:
                return require("This action requires fresh approval bound to its exact payload and target.")
            return PolicyDecision(DecisionKind.ALLOW, risk, "Exact, unexpired approval and capability grant validated.", digest)
        return PolicyDecision(DecisionKind.ALLOW, risk, "Capability grant validated.", digest)
