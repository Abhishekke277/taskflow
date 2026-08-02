from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.project import Project
from backend.models.task import Task
from backend.schemas.project import ProjectCreate, ProjectStats


def create_project(db: Session, project_in: ProjectCreate) -> Project:
    db_project = Project(
        name=project_in.name,
        description=project_in.description,
        owner_id=project_in.owner_id,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_project(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def list_projects(db: Session, skip: int = 0, limit: int = 100) -> list[Project]:
    return db.query(Project).offset(skip).limit(limit).all()


def get_project_stats(db: Session, project_id: int) -> ProjectStats:
    """
    Returns task counts grouped by status and by priority using
    COUNT + GROUP BY — a single round-trip per group.
    """
    # GROUP BY status
    status_rows = (
        db.query(Task.status, func.count(Task.id).label("cnt"))
        .filter(Task.project_id == project_id)
        .group_by(Task.status)
        .all()
    )

    # GROUP BY priority
    priority_rows = (
        db.query(Task.priority, func.count(Task.id).label("cnt"))
        .filter(Task.project_id == project_id)
        .group_by(Task.priority)
        .all()
    )

    by_status = {row.status: row.cnt for row in status_rows}
    by_priority = {row.priority: row.cnt for row in priority_rows}
    total = sum(by_status.values())

    return ProjectStats(
        project_id=project_id,
        total_tasks=total,
        by_status=by_status,
        by_priority=by_priority,
    )
