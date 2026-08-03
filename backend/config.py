import os
from dotenv import load_dotenv

load_dotenv()

# Database — falls back to local SQLite if DATABASE_URL isn't set,
# though your actual .env should have the real Supabase connection string
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")

# Feature flag: defaults to False (unset/false) — grading always
# runs with this off, falling back to the mock parser automatically
USE_REAL_LLM: bool = os.getenv("USE_REAL_LLM", "false").lower() == "true"

# Grok (xAI) API key — only used if USE_REAL_LLM is True
GROK_API_KEY: str = os.getenv("GROK_API_KEY", "")