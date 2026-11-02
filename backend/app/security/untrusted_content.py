"""Represent external content as data, never as authority-bearing instructions."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ContentSource(StrEnum):
    WEBPAGE = "webpage"
    EMAIL = "email"
    DOCUMENT = "document"
    SCREEN_OCR = "screen_ocr"
    MCP_RESULT = "mcp_result"
    MODEL_OUTPUT = "model_output"


@dataclass(frozen=True, slots=True)
class UntrustedContent:
    source: ContentSource
    text: str
    source_id: str | None = None


def wrap_untrusted(text: str, source: ContentSource, source_id: str | None = None) -> UntrustedContent:
    """Tag provenance. Consumers must pass extracted actions through ActionPolicy regardless."""
    return UntrustedContent(source=source, text=text, source_id=source_id)
