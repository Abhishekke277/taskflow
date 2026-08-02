"""
Seed script — populates the database with sample data for benchmarking.

Usage:
    python -m backend.scripts.seed --tasks 500

Sizes: 10 (smoke), 500 (default), 3000 (large benchmark)
"""

import argparse
import random
import sys
from datetime import date, timedelta

# Ensure the project root is on the path when run directly
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.database import SessionLocal, Base, engine
from backend.models import user, project, task  # noqa: F401 — registers models with Base

Base.metadata.create_all(bind=engine)

STATUSES = ["todo", "in_progress", "done"]
PRIORITIES = [1, 2, 3, 4, 5]
ADJECTIVES = ["urgent", "routine", "deferred", "critical", "optional"]
NOUNS = ["report", "review", "meeting", "deployment", "fix", "refactor", "test", "update"]


def random_due_date() -> str:
    today = date.today()
    delta = random.randint(-30, 60)
    return (today + timedelta(days=delta)).isoformat()


def seed(num_tasks: int = 500) -> None:
    db = SessionLocal()
    try:
        # Create one demo user and one demo project
        demo_user = user.User(name="Demo User", email="demo@taskflow.dev")
        db.add(demo_user)
        db.flush()

        demo_project = project.Project(
            name="Benchmark Project",
            description=f"Auto-seeded with {num_tasks} tasks",
            owner_id=demo_user.id,
        )
        db.add(demo_project)
        db.flush()

        tasks = [
            task.Task(
                title=f"{random.choice(ADJECTIVES).capitalize()} {random.choice(NOUNS)} #{i}",
                description=f"Auto-generated task number {i}",
                priority=random.choice(PRIORITIES),
                due_date=random_due_date(),
                status=random.choice(STATUSES),
                project_id=demo_project.id,
            )
            for i in range(1, num_tasks + 1)
        ]

        db.bulk_save_objects(tasks)
        db.commit()
        print(f"Seeded {num_tasks} tasks into project '{demo_project.name}' (id={demo_project.id})")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed TaskFlow database")
    parser.add_argument("--tasks", type=int, default=500, choices=[10, 500, 3000])
    args = parser.parse_args()
    seed(args.tasks)
