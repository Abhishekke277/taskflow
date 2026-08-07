from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from backend.crud import task as task_crud
from backend.crud import project as project_crud
from backend.algorithms.sorting import insertion_sort
from backend.algorithms.searching import binary_search, linear_search
from backend.models.user import User
from backend.auth.dependencies import get_current_user
import re

router = APIRouter(prefix="/tasks", tags=["tasks"])

PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


def due_date_sort_key(due_date_value):
    if due_date_value is None:
        return (2, 0)
    text = due_date_value.strip().lower()
    if text == "today":
        return (0, 0)
    if text == "tomorrow":
        return (0, 1)
    match = re.match(r"^\.?\d+(\.\d+)?", text)
    if match:
        return (0, float(match.group()))
    return (1, text)


def _verify_project_ownership(db: Session, project_id: int, current_user: User):
    """Raises 422/403 if project_id doesn't exist or isn't the user's."""
    project = project_crud.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=422, detail=f"project_id {project_id} does not reference an existing project")
    if project.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your project")


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _verify_project_ownership(db, task.project_id, current_user)
    return task_crud.create_task(db, task)


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    sort: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tasks = task_crud.get_tasks_for_owner(db, owner_id=current_user.id, skip=skip, limit=limit)

    if sort not in ("priority", "due_date", None):
        raise HTTPException(status_code=422, detail="sort must be either 'priority' or 'due_date'")

    if sort is None:
        return tasks

    task_dicts = [
        {"id": t.id, "title": t.title, "priority": t.priority, "due_date": t.due_date, "project_id": t.project_id}
        for t in tasks
    ]

    if sort == "priority":
        for t in task_dicts:
            t["_priority_rank"] = PRIORITY_RANK.get(t["priority"], 0)
        insertion_sort(task_dicts, key="_priority_rank")
        for t in task_dicts:
            del t["_priority_rank"]
    else:
        for t in task_dicts:
            t["_due_date_sort_key"] = due_date_sort_key(t["due_date"])
        insertion_sort(task_dicts, key="_due_date_sort_key")
        for t in task_dicts:
            del t["_due_date_sort_key"]

    return task_dicts


@router.get("/search")
def search_tasks(
    title: str = Query(...),
    algo: str = Query(default="binary"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if algo not in ("binary", "linear"):
        raise HTTPException(status_code=422, detail="algo must be either 'binary' or 'linear'")

    tasks = task_crud.get_tasks_for_owner(db, owner_id=current_user.id, skip=0, limit=1000000)
    index = [{"id": t.id, "title": t.title} for t in tasks]

    if algo == "binary":
        insertion_sort(index, key="title")
        found_position = binary_search(index, title, key="title")
    else:
        found_position = linear_search(index, title, key="title")

    if found_position == -1:
        raise HTTPException(status_code=404, detail="No task found with that exact title")

    matched_id = index[found_position]["id"]
    matched_task = task_crud.get_task_by_id_for_owner(db, matched_id, current_user.id)

    return {
        "id": matched_task.id, "title": matched_task.title, "priority": matched_task.priority,
        "due_date": matched_task.due_date, "project_id": matched_task.project_id,
    }


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = task_crud.get_task_by_id_for_owner(db, task_id, current_user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = task_crud.get_task_by_id_for_owner(db, task_id, current_user.id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_crud.update_task(db, task_id, task_update)


@router.delete("/{task_id}", status_code=200)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = task_crud.get_task_by_id_for_owner(db, task_id, current_user.id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Task not found")
    task_crud.delete_task(db, task_id)
    return {"message": "Task deleted", "id": task_id}