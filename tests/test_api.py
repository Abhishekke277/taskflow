"""
API test suite for TaskFlow.

Covers
------
1.  POST /auth/register  — happy path
2.  POST /auth/register  — duplicate email → 409
3.  POST /auth/login     — happy path
4.  POST /auth/login     — wrong password → 401
5.  POST /auth/login     — unregistered email → 401
6.  POST /tasks/         — create task with valid token → 201
7.  POST /tasks/         — create task without token → 403
8.  GET  /tasks/         — list tasks, only own tasks returned
9.  GET  /tasks/{id}     — user A cannot read user B's task → 404
10. PUT  /tasks/{id}     — update task fields
11. PUT  /tasks/{id}     — mark task completed
12. PUT  /tasks/{id}     — user A cannot update user B's task → 404
13. DELETE /tasks/{id}   — delete own task → 200
14. DELETE /tasks/{id}   — user A cannot delete user B's task → 404

All tests use an in-memory SQLite database (see conftest.py).
The real Supabase/PostgreSQL database is never contacted.
"""

import pytest

# All helpers live in conftest.py and are injected by pytest automatically
# (register_user, login_user, auth_headers, create_project, create_task).
from tests.conftest import (
    register_user,
    login_user,
    auth_headers,
    create_project,
    create_task,
)


# ===========================================================================
# 1. Registration — happy path
# ===========================================================================

class TestRegister:

    def test_register_returns_201_and_token(self, client):
        resp = register_user(client)
        assert resp.status_code == 201
        body = resp.json()
        # TokenResponse shape: access_token, token_type, user_id, name, email
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert body["name"] == "Alice"
        assert body["email"] == "alice@example.com"
        assert isinstance(body["user_id"], int)

    def test_register_token_is_non_empty_string(self, client):
        resp = register_user(client)
        token = resp.json()["access_token"]
        assert isinstance(token, str)
        assert len(token) > 20  # a real JWT is always longer than this

    def test_register_duplicate_email_returns_409(self, client):
        register_user(client)  # first registration succeeds
        resp = register_user(client)  # same email again
        assert resp.status_code == 409
        assert "already exists" in resp.json()["detail"].lower()


# ===========================================================================
# 2. Login
# ===========================================================================

class TestLogin:

    def test_login_happy_path(self, client):
        register_user(client)
        resp = login_user(client)
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["email"] == "alice@example.com"

    def test_login_wrong_password_returns_401(self, client):
        register_user(client)
        resp = login_user(client, password="WRONG_PASSWORD")
        assert resp.status_code == 401
        # The error message must NOT distinguish "wrong password" from
        # "no such user" — that would be an email-enumeration leak.
        assert "incorrect" in resp.json()["detail"].lower()

    def test_login_unknown_email_returns_401(self, client):
        # No registration — the email doesn't exist at all
        resp = login_user(client, email="nobody@example.com")
        assert resp.status_code == 401
        assert "incorrect" in resp.json()["detail"].lower()

    def test_login_wrong_password_same_message_as_unknown_email(self, client):
        """
        Security property: the error message for wrong-password must be
        identical to the message for unknown-email so attackers cannot
        enumerate registered addresses.
        """
        register_user(client)
        wrong_pw = login_user(client, password="WRONG").json()["detail"]
        no_user = login_user(client, email="ghost@x.com").json()["detail"]
        assert wrong_pw == no_user


# ===========================================================================
# 3. Task creation
# ===========================================================================

class TestCreateTask:

    def test_create_task_with_valid_token_returns_201(self, client):
        token = register_user(client).json()["access_token"]
        project = create_project(client, token)
        resp = client.post(
            "/tasks/",
            json={
                "title": "Buy milk",
                "priority": "high",
                "due_date": "tomorrow",
                "project_id": project["id"],
            },
            headers=auth_headers(token),
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["title"] == "Buy milk"
        assert body["priority"] == "high"
        assert body["due_date"] == "tomorrow"
        assert body["completed"] is False
        assert body["project_id"] == project["id"]
        assert isinstance(body["id"], int)

    def test_create_task_without_token_is_rejected(self, client):
        """
        FastAPI's HTTPBearer rejects requests without an Authorization
        header.  Depending on the installed version of fastapi/starlette
        this is either 401 or 403 — we assert on the family (4xx) and
        that it is NOT 200/201.
        """
        resp = client.post(
            "/tasks/",
            json={
                "title": "Should fail",
                "priority": "low",
                "project_id": 1,
            },
            # No Authorization header
        )
        assert resp.status_code in (401, 403)

    def test_create_task_with_invalid_token_returns_401(self, client):
        resp = client.post(
            "/tasks/",
            json={"title": "x", "priority": "low", "project_id": 1},
            headers={"Authorization": "Bearer this.is.not.a.real.token"},
        )
        assert resp.status_code == 401

    def test_create_task_with_invalid_priority_returns_422(self, client):
        token = register_user(client).json()["access_token"]
        project = create_project(client, token)
        resp = client.post(
            "/tasks/",
            json={
                "title": "Bad priority",
                "priority": "critical",   # not in low/medium/high
                "project_id": project["id"],
            },
            headers=auth_headers(token),
        )
        assert resp.status_code == 422

    def test_create_task_with_blank_title_returns_422(self, client):
        token = register_user(client).json()["access_token"]
        project = create_project(client, token)
        resp = client.post(
            "/tasks/",
            json={
                "title": "   ",   # whitespace-only, rejected by @field_validator
                "priority": "low",
                "project_id": project["id"],
            },
            headers=auth_headers(token),
        )
        assert resp.status_code == 422

    def test_create_task_for_nonexistent_project_returns_422(self, client):
        token = register_user(client).json()["access_token"]
        resp = client.post(
            "/tasks/",
            json={
                "title": "Orphan task",
                "priority": "low",
                "project_id": 99999,   # does not exist
            },
            headers=auth_headers(token),
        )
        # _verify_project_ownership raises 422 for a missing project
        assert resp.status_code == 422


# ===========================================================================
# 4. Cross-user isolation — user A cannot access user B's task
# ===========================================================================

class TestCrossUserIsolation:
    """
    The ownership check in crud/task.py (get_task_by_id_for_owner) JOINs
    tasks with projects and filters by project.owner_id.  When the task
    exists but belongs to another user, the query returns None and the
    router raises 404 — indistinguishable from "task doesn't exist".
    """

    def _setup_two_users(self, client):
        """Register two users, each with a project and a task."""
        token_a = register_user(
            client, name="Alice", email="alice@example.com"
        ).json()["access_token"]
        token_b = register_user(
            client, name="Bob", email="bob@example.com"
        ).json()["access_token"]

        project_a = create_project(client, token_a, name="Alice Project")
        project_b = create_project(client, token_b, name="Bob Project")

        task_a = create_task(client, token_a, project_a["id"], title="Alice task")
        task_b = create_task(client, token_b, project_b["id"], title="Bob task")

        return token_a, token_b, task_a, task_b

    def test_user_a_cannot_read_user_b_task(self, client):
        token_a, token_b, task_a, task_b = self._setup_two_users(client)
        resp = client.get(
            f"/tasks/{task_b['id']}",
            headers=auth_headers(token_a),   # Alice tries to read Bob's task
        )
        assert resp.status_code == 404

    def test_user_b_cannot_read_user_a_task(self, client):
        token_a, token_b, task_a, task_b = self._setup_two_users(client)
        resp = client.get(
            f"/tasks/{task_a['id']}",
            headers=auth_headers(token_b),
        )
        assert resp.status_code == 404

    def test_list_tasks_only_returns_own_tasks(self, client):
        token_a, token_b, task_a, task_b = self._setup_two_users(client)

        resp_a = client.get("/tasks/", headers=auth_headers(token_a))
        assert resp_a.status_code == 200
        ids_a = {t["id"] for t in resp_a.json()}
        assert task_a["id"] in ids_a
        assert task_b["id"] not in ids_a   # Bob's task must NOT appear

        resp_b = client.get("/tasks/", headers=auth_headers(token_b))
        assert resp_b.status_code == 200
        ids_b = {t["id"] for t in resp_b.json()}
        assert task_b["id"] in ids_b
        assert task_a["id"] not in ids_b   # Alice's task must NOT appear

    def test_user_a_cannot_update_user_b_task(self, client):
        token_a, token_b, task_a, task_b = self._setup_two_users(client)
        resp = client.put(
            f"/tasks/{task_b['id']}",
            json={"title": "Hijacked"},
            headers=auth_headers(token_a),
        )
        assert resp.status_code == 404

    def test_user_a_cannot_delete_user_b_task(self, client):
        token_a, token_b, task_a, task_b = self._setup_two_users(client)
        resp = client.delete(
            f"/tasks/{task_b['id']}",
            headers=auth_headers(token_a),
        )
        assert resp.status_code == 404

        # Confirm Bob's task still exists
        still_there = client.get(
            f"/tasks/{task_b['id']}",
            headers=auth_headers(token_b),
        )
        assert still_there.status_code == 200


# ===========================================================================
# 5. Update task
# ===========================================================================

class TestUpdateTask:

    def _setup(self, client):
        token = register_user(client).json()["access_token"]
        project = create_project(client, token)
        task = create_task(client, token, project["id"])
        return token, task

    def test_update_title(self, client):
        token, task = self._setup(client)
        resp = client.put(
            f"/tasks/{task['id']}",
            json={"title": "Updated title"},
            headers=auth_headers(token),
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Updated title"

    def test_update_priority(self, client):
        token, task = self._setup(client)
        resp = client.put(
            f"/tasks/{task['id']}",
            json={"priority": "high"},
            headers=auth_headers(token),
        )
        assert resp.status_code == 200
        assert resp.json()["priority"] == "high"

    def test_update_due_date(self, client):
        token, task = self._setup(client)
        resp = client.put(
            f"/tasks/{task['id']}",
            json={"due_date": "next friday"},
            headers=auth_headers(token),
        )
        assert resp.status_code == 200
        assert resp.json()["due_date"] == "next friday"

    def test_mark_task_completed(self, client):
        token, task = self._setup(client)
        assert task["completed"] is False   # starts incomplete

        resp = client.put(
            f"/tasks/{task['id']}",
            json={"completed": True},
            headers=auth_headers(token),
        )
        assert resp.status_code == 200
        assert resp.json()["completed"] is True

    def test_undo_task_completion(self, client):
        token, task = self._setup(client)
        # Mark complete first
        client.put(
            f"/tasks/{task['id']}",
            json={"completed": True},
            headers=auth_headers(token),
        )
        # Now undo
        resp = client.put(
            f"/tasks/{task['id']}",
            json={"completed": False},
            headers=auth_headers(token),
        )
        assert resp.status_code == 200
        assert resp.json()["completed"] is False

    def test_partial_update_does_not_overwrite_other_fields(self, client):
        """
        The backend uses model_dump(exclude_unset=True).
        Sending only `completed` must leave title/priority/due_date intact.
        """
        token, task = self._setup(client)
        original_title = task["title"]
        original_priority = task["priority"]
        original_due_date = task["due_date"]

        resp = client.put(
            f"/tasks/{task['id']}",
            json={"completed": True},   # only this field sent
            headers=auth_headers(token),
        )
        body = resp.json()
        assert body["title"] == original_title
        assert body["priority"] == original_priority
        assert body["due_date"] == original_due_date

    def test_update_nonexistent_task_returns_404(self, client):
        token = register_user(client).json()["access_token"]
        resp = client.put(
            "/tasks/99999",
            json={"title": "Ghost"},
            headers=auth_headers(token),
        )
        assert resp.status_code == 404

    def test_update_task_without_token_is_rejected(self, client):
        resp = client.put("/tasks/1", json={"title": "x"})
        assert resp.status_code in (401, 403)


# ===========================================================================
# 6. Delete task
# ===========================================================================

class TestDeleteTask:

    def _setup(self, client):
        token = register_user(client).json()["access_token"]
        project = create_project(client, token)
        task = create_task(client, token, project["id"])
        return token, task

    def test_delete_own_task_returns_200(self, client):
        token, task = self._setup(client)
        resp = client.delete(
            f"/tasks/{task['id']}",
            headers=auth_headers(token),
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "Task deleted"
        assert body["id"] == task["id"]

    def test_deleted_task_is_gone(self, client):
        token, task = self._setup(client)
        client.delete(f"/tasks/{task['id']}", headers=auth_headers(token))

        resp = client.get(
            f"/tasks/{task['id']}",
            headers=auth_headers(token),
        )
        assert resp.status_code == 404

    def test_delete_nonexistent_task_returns_404(self, client):
        token = register_user(client).json()["access_token"]
        resp = client.delete(
            "/tasks/99999",
            headers=auth_headers(token),
        )
        assert resp.status_code == 404

    def test_delete_task_without_token_is_rejected(self, client):
        resp = client.delete("/tasks/1")
        assert resp.status_code in (401, 403)

    def test_delete_task_not_in_list_afterwards(self, client):
        """After deletion, GET /tasks/ must not include the deleted task."""
        token, task = self._setup(client)
        client.delete(f"/tasks/{task['id']}", headers=auth_headers(token))

        resp = client.get("/tasks/", headers=auth_headers(token))
        ids = [t["id"] for t in resp.json()]
        assert task["id"] not in ids
