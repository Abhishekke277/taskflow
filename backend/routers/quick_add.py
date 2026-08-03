from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.quick_add import QuickAddRequest
from backend.schemas.task import TaskResponse
from backend.ai.prompt import build_quick_add_prompt
from backend.ai.mock_parser import parse_task_description
from backend.crud import project as project_crud
from backend.models.task import Task

router = APIRouter(prefix="/tasks", tags=["ai-quick-add"])


@router.post("/quick-add", response_model=TaskResponse, status_code=201)
def quick_add_task(payload: QuickAddRequest, db: Session = Depends(get_db)):
    """
    Accepts free-text description + project_id, parses it into
    structured fields using the mock parser (or optionally a real
    LLM behind a feature flag), and creates a real task row.
    """
    # Validate project_id references an existing project
    project = project_crud.get_project_by_id(db, payload.project_id)
    if project is None:
        raise HTTPException(
            status_code=422,
            detail=f"project_id {payload.project_id} does not reference an existing project"
        )

    # Build the role-based prompt (system + user messages) — used
    # even though the mock parser is what actually answers it, to
    # keep the code structured the same way a real LLM call would be
    prompt = build_quick_add_prompt(payload.description)

    # Parse using the deterministic mock (default, keyless path)
    parsed = parse_task_description(prompt["user"])

    # Validate the parsed object against TaskResponse-compatible
    # fields before writing to the database
    try:
        db_task = Task(
            title=parsed["title"],
            priority=parsed["priority"],
            due_date=parsed["due_date_hint"],
            project_id=payload.project_id,
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=f"Failed to create task: {str(e)}")

    return db_task