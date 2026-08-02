from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from backend.crud import task as task_crud
from backend.algorithms.sorting import insertion_sort
from backend.algorithms.searching import binary_search, linear_search

router = APIRouter(prefix="/tasks", tags=["tasks"])

# Maps priority strings to comparable numeric ranks for sorting
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return task_crud.create_task(db, task)


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    sort: Optional[str] = Query(default=None, description="Sort by 'priority' or 'due_date'"),
    db: Session = Depends(get_db),
):
    """
    Lists tasks. If ?sort=priority or ?sort=due_date is provided,
    the results are sorted using our own insertion_sort — never
    Python's built-in sorted()/list.sort(), never the database's
    ORDER BY. Without ?sort=, returns tasks in default DB order.
    """
    tasks = task_crud.get_tasks(db, skip, limit)

    if sort not in ("priority", "due_date", None):
        raise HTTPException(
            status_code=422,
            detail="sort must be either 'priority' or 'due_date'"
        )

    if sort is None:
        return tasks

    # Convert ORM objects to plain dicts — insertion_sort operates
    # on dictionaries, not SQLAlchemy model instances
    task_dicts = [
        {
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "due_date": t.due_date,
            "project_id": t.project_id,
        }
        for t in tasks
    ]

    if sort == "priority":
        # Map priority string to a comparable numeric rank before sorting
        for t in task_dicts:
            t["_priority_rank"] = PRIORITY_RANK.get(t["priority"], 0)
        insertion_sort(task_dicts, key="_priority_rank")
        for t in task_dicts:
            del t["_priority_rank"]
    else:
        # sort == "due_date" — sorts by the raw text value directly
        insertion_sort(task_dicts, key="due_date")

    return task_dicts


@router.get("/search")
def search_tasks(
    title: str = Query(...),
    algo: str = Query(default="binary"),
    db: Session = Depends(get_db),
):
    """
    Builds an in-memory index of {"id", "title"} pairs from the real
    tasks in the database, then locates the exact-title match using
    binary_search (after sorting the index with insertion_sort) when
    algo=binary, or linear_search over the unsorted index when
    algo=linear. Returns the matching task (200) or 404.

    IMPORTANT: this route must be defined before GET /{task_id},
    otherwise FastAPI would treat "search" as a task_id value.
    """
    if algo not in ("binary", "linear"):
        raise HTTPException(
            status_code=422,
            detail="algo must be either 'binary' or 'linear'"
        )

    tasks = task_crud.get_tasks(db, skip=0, limit=1000000)
    index = [{"id": t.id, "title": t.title} for t in tasks]

    if algo == "binary":
        insertion_sort(index, key="title")
        found_position = binary_search(index, title, key="title")
    else:
        found_position = linear_search(index, title, key="title")

    if found_position == -1:
        raise HTTPException(status_code=404, detail="No task found with that exact title")

    matched_id = index[found_position]["id"]
    matched_task = task_crud.get_task_by_id(db, matched_id)

    return {
        "id": matched_task.id,
        "title": matched_task.title,
        "priority": matched_task.priority,
        "due_date": matched_task.due_date,
        "project_id": matched_task.project_id,
    }


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = task_crud.get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = task_crud.update_task(db, task_id, task_update)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=200)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = task_crud.delete_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted", "id": task_id}