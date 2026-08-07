from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import Base, engine
from backend import models  # noqa: F401
from backend.routers import users, projects, tasks
from backend.middleware.logging_middleware import LoggingMiddleware
from backend.algorithms.routes import router as algorithms_router
from backend.routers import users, projects, tasks, quick_add
from backend.routers import users, projects, tasks, quick_add, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow API")

# ── Custom logging middleware (Task 7) ──
app.add_middleware(LoggingMiddleware)

# ── CORS configuration (Task 8) ──
# Update this origin to match wherever your frontend actually runs.
# If you serve frontend/ with VS Code Live Server or a static server
# on port 5500, this is correct. Change the port if yours differs.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(algorithms_router)
app.include_router(quick_add.router)
app.include_router(auth.router)



@app.get("/")
def root():
    return {"message": "TaskFlow API is running"}