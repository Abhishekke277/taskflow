"""
Real-LLM parser — only active when USE_REAL_LLM=true in config.

Calls the OpenAI Chat Completions API using the prompt built by prompt.py.
Falls back to mock_parser if the API call fails or returns malformed JSON.
"""

import json
import logging
from typing import Optional

from backend.config import OPENAI_API_KEY, OPENAI_MODEL
from backend.ai.prompt import build_messages
from backend.ai import mock_parser

logger = logging.getLogger(__name__)


def parse(text: str) -> dict:
    """
    Send *text* to the configured LLM and return parsed task fields.
    Falls back to mock_parser.parse() on any error.
    """
    try:
        # Lazy import so the project doesn't require openai when USE_REAL_LLM=false
        import openai  # type: ignore

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=build_messages(text),
            temperature=0,
            max_tokens=256,
        )

        raw = response.choices[0].message.content or ""
        parsed = json.loads(raw)

        # Validate required field
        if "title" not in parsed:
            raise ValueError("LLM response missing 'title' field")

        # Clamp priority to 1–5
        parsed["priority"] = max(1, min(5, int(parsed.get("priority", 3))))

        return parsed

    except Exception as exc:  # noqa: BLE001
        logger.warning("LLM parsing failed (%s); falling back to mock parser.", exc)
        return mock_parser.parse(text)
