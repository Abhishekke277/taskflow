from fastapi import FastAPI
from backend.database import Base, engine
from backend import models  # noqa: F401 — ensures all models are registered
from backend.routers import users, projects, tasks

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow API")

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)


@app.get("/")
def root():
    return {"message": "TaskFlow API is running"}