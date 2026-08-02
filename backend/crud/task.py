from sqlalchemy.orm import Session

from backend.models.task import Task
from backend.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, task_in: TaskCreate) -> Task:
    db_task = Task(**task_in.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()


def list_tasks(
    db: Session,
    project_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Task]:
    q = db.query(Task)
    if project_id is not None:
        q = q.filter(Task.project_id == project_id)
    return q.offset(skip).limit(limit).all()


def update_task(db: Session, task_id: int, task_in: TaskUpdate) -> Task | None:
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True
