from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional
import re


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    # Field constraint: priority must be 1–5
    priority: int = Field(default=3, ge=1, le=5)
    due_date: Optional[str] = None  # ISO-8601 YYYY-MM-DD text column
    status: str = Field(default="todo")
    project_id: int

    # Custom validator: ensure due_date matches YYYY-MM-DD if provided
    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            raise ValueError("due_date must be in YYYY-MM-DD format")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=300)
    description: Optional[str] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    due_date: Optional[str] = None
    status: Optional[str] = None

    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            raise ValueError("due_date must be in YYYY-MM-DD format")
        return v


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: int
    due_date: Optional[str]
    status: str
    project_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
