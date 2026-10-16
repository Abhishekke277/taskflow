"""
Test configuration — shared fixtures for the entire test suite.

Strategy
--------
* Use an **in-memory SQLite** database so tests never touch the real
  Supabase / PostgreSQL instance.
* Override FastAPI's `get_db` dependency so every request the
  TestClient makes receives a session bound to the SQLite engine.
* Create all tables before the first test and drop them after the last,
  giving each test function a clean slate via a per-test transaction
  rollback.

Important notes on the app's own code
--------------------------------------
* `database.py` creates the SQLAlchemy engine at import time using the
  real DATABASE_URL from .env.  We do NOT patch that module; instead we
  let it create its own engine and we layer our override on top through
  `app.dependency_overrides`.
* `main.py` calls `Base.metadata.create_all(bind=engine)` on the
  production engine at import time.  We call `create_all` again on our
  test engine inside the session-scoped `setup_database` fixture so the
  SQLite schema is always present before any test runs.
* `Task.CheckConstraint` for priority is defined at the ORM level.
  SQLite does not enforce CHECK constraints by default, but that is fine
  because Pydantic validates the priority field before it ever reaches
  the database.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Import the FastAPI app and the dependency we need to override.
from backend.main import app
from backend.database import Base, get_db

# ---------------------------------------------------------------------------
# In-memory SQLite engine — completely isolated from the real database.
# `check_same_thread=False` is required when SQLite is used with FastAPI's
# sync dependency injection (multiple threads may share the same connection).
# ---------------------------------------------------------------------------
SQLITE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# ---------------------------------------------------------------------------
# Session-scoped fixture: create all tables once before any test in the
# session runs, and drop them all afterwards.
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create the full schema on the in-memory SQLite engine."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


# ---------------------------------------------------------------------------
# Function-scoped fixture: wrap each test in a transaction that is rolled
# back after the test, so every test starts with an empty database.
# ---------------------------------------------------------------------------
@pytest.fixture()
def db_session():
    """
    Yields a SQLAlchemy Session whose changes are rolled back after each
    test, guaranteeing test isolation without recreating the schema.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


# ---------------------------------------------------------------------------
# Override `get_db` so every TestClient request uses the test session.
# ---------------------------------------------------------------------------
@pytest.fixture()
def client(db_session):
    """
    Returns a FastAPI TestClient whose database dependency is wired to
    the isolated per-test SQLite session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # rollback is handled by the db_session fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Convenience helpers used by multiple test functions.
# ---------------------------------------------------------------------------

def register_user(client, *, name="Alice", email="alice@example.com", password="secret123"):
    """Register a user and return the full JSON response body."""
    resp = client.post("/auth/register", json={
        "name": name,
        "email": email,
        "password": password,
    })
    return resp


def login_user(client, *, email="alice@example.com", password="secret123"):
    """Log in an existing user and return the full JSON response body."""
    resp = client.post("/auth/login", json={
        "email": email,
        "password": password,
    })
    return resp


def auth_headers(token: str) -> dict:
    """Build the Authorization header dict from a JWT string."""
    return {"Authorization": f"Bearer {token}"}


def create_project(client, token: str, *, name="Test Project") -> dict:
    """Create a project for the authenticated user and return its JSON."""
    resp = client.post(
        "/projects/",
        json={"name": name},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def create_task(client, token: str, project_id: int, *, title="Buy milk") -> dict:
    """Create a task and return its JSON."""
    resp = client.post(
        "/tasks/",
        json={
            "title": title,
            "priority": "medium",
            "due_date": "tomorrow",
            "project_id": project_id,
        },
        headers=auth_headers(token),
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
