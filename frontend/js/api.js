// Base URL of the backend — matches the two-process run setup.
// Update this if your backend runs on a different port.
const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Fetches all tasks from the real backend.
 */
async function fetchTasks() {
  const response = await fetch(`${API_BASE_URL}/tasks/`);
  if (!response.ok) {
    throw new Error(`Failed to fetch tasks: ${response.status}`);
  }
  return response.json();
}

/**
 * Sends a new task to the backend.
 */
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

/**
 * Sends an update for an existing task.
 */
async function updateTaskAPI(taskId, updates) {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates),
  });
  if (!response.ok) {
    throw new Error(`Failed to update task: ${response.status}`);
  }
  return response.json();
}

/**
 * Deletes a task on the backend.
 */
async function deleteTaskAPI(taskId) {
  const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(`Failed to delete task: ${response.status}`);
  }
  return response.json();
}