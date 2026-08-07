from sqlalchemy.orm import Session
from backend.models.task import Task
from backend.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, task: TaskCreate) -> Task:
    db_task = Task(
        title=task.title,
        priority=task.priority,
        due_date=task.due_date,
        project_id=task.project_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task) # Updating the object to retrieve the latest data from the database, including any auto-generated fields like the primary key (id).
    return db_task


def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Task).offset(skip).limit(limit).all()


def get_task_by_id(db: Session, task_id: int):
    return db.query(Task).filter(Task.id == task_id).first()


def update_task(db: Session, task_id: int, task_update: TaskUpdate):
    db_task = get_task_by_id(db, task_id)
    if db_task is None:
        return None

    # Only update fields the client actually sent (exclude_unset=True
    # skips fields left as None/default in the request body)
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_task, field, value) #setattr is a built-in Python function that sets the value of an attribute of an object. In this case, it updates the fields of the db_task object with the new values provided in update_data.

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int):
    db_task = get_task_by_id(db, task_id)
    if db_task is None:
        return None
    db.delete(db_task)
    db.commit()
    return db_task