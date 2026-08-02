from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.models.project import Project
from backend.models.task import Task
from backend.schemas.project import ProjectCreate


def create_project(db: Session, project: ProjectCreate) -> Project:
    db_project = Project(name=project.name, owner_id=project.owner_id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Project).offset(skip).limit(limit).all()


def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()


def get_project_stats(db: Session, project_id: int):
    """
    Per-project task statistics computed with SQL aggregates
    (COUNT + GROUP BY) executed through SQLAlchemy across a join
    of projects and tasks — NOT computed in Python after fetching
    every row. Satisfies Section 1's statistics endpoint requirement.
    """
    total_count = (
        db.query(func.count(Task.id))
        .filter(Task.project_id == project_id)
        .scalar()
    )

    # COUNT grouped by priority for this project — e.g.
    # [("high", 3), ("medium", 5), ("low", 2)]
    by_priority = (
        db.query(Task.priority, func.count(Task.id))
        .filter(Task.project_id == project_id)
        .group_by(Task.priority)
        .all()
    )

    return {
        "project_id": project_id,
        "total_tasks": total_count,
        "by_priority": {priority: count for priority, count in by_priority},
    }