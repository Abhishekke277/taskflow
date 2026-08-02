# Import all models here so Base.metadata knows about every table
# before create_all() is called in main.py
from backend.models.user import User
from backend.models.project import Project
from backend.models.task import Task