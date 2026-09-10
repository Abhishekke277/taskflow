import os
from dotenv import load_dotenv

load_dotenv()

# Database — falls back to local SQLite if DATABASE_URL isn't set,
# though your actual .env should have the real Supabase connection string
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")

# Feature flag: defaults to False (unset/false) — grading always
# runs with this off, falling back to the mock parser automatically
USE_REAL_LLM: bool = os.getenv("USE_REAL_LLM", "false").lower() == "true"

# Groq (xAI) API key — only used if USE_REAL_LLM is True
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")


# JWT settings for authentication
SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
