from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from backend.database import get_db
from backend.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from backend.schemas.quick_add import QuickAddRequest, QuickAddResponse
from backend.crud import task as crud_task
from backend.algorithms.sorting import insertion_sort
from backend.algorithms.searching import binary_search, linear_search
from backend.config import USE_REAL_LLM

router = APIRouter()


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    return crud_task.create_task(db, task_in)


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    project_id: Optional[int] = Query(default=None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud_task.list_tasks(db, project_id=project_id, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud_task.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    task = crud_task.update_task(db, task_id, task_in)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    deleted = crud_task.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found.")


# ---------------------------------------------------------------------------
# Sort endpoint  (Section 2)
# ---------------------------------------------------------------------------

@router.get("/sort/results", response_model=list[TaskResponse])
def sort_tasks(
    project_id: Optional[int] = Query(default=None),
    sort_by: str = Query(default="priority", description="Field to sort by: priority | due_date | title"),
    reverse: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    tasks = crud_task.list_tasks(db, project_id=project_id, limit=10_000)
    # Convert ORM objects to dicts for the algorithm layer
    task_dicts = [
        {
            "id": t.id, "title": t.title, "description": t.description,
            "priority": t.priority, "due_date": t.due_date or "",
            "status": t.status, "project_id": t.project_id,
            "created_at": t.created_at, "updated_at": t.updated_at,
        }
        for t in tasks
    ]
    sorted_dicts = insertion_sort(task_dicts, key=sort_by, reverse=reverse)
    # Re-fetch ORM objects in sorted order by id for response_model compatibility
    id_order = {d["id"]: idx for idx, d in enumerate(sorted_dicts)}
    return sorted(tasks, key=lambda t: id_order[t.id])


# ---------------------------------------------------------------------------
# Search endpoint  (Section 2)
# ---------------------------------------------------------------------------

@router.get("/search/results", response_model=list[TaskResponse])
def search_tasks(
    q: str = Query(..., description="Search term"),
    project_id: Optional[int] = Query(default=None),
    method: str = Query(default="linear", description="Search method: binary | linear"),
    db: Session = Depends(get_db),
):
    tasks = crud_task.list_tasks(db, project_id=project_id, limit=10_000)
    task_dicts = [
        {
            "id": t.id, "title": t.title, "description": t.description,
            "priority": t.priority, "due_date": t.due_date or "",
            "status": t.status, "project_id": t.project_id,
            "created_at": t.created_at, "updated_at": t.updated_at,
        }
        for t in tasks
    ]

    if method == "binary":
        # Binary search requires sorted list + exact match
        sorted_dicts = insertion_sort(task_dicts, key="title")
        idx = binary_search(sorted_dicts, q, key="title")
        matched_ids = {sorted_dicts[idx]["id"]} if idx != -1 else set()
    else:
        # Linear search with substring support
        indices = linear_search(task_dicts, q, key="title", substring=True)
        matched_ids = {task_dicts[i]["id"] for i in indices}

    return [t for t in tasks if t.id in matched_ids]


# ---------------------------------------------------------------------------
# Quick-add endpoint  (Section 3)
# ---------------------------------------------------------------------------

@router.post("/quick-add", response_model=QuickAddResponse, status_code=status.HTTP_201_CREATED)
def quick_add_task(payload: QuickAddRequest, db: Session = Depends(get_db)):
    if USE_REAL_LLM:
        from backend.ai import llm_parser
        parsed = llm_parser.parse(payload.text)
        parser_used = "llm"
    else:
        from backend.ai import mock_parser
        parsed = mock_parser.parse(payload.text)
        parser_used = "mock"

    task_in = TaskCreate(
        title=parsed["title"],
        description=parsed.get("description"),
        priority=parsed.get("priority", 3),
        due_date=parsed.get("due_date"),
        status=parsed.get("status", "todo"),
        project_id=payload.project_id,
    )
    db_task = crud_task.create_task(db, task_in)

    return QuickAddResponse(
        title=db_task.title,
        description=db_task.description,
        priority=db_task.priority,
        due_date=db_task.due_date,
        status=db_task.status,
        project_id=db_task.project_id,
        parser_used=parser_used,
    )
