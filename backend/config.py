import os

# Database
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")

# Feature flags
USE_REAL_LLM: bool = os.getenv("USE_REAL_LLM", "false").lower() == "true"

# If USE_REAL_LLM is True, provide your API key via environment variable
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
