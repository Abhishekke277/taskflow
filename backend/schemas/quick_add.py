from pydantic import BaseModel
from typing import Optional


class QuickAddRequest(BaseModel):
    """Natural-language task description sent by the client."""
    text: str
    project_id: int


class QuickAddResponse(BaseModel):
    """Parsed task fields returned before (or after) DB insertion."""
    title: str
    description: Optional[str] = None
    priority: int = 3
    due_date: Optional[str] = None
    status: str = "todo"
    project_id: int
    # Indicates whether the real LLM or the mock parser was used
    parser_used: str = "mock"
