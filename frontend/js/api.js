// Base URL of the backend — matches the two-process run setup.
const API_BASE_URL = "http://127.0.0.1:8000";

async function fetchTasks() {
  const response = await fetch(`${API_BASE_URL}/tasks/`);
  if (!response.ok) throw new Error(`Failed to fetch tasks: ${response.status}`);
  return response.json();
}

/**
 * Fetches tasks sorted by the backend's own insertion_sort
 * implementation (Section 2), via GET /tasks?sort=priority|due_date
 */
async function fetchSortedTasks(sortField) {
  const response = await fetch(`${API_BASE_URL}/tasks?sort=${sortField}`);
  if (!response.ok) throw new Error(`Failed to fetch sorted tasks: ${response.status}`);
  return response.json();
}

/**
 * Searches for a task by exact title using either binary_search
 * or linear_search on the backend (Section 2).
 */
async function searchTaskByTitle(title, algo) {
  const url = `${API_BASE_URL}/tasks/search?title=${encodeURIComponent(title)}&algo=${algo}`;
  const response = await fetch(url);
  if (response.status === 404) {
    return { found: false };
  }
  if (!response.ok) throw new Error(`Search failed: ${response.status}`);
  const task = await response.json();
  return { found: true, task };
}

async function createTaskAPI(taskData) {
  const response = await fetch(`${API_BASE_URL}/tasks/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(taskData),
  });
  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail ? JSON.stringify(errorBody.detail) : "Failed to create task");
  }
  return response.json();
}

async function updateTaskAPI(taskId, updates) {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  if (!response.ok) throw new Error(`Failed to update task: ${response.status}`);
  return response.json();
}

async function deleteTaskAPI(taskId) {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error(`Failed to delete task: ${response.status}`);
  return response.json();
}