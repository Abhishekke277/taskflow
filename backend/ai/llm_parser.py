"""
Real-LLM parser — only active when USE_REAL_LLM=true in config.

Calls GROQ (xAI) via the OpenAI-compatible SDK, using the prompt
built by prompt.py. Falls back to the mock parser if the API call
fails, times out, or returns malformed/invalid JSON.
"""

import json
import logging

from backend.config import GROQ_API_KEY
from backend.ai.prompt import build_quick_add_prompt
from backend.ai.mock_parser import parse_task_description

logger = logging.getLogger(__name__)


def parse_with_real_llm(description: str) -> dict:
    """
    Sends `description` to GROQ and returns parsed task fields:
    title, priority ('low'/'medium'/'high'), due_date_hint.
    Falls back to the deterministic mock parser on any error.
    """
    try:
        # Lazy import so the project doesn't require `openai` installed
        # when USE_REAL_LLM=false
        from openai import OpenAI

        prompt = build_quick_add_prompt(description)

        json_instruction = (
            prompt["system"] +
            " Respond ONLY with a valid JSON object with exactly these "
            "three keys: title (string), priority (one of 'low', "
            "'medium', 'high'), due_date_hint (string or null). "
            "No other text, no markdown formatting."
        )

        client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": json_instruction},
                {"role": "user", "content": prompt["user"]},
            ],
            temperature=0,
            max_tokens=200,
        )

        raw_text = (response.choices[0].message.content or "").strip()

        # Strip markdown code fences if the model added them anyway
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        parsed = json.loads(raw_text)

        required_keys = {"title", "priority", "due_date_hint"}
        if not required_keys.issubset(parsed.keys()):
            raise ValueError("LLM response missing required keys")

        if parsed["priority"] not in ("low", "medium", "high"):
            raise ValueError("LLM returned invalid priority value")

        return parsed

    except Exception as exc:
        logger.warning("LLM parsing failed (%s); falling back to mock parser.", exc)
        return parse_task_description(description)