const taskListContainer = document.getElementById("task-list-container");
const addTaskForm = document.getElementById("add-task-form");
const titleInput = document.getElementById("task-title");
const dueDateInput = document.getElementById("task-due-date");
const priorityInput = document.getElementById("task-priority");
const projectIdInput = document.getElementById("task-project-id");
const titleError = document.getElementById("title-error");

const addUserForm = document.getElementById("add-user-form");
const userNameInput = document.getElementById("user-name");
const userEmailInput = document.getElementById("user-email");
const lastCreatedUserIdEl = document.getElementById("last-created-user-id");

const addProjectForm = document.getElementById("add-project-form");
const projectNameInput = document.getElementById("project-name");
const projectOwnerIdInput = document.getElementById("project-owner-id");
const taskProjectSelect = document.getElementById("task-project-id");

let currentTasks = [];

/**
 * Renders the task list into the DOM using createElement/appendChild.
 * No innerHTML with user-provided data — textContent only.
 */
function renderTasks(tasks) {
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

    const infoDiv = document.createElement("div");
    infoDiv.className = "task-info";

    const titleEl = document.createElement("h3");
    titleEl.textContent = task.title;

    const metaEl = document.createElement("p");
    metaEl.className = "task-meta";
    metaEl.textContent = `Project #${task.project_id} · Due: ${task.due_date || "—"}`;

    const priorityBadge = document.createElement("span");
    priorityBadge.className = `priority-badge priority-${task.priority}`;
    priorityBadge.textContent = task.priority;
    metaEl.appendChild(priorityBadge);

    infoDiv.appendChild(titleEl);
    infoDiv.appendChild(metaEl);

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
 * Fetches all projects and populates the dropdown in the task form.
 */
async function loadProjectsIntoDropdown() {
  try {
    const response = await fetch(`${API_BASE_URL}/projects/`);
    if (!response.ok) throw new Error("Failed to fetch projects");
    const projects = await response.json();

    taskProjectSelect.textContent = "";
    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = "Select a project...";
    taskProjectSelect.appendChild(placeholderOption);

    projects.forEach((project) => {
      const option = document.createElement("option");
      option.value = project.id;
      option.textContent = `${project.name} (#${project.id})`;
      taskProjectSelect.appendChild(option);
    });
  } catch (err) {
    console.error("Could not load projects:", err);
  }
}

/**
 * Handles create-user form submission.
 */
addUserForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const name = userNameInput.value.trim();
  const email = userEmailInput.value.trim();

  if (!name || !email) {
    alert("Please enter both a name and an email.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/users/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email }),
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail ? JSON.stringify(errorBody.detail) : "Failed to create user");
    }

    const createdUser = await response.json();
    lastCreatedUserIdEl.textContent = `Created user "${createdUser.name}" — ID: ${createdUser.id}`;
    addUserForm.reset();
  } catch (err) {
    console.error("Failed to create user:", err);
    alert("Failed to create user. Check the console for details — email might already be in use.");
  }
});

/**
 * Handles create-project form submission.
 */
addProjectForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const name = projectNameInput.value.trim();
  const ownerId = parseInt(projectOwnerIdInput.value, 10);

  if (!name || !ownerId) {
    alert("Please enter both a project name and owner user ID.");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/projects/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, owner_id: ownerId }),
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail ? JSON.stringify(errorBody.detail) : "Failed to create project");
    }

    addProjectForm.reset();
    await loadProjectsIntoDropdown();
  } catch (err) {
    console.error("Failed to create project:", err);
    alert("Failed to create project. Check the console for details.");
  }
});

/**
 * Handles add-task form submission.
 */
addTaskForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const title = titleInput.value.trim();

  if (!title) {
    titleError.textContent = "Title cannot be empty.";
    return;
  }
  titleError.textContent = "";

  const projectId = parseInt(projectIdInput.value, 10);
  if (!projectId) {
    alert("Please select a project.");
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
  if (newTitle === null) return;

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
loadProjectsIntoDropdown();