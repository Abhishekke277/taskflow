from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from backend.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    # Closed set: "low" / "medium" / "high" — same values the
    # Section 3 AI parser produces. Enforced at the DB level with
    # a CheckConstraint, not just in Pydantic.
    priority = Column(String, nullable=False, default="medium")

    # Nullable, stored as raw text on purpose — holds either a
    # manually entered date OR a parsed phrase like "next friday"
    due_date = Column(String, nullable=True)

    # Foreign key referencing projects.id
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Many tasks belong to one project
    project = relationship("Project", back_populates="tasks")

    __table_args__ = (
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="check_priority_valid"
        ),
    )