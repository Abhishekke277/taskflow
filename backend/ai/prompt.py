"""
Prompt builder for the AI quick-add feature.

Uses a system + user role structure:
  - system role: locks the model to JSON-only output and defines the schema,
                 preventing free-text hallucination.
  - user role:   passes the raw natural-language task description.
"""


SYSTEM_PROMPT = """\
You are a task-parsing assistant. When given a plain-English task description, \
extract structured fields and return ONLY a JSON object with no extra text.

The JSON must follow this exact schema:
{
  "title":       "<string, required — concise task title>",
  "description": "<string or null>",
  "priority":    <integer 1–5, default 3 — 1=low, 5=critical>,
  "due_date":    "<YYYY-MM-DD string or null>",
  "status":      "<one of: todo | in_progress | done, default todo>"
}

Rules:
- Output valid JSON only. No markdown, no prose.
- Infer priority from urgency keywords: "critical"/"urgent" → 5, "asap" → 4, \
  "low priority"/"whenever" → 1–2, otherwise 3.
- If no due date is mentioned, set due_date to null.
- Keep title short (≤ 80 chars); move detail to description.
"""


def build_messages(user_text: str) -> list[dict]:
    """
    Return the messages list expected by the OpenAI Chat Completions API.

    Args:
        user_text: Raw natural-language string from the client.

    Returns:
        [{"role": "system", ...}, {"role": "user", ...}]
    """
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text.strip()},
    ]
