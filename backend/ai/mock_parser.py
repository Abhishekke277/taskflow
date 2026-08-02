"""
Deterministic rule-based parser — the default parser when USE_REAL_LLM=false.

No API key required. Parses a natural-language string using simple keyword
rules and regex to produce the same field set that the LLM would return.
This is required (not optional) as the fallback path.
"""

import re
from typing import Optional


# Priority keyword maps (checked in order; first match wins)
_PRIORITY_RULES: list[tuple[list[str], int]] = [
    (["critical", "urgent", "emergency", "immediately"], 5),
    (["asap", "high priority", "important"], 4),
    (["low priority", "whenever", "no rush", "sometime"], 2),
    (["very low", "lowest"], 1),
]

# Regex to find an ISO date anywhere in the string
_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")

# Relative date hints
_REL_DATE_RE = re.compile(
    r"\b(today|tomorrow|next week|next month)\b", re.IGNORECASE
)


def _infer_priority(text: str) -> int:
    lower = text.lower()
    for keywords, priority in _PRIORITY_RULES:
        if any(kw in lower for kw in keywords):
            return priority
    return 3  # default


def _infer_due_date(text: str) -> Optional[str]:
    # Prefer explicit ISO date
    match = _DATE_RE.search(text)
    if match:
        return match.group(1)

    # Relative hints → return the keyword as a placeholder note in description
    # (real date math is out of scope for the mock parser)
    return None


def _infer_status(text: str) -> str:
    lower = text.lower()
    if any(kw in lower for kw in ["in progress", "working on", "started", "ongoing"]):
        return "in_progress"
    if any(kw in lower for kw in ["done", "finished", "completed", "complete"]):
        return "done"
    return "todo"


def _extract_title(text: str) -> str:
    """
    Use the first sentence (up to the first '.', '!', '?', or 80 chars)
    as the title.
    """
    first = re.split(r"[.!?]", text.strip())[0].strip()
    return first[:80] if first else text[:80]


def _extract_description(text: str, title: str) -> Optional[str]:
    """Return the remainder of the text after the title sentence, or None."""
    remainder = text.strip()[len(title):].lstrip(".!? ").strip()
    return remainder if remainder else None


def parse(text: str) -> dict:
    """
    Parse *text* and return a dict matching QuickAddResponse fields
    (excluding project_id and parser_used, which the caller adds).
    """
    title = _extract_title(text)
    description = _extract_description(text, title)
    priority = _infer_priority(text)
    due_date = _infer_due_date(text)
    status = _infer_status(text)

    return {
        "title": title,
        "description": description,
        "priority": priority,
        "due_date": due_date,
        "status": status,
    }
