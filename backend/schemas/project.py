from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    owner_id: int


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectStats(BaseModel):
    project_id: int
    total_tasks: int
    by_status: dict[str, int]
    by_priority: dict[int, int]
