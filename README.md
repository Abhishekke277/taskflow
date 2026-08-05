# TaskFlow — Full-Stack Task Management Platform

An internal task-and-project management platform built for Blinkit's dark-store engineering pods. Combines a FastAPI + SQLAlchemy backend, a vanilla JS dashboard, a hand-rolled sorting/search engine, and an AI-assisted quick-add feature — all operating on the same three-table database (users, projects, tasks).

## Environment Setup

1. Clone the repository and navigate into it:
```bash
   git clone <your-repo-url>
   cd taskflow
```

2. Create and activate a virtual environment:
```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
```

3. Install dependencies:
```bash
   pip install -r requirements.txt
```

4. Create a `.env` file in the project root with:

DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxxxxxxxxxx.supabase.co:5432/postgres
USE_REAL_LLM=false
GROK_API_KEY=

(`GROK_API_KEY` is only needed if you want to test the optional real-LLM path — leave `USE_REAL_LLM=false` for normal/graded use, which requires zero API keys.)

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

The backend's CORS configuration (`backend/main.py`) is already set to allow requests from `http://127.0.0.1:3000` and `http://localhost:3000`. If you serve the frontend from a different port, update the `allow_origins` list in `main.py` to match.

## Database Schema

Three tables, defined as SQLAlchemy models in `backend/models/`:

- **users**: `id` (PK), `name`, `email` (UNIQUE, NOT NULL)
- **projects**: `id` (PK), `name`, `owner_id` (FK → users.id)
- **tasks**: `id` (PK), `title` (NOT NULL), `priority` (CHECK: 'low'/'medium'/'high'), `due_date` (nullable text), `project_id` (FK → projects.id)

## API Endpoints

Base URL: `http://127.0.0.1:8000`

### Users

**Create user** — `POST /users/`
```json
// Request
{ "name": "Priya Sharma", "email": "priya@blinkit.com" }
// Response (201)
{ "id": 1, "name": "Priya Sharma", "email": "priya@blinkit.com" }
```

**List users** — `GET /users/`
```json
// Response (200) — list
[
  { "id": 17, "name": "riya jatav", "email": "riya@gmail.com" },
  { "id": 18, "name": "Ankush kewat", "email": "Ankush@gmail.com" },
  { "id": 19, "name": "Priya Sharma", "email": "priya@blinkit.com" }
]
```
### Projects
```json
// Create — POST /projects/
{ "name": "Dark Store Ops", "owner_id": 19 }
// Response (201)
{ "id": 13, "name": "Dark Store Ops", "owner_id": 19 }
```

// List — GET /projects/
```json
[
  { "id": 11, "name": "odd even", "owner_id": 17 },
  { "id": 12, "name": "Ai Chatbout", "owner_id": 18 },
  { "id": 13, "name": "Dark Store Ops", "owner_id": 19 }
]
```
```json
// Get by ID — GET /projects/13
// Response (200)
{ "id": 13, "name": "Dark Store Ops", "owner_id": 19 }
```

// Statistics — GET /projects/13/stats
```json
// Response (200)
{ "project_id": 13, "total_tasks": 0, "by_priority": {} }

(Example above shows a freshly created project with no tasks yet. Once tasks are added, by_priority reflects the real distribution, e.g. {"high": 2, "medium": 1}.)
```
### Tasks

**Create task** — `POST /tasks/`
```json
// Request
{ "title": "Restock shelves", "priority": "high", "due_date": "tomorrow", "project_id": 13 }
// Response (201)
{ "id": 23, "title": "Restock shelves", "priority": "high", "due_date": "tomorrow", "project_id": 13 }
```

**List tasks** — `GET /tasks/`
```json
// Response (200)
[
  { "id": 22, "title": "Create AI bout", "priority": "medium", "due_date": "6", "project_id": 12 },
  { "id": 23, "title": "Restock shelves", "priority": "high", "due_date": "tomorrow", "project_id": 13 }
]
```

**Get task by id** — `GET /tasks/{id}`
```json
// Response (200)
{ "id": 23, "title": "Restock shelves", "priority": "high", "due_date": "tomorrow", "project_id": 13 }
// 404 if not found: { "detail": "Task not found" }
```

**Update task** — `PUT /tasks/{id}`
```json
// Update — PUT /tasks/23
{ "title": "Restock shelves urgently" }
// Response (200)
{ "id": 23, "title": "Restock shelves urgently", "priority": "high", "due_date": "tomorrow", "project_id": 13 }
```

**Delete task** — `DELETE /tasks/{id}`
```json
// Delete — DELETE /tasks/23
// Response (200)
{ "message": "Task deleted", "id": 23 }
("run this after complete search section not before.")
```

**Sorted list (Section 2)** — `GET /tasks?sort=priority` 
```json
// Sorted list — GET /tasks?sort=priority
// Response (200) — sorted via our own insertion_sort, not built-in sort or ORDER BY
[
  { "id": 21, "title": "start bussiness", "priority": "low", "due_date": ".5 day", "project_id": 11 },
  { "id": 15, "title": "solve two problems", "priority": "medium", "due_date": "1 days", "project_id": 8 },
  { "id": 22, "title": "Create AI bout", "priority": "medium", "due_date": "6", "project_id": 12 },
  { "id": 7, "title": "Calculator", "priority": "high", "due_date": "1 days", "project_id": 5 },
  { "id": 20, "title": "kanban bourd", "priority": "high", "due_date": "2 days", "project_id": 4 }
]
```

**Search (Section 2)** — `GET /tasks/search?title=Restock shelves urgently&algo=binary` (or `algo=linear`)
```json
// Search — GET /tasks/search?title=Restock shelves urgently&algo=binary
// Response (200)
{ "id": 23, "title": "Restock shelves urgently", "priority": "high", "due_date": "tomorrow", "project_id": 13 }
// 404 if no exact match: { "detail": "No task found with that exact title" }
```

**AI Quick-Add (Section 3)** — `POST /tasks/quick-add`
```json
// AI Quick-Add (Section 3) — POST /tasks/quick-add
{ "description": "This is urgent, mark it ASAP please", "project_id": 13 }
// Response (201)
{ "id": 24, "title": "This is , mark it  please", "priority": "high", "due_date": null, "project_id": 13 }
// 422 if project_id doesn't exist or body is malformed
```

---


Algorithm Complexity & Benchmark Analysis

Time Complexity:

insertion_sort: Best case O(n) — already-sorted input, one comparison per element. Worst case O(n²) — reverse-sorted input, each element compared against and shifted past all previously placed elements.
binary_search: Best case O(1) — target found at the middle index immediately. Worst case O(log n) — search space halves each iteration until exhausted.
linear_search: Best case O(1) — target is the first element checked. Worst case O(n) — target is last or absent, requiring a full scan.

Is sorting-first worth it?

Our benchmark confirms the theoretical complexity: sorting 3,000 tasks with insertion_sort took 1,820,009 comparisons, while searching that same sorted list with binary_search took only 12 comparisons — versus 3,000 comparisons for linear_search on unsorted data. Given TaskFlow's real usage pattern — a team listing/sorting tasks repeatedly throughout the day, while adding or renaming tasks comparatively rarely — paying the steep one-time O(n²) sorting cost is justified whenever the sorted list can be reused across multiple reads (e.g. a session cache), since each subsequent binary search stays near-constant even as the dataset grows into the thousands. However, if GET /tasks?sort=priority re-sorts from scratch on every single request without caching, the O(n²) cost is paid repeatedly, and at 3,000+ tasks this becomes the dominant cost of the endpoint — in that case, a database-level ORDER BY (O(n log n), or effectively free with an index) would outperform our hand-rolled sort at scale, even though the assignment intentionally requires implementing it manually here.


## AI Quick-Add: Prompting Technique Rationale

The quick-add feature's system message and mock parser are modeled on a **zero-shot** prompting approach, rather than few-shot or chain-of-thought.

The system message directly states the extraction task and the exact output format expected (title, priority, due_date_hint) without providing worked examples inside the prompt itself. This was chosen for three reasons specific to TaskFlow's use case:

1. **Token efficiency.** Few-shot prompting requires embedding several example input/output pairs directly in every request, which multiplies token usage on every single quick-add call — a cost that adds up quickly for a feature meant to be used dozens of times a day across a team. Zero-shot keeps the system message short and constant.

2. **Deterministic domain, not open-ended reasoning.** Chain-of-thought prompting is most valuable when a task benefits from step-by-step reasoning over ambiguous or multi-step problems. Task parsing here is a narrow, rule-based classification task (keyword matching for priority and date phrases) — it doesn't benefit from a model "thinking out loud," and forcing that would only inflate token usage without improving reliability.

3. **Reliability via explicit rules, not model inference.** Because the actual parsing logic is deterministic (see `mock_parser.py`), the system message's role is really to document intended behavior for a future real-LLM integration — not to carry the reasoning burden itself. A zero-shot instruction that precisely enumerates the exact fields and rules is more reliable here than relying on the model to infer structure from examples, since our fallback (the mock) already guarantees correctness regardless of what a real LLM would produce.

If TaskFlow later needed to handle more ambiguous, free-form task descriptions (e.g. instructions requiring inference about implied urgency), a few-shot approach with 2-3 worked examples embedded in the prompt would likely improve reliability at the cost of higher token usage per call.

## AI Quick-Add: Worked Examples

| # | Input Description | Parsed Output |
|---|--------------------|-----------------|
| 1 | `Call the vendor whenever you get a chance` | `{'title': 'Call the vendor  you get a chance', 'priority': 'low', 'due_date_hint': None}` |
| 2 | `Submit invoice by next Monday` | `{'title': 'Submit invoice by', 'priority': 'medium', 'due_date_hint': 'next monday'}` |
| 3 | `urgent: fix the payment bug asap` | `{'title': ': fix the payment bug', 'priority': 'high', 'due_date_hint': None}` |
| 4 | `low priority - clean up old logs` | `{'title': '- clean up old logs', 'priority': 'low', 'due_date_hint': None}` |
| 5 | `Review PR on Sunday` | `{'title': 'Review PR on', 'priority': 'medium', 'due_date_hint': 'sunday'}` |