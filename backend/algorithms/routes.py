from fastapi import APIRouter, Depends, HTTPException, Query #Query is used to define query parameters for the endpoint
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.task import Task
from backend.algorithms.sorting import insertion_sort
from backend.algorithms.searching import binary_search, linear_search

router = APIRouter(tags=["algorithms"])

# Maps priority strings to comparable numeric ranks for sorting
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


@router.get("/tasks/sort")
def sort_tasks(sort: str = Query(default="priority"), db: Session = Depends(get_db)):
    """
    Fetches all tasks from the database, converts them to a list of
    dicts, then sorts them using our own insertion_sort — never
    Python's built-in sorted()/list.sort() and never the database's
    ORDER BY. Supports sort=priority and sort=due_date.
    """
    if sort not in ("priority", "due_date"):
        raise HTTPException(
            status_code=422,
            detail="sort must be either 'priority' or 'due_date'"
        )

    tasks = db.query(Task).all()

    # Convert SQLAlchemy objects into plain dicts, since insertion_sort
    # operates on dictionaries, not ORM model instances
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
        for task in task_dicts:
            task["_priority_rank"] = PRIORITY_RANK.get(task["priority"], 0)#this line adds a temporary key "_priority_rank" to each task dictionary, which holds the numeric rank corresponding to the task's priority. This allows for easier comparison during sorting.
        insertion_sort(task_dicts, key="_priority_rank")
        # Remove the helper key before returning
        for task in task_dicts:
            del task["_priority_rank"]
    else:
        # sort == "due_date" — sorts by the raw text value directly
        insertion_sort(task_dicts, key="due_date")

    return task_dicts


@router.get("/tasks/search")
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
    """
    if algo not in ("binary", "linear"):
        raise HTTPException(
            status_code=422,
            detail="algo must be either 'binary' or 'linear'"
        )

    tasks = db.query(Task).all()
    index = [{"id": t.id, "title": t.title} for t in tasks]

    if algo == "binary":
        insertion_sort(index, key="title")
        found_position = binary_search(index, title, key="title")
    else:
        found_position = linear_search(index, title, key="title")

    if found_position == -1:
        raise HTTPException(status_code=404, detail="No task found with that exact title")

    matched_id = index[found_position]["id"]
    matched_task = db.query(Task).filter(Task.id == matched_id).first()

    return {
        "id": matched_task.id,
        "title": matched_task.title,
        "priority": matched_task.priority,
        "due_date": matched_task.due_date,
        "project_id": matched_task.project_id,
    }