const taskListContainer = document.getElementById("task-list-container");
const addTaskForm = document.getElementById("add-task-form");
const titleInput = document.getElementById("task-title");
const dueDateInput = document.getElementById("task-due-date");
const priorityInput = document.getElementById("task-priority");
const projectIdInput = document.getElementById("task-project-id");
const titleError = document.getElementById("title-error");

let currentTasks = [];

/**
 * Renders the task list into the DOM using createElement/appendChild.
 * No innerHTML with user-provided data — textContent only.
 */
function renderTasks(tasks) {
  // Clear existing content
  taskListContainer.textContent = "";

  if (tasks.length === 0) {
    const emptyMsg = document.createElement("p");
    emptyMsg.textContent = "No tasks yet. Add one above.";
    taskListContainer.appendChild(emptyMsg);
    return;
  }

  tasks.forEach((task) => {
    const taskItem = document.createElement("div");
    taskItem.className = "task-item";
    taskItem.dataset.taskId = task.id;

    // ── Task info block ──
    const infoDiv = document.createElement("div");
    infoDiv.className = "task-info";

    const titleEl = document.createElement("h3");
    titleEl.textContent = task.title; // safe: textContent, not innerHTML

    const metaEl = document.createElement("p");
    metaEl.className = "task-meta";
    metaEl.textContent = `Project #${task.project_id} · Due: ${task.due_date || "—"}`;

    const priorityBadge = document.createElement("span");
    priorityBadge.className = `priority-badge priority-${task.priority}`;
    priorityBadge.textContent = task.priority;
    metaEl.appendChild(priorityBadge);

    infoDiv.appendChild(titleEl);
    infoDiv.appendChild(metaEl);

    // ── Actions block ──
    const actionsDiv = document.createElement("div");
    actionsDiv.className = "task-actions";

    const editBtn = document.createElement("button");
    editBtn.textContent = "Edit";
    editBtn.className = "edit-btn";
    editBtn.addEventListener("click", () => handleEditTask(task));

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "Delete";
    deleteBtn.className = "delete-btn";
    deleteBtn.addEventListener("click", () => handleDeleteTask(task.id));

    actionsDiv.appendChild(editBtn);
    actionsDiv.appendChild(deleteBtn);

    taskItem.appendChild(infoDiv);
    taskItem.appendChild(actionsDiv);
    taskListContainer.appendChild(taskItem);
  });
}

/**
 * Loads tasks: shows cached copy immediately, then fetches
 * the real backend list and updates once it arrives.
 */
async function loadTasks() {
  // Show cached data first so the page is never blank while loading
  currentTasks = loadTasksFromCache();
  renderTasks(currentTasks);

  try {
    const freshTasks = await fetchTasks();
    currentTasks = freshTasks;
    renderTasks(currentTasks);
    saveTasksToCache(currentTasks);
  } catch (err) {
    console.error("Could not load tasks from backend:", err);
  }
}

/**
 * Handles add-task form submission.
 */
addTaskForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const title = titleInput.value.trim();

  // Client-side validation: empty title after trimming
  if (!title) {
    titleError.textContent = "Title cannot be empty.";
    return;
  }
  titleError.textContent = "";

  const projectId = parseInt(projectIdInput.value, 10);
  if (!projectId) {
    alert("Please enter a valid project ID.");
    return;
  }

  const newTaskData = {
    title: title,
    due_date: dueDateInput.value.trim() || null,
    priority: priorityInput.value,
    project_id: projectId,
  };

  try {
    const createdTask = await createTaskAPI(newTaskData);
    currentTasks.push(createdTask);
    renderTasks(currentTasks);
    saveTasksToCache(currentTasks);
    addTaskForm.reset();
    priorityInput.value = "medium";
  } catch (err) {
    console.error("Failed to create task:", err);
    alert("Failed to create task. Check the console for details.");
  }
});

/**
 * Removes the error message once the title field becomes valid.
 */
titleInput.addEventListener("input", () => {
  if (titleInput.value.trim()) {
    titleError.textContent = "";
  }
});

/**
 * Handles editing a task — simple prompt-based edit for the title.
 */
async function handleEditTask(task) {
  const newTitle = prompt("Edit task title:", task.title);
  if (newTitle === null) return; // cancelled

  const trimmedTitle = newTitle.trim();
  if (!trimmedTitle) {
    alert("Title cannot be empty.");
    return;
  }

  try {
    const updatedTask = await updateTaskAPI(task.id, { title: trimmedTitle });
    currentTasks = currentTasks.map((t) => (t.id === task.id ? updatedTask : t));
    renderTasks(currentTasks);
    saveTasksToCache(currentTasks);
  } catch (err) {
    console.error("Failed to update task:", err);
    alert("Failed to update task.");
  }
}

/**
 * Handles deleting a task.
 */
async function handleDeleteTask(taskId) {
  const confirmed = confirm("Delete this task?");
  if (!confirmed) return;

  try {
    await deleteTaskAPI(taskId);
    currentTasks = currentTasks.filter((t) => t.id !== taskId);
    renderTasks(currentTasks);
    saveTasksToCache(currentTasks);
  } catch (err) {
    console.error("Failed to delete task:", err);
    alert("Failed to delete task.");
  }
}

// Initial load on page open
loadTasks();