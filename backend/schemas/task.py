from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TaskCreate(BaseModel):
    title: str
    # Field constraint: priority must be exactly one of these three values
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    due_date: Optional[str] = None
    project_id: int

    # Custom validator: rejects a blank/whitespace-only title
    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("title cannot be blank")
        return stripped


class TaskUpdate(BaseModel):
    # All fields optional here, since a PATCH/PUT may update
    # only some fields at a time
    title: Optional[str] = None
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|high)$")
    due_date: Optional[str] = None
    completed: Optional[bool] = None   # ← ye add karein

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        stripped = value.strip()
        if not stripped:
            raise ValueError("title cannot be blank")
        return stripped


class TaskResponse(BaseModel):
    id: int
    title: str
    priority: str
    due_date: Optional[str] = None
    completed: bool = False   # ← for complte tasks
    project_id: int

    class Config:
        from_attributes = True