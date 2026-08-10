# TaskFlow — Full-Stack Task Management Platform

An internal task-and-project management platform built for Blinkit's dark-store engineering pods. Combines a FastAPI + SQLAlchemy backend, a JWT-authenticated dashboard, a hand-rolled sorting/search engine, and an AI-assisted quick-add feature — all operating on the same three-table database (users, projects, tasks).

---

## Environment Setup

1. Clone the repository and navigate into it:
```bash
   git clone <my-repo-url>
   cd taskflow
```

2. Create and activate a virtual environment:
```bash
   python -m venv venv
   # Windows:
   venv\Scripts\Activate.ps1
   # macOS/Linux:
   source venv/bin/activate
```

3. Install dependencies:
```bash
   pip install -r requirements.txt
```

4. Create a `.env` file in the project root with:
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres
SECRET_KEY=your-random-secret-key-here-make-it-long-and-random
USE_REAL_LLM=false
GROK_API_KEY=

- `SECRET_KEY` signs and verifies JWT authentication tokens — any long random string works for local development.
   - `USE_REAL_LLM` / `GROK_API_KEY` are only needed for the **optional** real-LLM quick-add path — leave `USE_REAL_LLM=false` for normal/graded use, which requires zero API keys.

---

## Running the App (Two-Process Run)

**Terminal 1 — start the backend:**
```bash
uvicorn backend.main:app --reload
```
Runs on `http://127.0.0.1:8000`.

**Terminal 2 — start the frontend:**
```bash
cd frontend
python -m http.server 3000
```
Runs on `http://127.0.0.1:3000`. Open this URL in your browser.

The backend's CORS configuration (`backend/main.py`) allows requests from `http://127.0.0.1:3000` and `http://localhost:3000`. If you serve the frontend from a different port, update the `allow_origins` list in `main.py` to match.

---

## Database Schema

Three tables, defined as SQLAlchemy models in `backend/models/`:

**`users`**
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary Key |
| `name` | String | NOT NULL |
| `email` | String | NOT NULL, UNIQUE |
| `hashed_password` | String | NOT NULL — bcrypt hash, never stores plain text |

**`projects`**
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary Key |
| `name` | String | NOT NULL |
| `owner_id` | Integer | Foreign Key → `users.id` |

**`tasks`**
| Column | Type | Constraints |
|---|---|---|
| `id` | Integer | Primary Key |
| `title` | String | NOT NULL |
| `priority` | String | CHECK: `'low'` / `'medium'` / `'high'` |
| `due_date` | String | Nullable — stores raw text (manual dates *or* AI-parsed phrases like `"next friday"`) |
| `completed` | Boolean | NOT NULL, default `False` |
| `project_id` | Integer | Foreign Key → `projects.id` |

---

## Authentication

All `/projects/*` and `/tasks/*` endpoints (except registration/login) require a valid JWT sent in the request header:

Authorization: Bearer <access_token>

Tokens are obtained from `/auth/register` or `/auth/login` and are valid for 24 hours. `owner_id` on projects is derived automatically from the logged-in user's token — it is never sent in the request body, and a user can only see/modify their own projects and tasks (attempting to access another user's project returns `403 Forbidden`).

---

## API Endpoints

Base URL: `http://127.0.0.1:8000`

### Authentication

**Register** — `POST /auth/register`
```json
// Request
{ "name": "Priya Sharma", "email": "priya.test@blinkit.com", "password": "securepass123" }
// Response (201)
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 11,
  "name": "Priya Sharma",
  "email": "priya.test@blinkit.com"
}
// 409 if email already registered: { "detail": "An account with this email already exists." }
```

**Login** — `POST /auth/login`
```json
// Request
{ "email": "priya.test@blinkit.com", "password": "securepass123" }
// Response (200) — same shape as register
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 11,
  "name": "Priya Sharma",
  "email": "priya.test@blinkit.com"
}
// 401 on wrong email/password: { "detail": "Incorrect email or password." }
```

### Users *(legacy — direct user creation without authentication; the real app flow uses `/auth/register` instead)*

**Create user** — `POST /users/`
```json
// Request
{ "name": "Priya Sharma", "email": "priya@blinkit.com" }
// Response (201)
{ "id": 19, "name": "Priya Sharma", "email": "priya@blinkit.com" }
```

**List users** — `GET /users/`
```json
// Response (200)
[{ "id": 19, "name": "Priya Sharma", "email": "priya@blinkit.com" }]
```

### Projects
*(all require `Authorization: Bearer <token>`)*

**Create project** — `POST /projects/`
```json
// Request
{ "name": "Dark Store Ops" }
// Response (201) — owner_id is derived from the token, not sent by the client
{ "id": 5, "name": "Dark Store Ops", "owner_id": 11 }
```

**List projects** — `GET /projects/`
```json
// Response (200) — only returns projects owned by the logged-in user
[{ "id": 5, "name": "Dark Store Ops", "owner_id": 11 }]
```

**Get project by id** — `GET /projects/{id}`
```json
// Response (200)
{ "id": 5, "name": "Dark Store Ops", "owner_id": 11 }
// 404 if not found: { "detail": "Project not found" }
// 403 if it belongs to a different user: { "detail": "Not your project" }
```

**Project statistics** — `GET /projects/{id}/stats`
```json
// Response (200)
{ "project_id": 5, "total_tasks": 0, "by_priority": {} }
```

### Tasks
*(all require `Authorization: Bearer <token>`)*

**Create task** — `POST /tasks/`
```json
// Request
{ "title": "Restock shelves", "priority": "high", "due_date": "tomorrow", "project_id": 5 }
// Response (201)
{ "id": 26, "title": "Restock shelves", "priority": "high", "due_date": "tomorrow", "completed": false, "project_id": 5 }
```

**List tasks** — `GET /tasks/`
```json
// Response (200) — only returns tasks belonging to the logged-in user's projects
[{ "id": 26, "title": "Restock shelves", "priority": "high", "due_date": "tomorrow", "completed": false, "project_id": 5 }]
```

**Get task by id** — `GET /tasks/{id}`
```json
// Response (200)
{ "id": 26, "title": "Restock shelves", "priority": "high", "due_date": "tomorrow", "completed": false, "project_id": 5 }
// 404 if not found: { "detail": "Task not found" }
```

**Update task** — `PUT /tasks/{id}`
```json
// Request — supports partial updates, including marking complete/incomplete
{ "completed": true }
// Response (200)
{ "id": 26, "title": "Restock shelves", "priority": "high", "due_date": "tomorrow", "completed": true, "project_id": 5 }
```

**Delete task** — `DELETE /tasks/{id}`
```json
// Response (200)
{ "message": "Task deleted", "id": 26 }
```

**Sorted list (Section 2)** — `GET /tasks?sort=priority` (or `sort=due_date`)
```json
// Response (200) — sorted using our own insertion_sort, not built-in sort or ORDER BY
[
  { "id": 27, "title": "Update inventory", "priority": "low", "due_date": "next monday", "completed": false, "project_id": 5 },
  { "id": 26, "title": "Restock shelves", "priority": "high", "due_date": "tomorrow", "completed": true, "project_id": 5 }
]
// Note: for sort=due_date, completed tasks always sink to the bottom of the
// list regardless of their due date; sort=priority does not apply this rule.
```

**Search (Section 2)** — `GET /tasks/search?title=<exact title>&algo=binary|linear` (default: `binary`)
```json
// Response (200)
{ "id": 27, "title": "Update inventory", "priority": "low", "due_date": "next monday", "completed": false, "project_id": 5 }
// 404 if no exact match: { "detail": "No task found with that exact title" }
```

**AI Quick-Add (Section 3)** — `POST /tasks/quick-add`
```json
// Request
{ "description": "This is urgent, mark it ASAP please", "project_id": 5 }
// Response (201)
{ "id": 28, "title": "This is , mark it  please", "priority": "high", "due_date": null, "completed": false, "project_id": 5 }
// 422 if project_id doesn't exist or the body is malformed
// 403 if project_id belongs to a different user
```

---

## Section 2: Algorithm Complexity & Benchmark Analysis

**Time Complexity:**
- `insertion_sort`: Best case O(n) — already-sorted input. Worst case O(n²) — reverse-sorted input.
- `binary_search`: Best case O(1) — target found at the middle index immediately. Worst case O(log n).
- `linear_search`: Best case O(1) — target is the first element checked. Worst case O(n).

**Benchmark Results** (synthetic in-memory task data — title, priority, due_date fields):

| Size | insertion_sort comparisons | binary_search comparisons | linear_search comparisons |
|------|------------------------------|-----------------------------|------------------------------|
| 10 | 9 | 4 | 10 |
| 500 | 31259 | 9 | 500 |
| 3000 | 1820009 | 12 | 3000 |

**Is sorting-first worth it?**

Our benchmark confirms the theoretical complexity: sorting 3,000 tasks with `insertion_sort` took 1,820,009 comparisons, while searching that same sorted list with `binary_search` took only 12 comparisons — versus 3,000 comparisons for `linear_search` on unsorted data. Given TaskFlow's real usage pattern — a team listing/sorting tasks repeatedly throughout the day, while adding or renaming tasks comparatively rarely — paying the steep one-time O(n²) sorting cost is justified whenever the sorted list can be reused across multiple reads, since each subsequent binary search stays near-constant even as the dataset grows into the thousands. However, if `GET /tasks?sort=...` re-sorts from scratch on every single request without caching, the O(n²) cost is paid repeatedly, and at 3,000+ tasks this becomes the dominant cost of the endpoint — in that case, a database-level `ORDER BY` (O(n log n), or effectively free with an index) would outperform our hand-rolled sort at scale, even though the assignment intentionally requires implementing it manually here.

**Note on due-date sorting**: since `due_date` is intentionally a free-text column (supporting both real dates and AI-parsed phrases like "next friday"), the sort uses a numeric-aware heuristic: "today"/"tomorrow" sort first, numeric day-counts ("2 days", "10") sort by magnitude, other text phrases sort alphabetically, and tasks with no due date sort last. Completed tasks are additionally sunk to the bottom of due-date-sorted results.

---

## Section 3: AI Quick-Add — Prompting Technique Rationale

The quick-add feature's system message and mock parser are modeled on a **zero-shot** prompting approach, rather than few-shot or chain-of-thought.

The system message directly states the extraction task and the exact output format expected (title, priority, due_date_hint) without providing worked examples inside the prompt itself. This was chosen for three reasons specific to TaskFlow's use case:

1. **Token efficiency.** Few-shot prompting requires embedding several example input/output pairs directly in every request, which multiplies token usage on every single quick-add call. Zero-shot keeps the system message short and constant.

2. **Deterministic domain, not open-ended reasoning.** Task parsing here is a narrow, rule-based classification task (keyword matching for priority and date phrases) — it doesn't benefit from a model "thinking out loud."

3. **Reliability via explicit rules, not model inference.** Because the actual parsing logic is deterministic (see `mock_parser.py`), the system message's role is really to document intended behavior for a future real-LLM integration. A zero-shot instruction that precisely enumerates the exact fields and rules is more reliable here than relying on the model to infer structure from examples, since our fallback (the mock) already guarantees correctness regardless of what a real LLM would produce.

If TaskFlow later needed to handle more ambiguous, free-form task descriptions, a few-shot approach with 2-3 worked examples embedded in the prompt would likely improve reliability at the cost of higher token usage per call.

## AI Quick-Add: Worked Examples

| # | Input Description | Parsed Output |
|---|--------------------|-----------------|
| 1 | `Call the vendor whenever you get a chance` | `{'title': 'Call the vendor  you get a chance', 'priority': 'low', 'due_date_hint': None}` |
| 2 | `Submit invoice by next Monday` | `{'title': 'Submit invoice by', 'priority': 'medium', 'due_date_hint': 'next monday'}` |
| 3 | `urgent: fix the payment bug asap` | `{'title': ': fix the payment bug', 'priority': 'high', 'due_date_hint': None}` |
| 4 | `low priority - clean up old logs` | `{'title': '- clean up old logs', 'priority': 'low', 'due_date_hint': None}` |
| 5 | `Review PR on Sunday` | `{'title': 'Review PR on', 'priority': 'medium', 'due_date_hint': 'sunday'}` |

---

## Optional: Real-LLM Quick-Add Path

Set `USE_REAL_LLM=true` and provide `GROK_API_KEY` in `.env` to route quick-add requests through Groq's OpenAI-compatible API instead of the deterministic mock. This path automatically falls back to the mock parser on any error (missing key, network failure, malformed response), so the feature never breaks even with the flag on. **Grading is performed with the flag off** — no API key is required to run or evaluate this project.

---

## Git Workflow

This repository's commit history includes multiple feature branches (`feature/algorithms-engine`, `feature/ai-quick-add`, `feature/auth-and-ui-overhaul`), each with multiple commits, merged back into `main` — visible via:
```bash
git log --oneline --graph --all
```
