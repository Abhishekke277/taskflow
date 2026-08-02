from fastapi import FastAPI
from backend.database import Base, engine
from backend import models  # noqa: F401 — ensures all models are registered

# Creates all tables (users, projects, tasks) in the connected database
# if they don't already exist. Safe to run every startup — it won't
# drop or duplicate existing tables.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow API")


@app.get("/")
def root():
    return {"message": "TaskFlow API is running"}