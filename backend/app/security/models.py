"""Typed security domain models; no model-generated field grants authority."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionKind(StrEnum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    DENY = "deny"


@dataclass(frozen=True, slots=True)
class ActionRequest:
    """An action proposed by an agent; it is not an authorization credential."""
    task_id: str
    tool: str
    capability: str
    target: str = ""
    payload: Mapping[str, Any] = field(default_factory=dict)
    external_side_effect: bool = False
    destructive: bool = False


@dataclass(frozen=True, slots=True)
class CapabilityGrant:
    """Authority issued by trusted application code after user configuration."""
    user_id: str
    session_id: str
    capabilities: frozenset[str]
    allowed_tools: frozenset[str] = frozenset()
    allowed_targets: frozenset[str] = frozenset()
    expires_at: float = 0.0


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    kind: DecisionKind
    risk: RiskLevel
    reason: str
    action_digest: str

    @property
    def allowed(self) -> bool:
        return self.kind is DecisionKind.ALLOW
