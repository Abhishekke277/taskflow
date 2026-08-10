from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.quick_add import QuickAddRequest
from backend.schemas.task import TaskResponse
from backend.ai.prompt import build_quick_add_prompt
from backend.ai.mock_parser import parse_task_description
from backend.crud import project as project_crud
from backend.models.task import Task
from backend.models.user import User
from backend.auth.dependencies import get_current_user
from backend.config import USE_REAL_LLM, GROQ_API_KEY

router = APIRouter(prefix="/tasks", tags=["ai-quick-add"])


@router.post("/quick-add", response_model=TaskResponse, status_code=201)
def quick_add_task(
    payload: QuickAddRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_crud.get_project_by_id(db, payload.project_id)
    if project is None:
        raise HTTPException(status_code=422, detail=f"project_id {payload.project_id} does not reference an existing project")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your project")

    prompt = build_quick_add_prompt(payload.description)

    if USE_REAL_LLM and GROQ_API_KEY:
        from backend.ai.llm_parser import parse_with_real_llm
        parsed = parse_with_real_llm(payload.description)
    else:
        parsed = parse_task_description(prompt["user"])

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