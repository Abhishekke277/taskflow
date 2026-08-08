const API_BASE_URL = "http://127.0.0.1:8000";

// Builds headers with the Authorization token attached, if logged in
function authHeaders() {
  const token = localStorage.getItem("taskflow_token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function fetchTasks() {
  const response = await fetch(`${API_BASE_URL}/tasks/`, { headers: authHeaders() });
  if (!response.ok) throw new Error(`Failed to fetch tasks: ${response.status}`);
  return response.json();
}

async function fetchSortedTasks(sortField) {
  const response = await fetch(`${API_BASE_URL}/tasks?sort=${sortField}`, { headers: authHeaders() });
  if (!response.ok) throw new Error(`Failed to fetch sorted tasks: ${response.status}`);
  return response.json();
}

async function searchTaskByTitle(title, algo) {
  const url = `${API_BASE_URL}/tasks/search?title=${encodeURIComponent(title)}&algo=${algo}`;
  const response = await fetch(url, { headers: authHeaders() });
  if (response.status === 404) return { found: false };
  if (!response.ok) throw new Error(`Search failed: ${response.status}`);
  const task = await response.json();
  return { found: true, task };
}

async function createTaskAPI(taskData) {
  const response = await fetch(`${API_BASE_URL}/tasks/`, {
    method: "POST",
    headers: authHeaders(),
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
    headers: authHeaders(),
    body: JSON.stringify(updates),
  });
  if (!response.ok) throw new Error(`Failed to update task: ${response.status}`);
  return response.json();
}

async function deleteTaskAPI(taskId) {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!response.ok) throw new Error(`Failed to delete task: ${response.status}`);
  return response.json();
}