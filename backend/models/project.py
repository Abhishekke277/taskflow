from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from backend.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # Foreign key referencing users.id
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Many projects belong to one user
    owner = relationship("User", back_populates="projects")

    # One project contains many tasks
    tasks = relationship("Task", back_populates="project")