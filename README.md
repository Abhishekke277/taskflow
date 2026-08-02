# TaskFlow

A task management API built with FastAPI, SQLAlchemy, and a vanilla JS frontend.

## Setup

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## Run

```bash
uvicorn backend.main:app --reload
```

Frontend: open `frontend/index.html` in a browser (or serve via Live Server).

## Endpoints

### Users
| Method | Path | Description |
|--------|------|-------------|
| POST | `/users/` | Create a user |
| GET | `/users/` | List all users |

### Projects
| Method | Path | Description |
|--------|------|-------------|
| POST | `/projects/` | Create a project |
| GET | `/projects/` | List all projects |
| GET | `/projects/{id}/stats` | Task stats for a project |

### Tasks
| Method | Path | Description |
|--------|------|-------------|
| POST | `/tasks/` | Create a task |
| GET | `/tasks/` | List tasks (filter by project) |
| GET | `/tasks/{id}` | Get a single task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |
| GET | `/tasks/sort` | Return tasks sorted by priority/due_date |
| GET | `/tasks/search` | Binary or linear search by title |
| POST | `/tasks/quick-add` | AI-powered natural-language task creation |

## Algorithmic Complexity Write-Up

### Insertion Sort (`algorithms/sorting.py`)
- **Best case**: O(n) — already sorted input; inner loop never swaps.
- **Average/Worst case**: O(n²) — each element may shift past all previous elements.
- **Space**: O(1) in-place.
- Chosen because it is simple to instrument with a comparison counter and performs well on small or nearly-sorted lists (common in task lists).

### Binary Search (`algorithms/searching.py`)
- **Best case**: O(1) — target is the midpoint.
- **Average/Worst case**: O(log n) — halves the search space each step.
- **Prerequisite**: input must be sorted; we sort with insertion sort first.
- Falls back to linear search O(n) when the list is unsorted or for substring matching.

## AI Quick-Add Prompting Rationale

The prompt (`ai/prompt.py`) uses a **system + user role** structure:
- The **system role** locks the model into returning only JSON and defines the exact output schema, preventing free-text hallucination.
- The **user role** passes the raw natural-language string.
- A deterministic `mock_parser.py` is always available behind the `USE_REAL_LLM=false` flag so the feature works without an API key during development and testing.
