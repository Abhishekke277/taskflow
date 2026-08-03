from pydantic import BaseModel


class QuickAddRequest(BaseModel):
    """Free-text task description sent by the client, per Section 3."""
    description: str
    project_id: int