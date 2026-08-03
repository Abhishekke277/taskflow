from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.quick_add import QuickAddRequest
from backend.schemas.task import TaskResponse
from backend.ai.prompt import build_quick_add_prompt
from backend.ai.mock_parser import parse_task_description
from backend.crud import project as project_crud
from backend.models.task import Task
from backend.config import USE_REAL_LLM, GROK_API_KEY

router = APIRouter(prefix="/tasks", tags=["ai-quick-add"])


@router.post("/quick-add", response_model=TaskResponse, status_code=201)
def quick_add_task(payload: QuickAddRequest, db: Session = Depends(get_db)):
    """
    Accepts free-text description + project_id, parses it into
    structured fields, and creates a real task row.

    Uses the deterministic mock parser by default (required, keyless
    path). If USE_REAL_LLM=true and a Grok API key is present, uses
    the real LLM instead — which internally falls back to the mock
    automatically on any failure, so this endpoint always succeeds
    via one path or the other.
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

    if USE_REAL_LLM and GROK_API_KEY:
        # llm_parser.parse_with_real_llm already falls back to the
        # mock internally on any error, so this call never raises
        from backend.ai.llm_parser import parse_with_real_llm
        parsed = parse_with_real_llm(payload.description)
    else:
        # Default, required, keyless path
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