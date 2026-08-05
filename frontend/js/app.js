// ── Theme toggle ──
const themeToggleBtn = document.getElementById("theme-toggle-btn");
let isLightMode = localStorage.getItem("taskflow_theme") === "light";

if (isLightMode) {
  document.documentElement.setAttribute("data-theme", "light");
  themeToggleBtn.textContent = "🌙 Dark";
}

themeToggleBtn.addEventListener("click", () => {
  isLightMode = !isLightMode;
  if (isLightMode) {
    document.documentElement.setAttribute("data-theme", "light");
    localStorage.setItem("taskflow_theme", "light");
    themeToggleBtn.textContent = "🌙 Dark";
  } else {
    document.documentElement.removeAttribute("data-theme");
    localStorage.setItem("taskflow_theme", "dark");
    themeToggleBtn.textContent = "☀ Light";
  }
});

// ── Element references ──
const setupToggleBtn = document.getElementById("setup-toggle-btn");
const setupPanel = document.getElementById("setup-panel");

const quickAddToggle = document.getElementById("quick-add-toggle");
const addTaskForm = document.getElementById("add-task-form");
const titleInput = document.getElementById("task-title");
const dueDateInput = document.getElementById("task-due-date");
const priorityInput = document.getElementById("task-priority");
const projectIdInput = document.getElementById("task-project-id");
const taskFormMsg = document.getElementById("task-form-msg");

const addUserForm = document.getElementById("add-user-form");
const userNameInput = document.getElementById("user-name");
const userEmailInput = document.getElementById("user-email");
const userFormMsg = document.getElementById("user-form-msg");

const addProjectForm = document.getElementById("add-project-form");
const projectNameInput = document.getElementById("project-name");
const projectOwnerIdInput = document.getElementById("project-owner-id");
const projectFormMsg = document.getElementById("project-form-msg");
const taskProjectSelect = document.getElementById("task-project-id");

const searchInput = document.getElementById("search-input");
const searchBtn = document.getElementById("search-btn");
const clearSearchBtn = document.getElementById("clear-search-btn");
const searchResultMsg = document.getElementById("search-result-msg");
const algoButtons = document.querySelectorAll(".algo-btn");
const sortButtons = document.querySelectorAll(".sort-btn");

const flatListEl = document.getElementById("sorted-list-section");
const flatListBody = document.getElementById("sorted-list-body");
const boardEl = document.getElementById("priority-board");

const laneBodies = {
  high: document.getElementById("lane-high"),
  medium: document.getElementById("lane-medium"),
  low: document.getElementById("lane-low"),
};
const laneCounts = {
  high: document.getElementById("count-high"),
  medium: document.getElementById("count-medium"),
  low: document.getElementById("count-low"),
};

let currentTasks = [];
let activeAlgo = "binary";

// Two independent states matching requested behavior:
// viewMode: "list" (default) or "lanes" (when "priority" is clicked)
// sortBy:   "none" (default) or "due_date" (when "due date" is clicked)
let viewMode = "list";
let sortBy = "none";
let searchedTask = null; // Single task search isolate variable

// ── Collapsible setup panel ──
setupToggleBtn.addEventListener("click", () => {
  const isExpanded = setupToggleBtn.getAttribute("aria-expanded") === "true";
  setupToggleBtn.setAttribute("aria-expanded", String(!isExpanded));
  setupPanel.hidden = isExpanded;
});

// ── Quick-add toggle ──
quickAddToggle.addEventListener("click", () => {
  const isHidden = addTaskForm.hidden;
  addTaskForm.hidden = !isHidden;
  quickAddToggle.textContent = isHidden ? "− Cancel" : "+ New Task";
  if (isHidden) titleInput.focus();
});

// ── Build a flat-list card (Image 1 style — shows priority badge) ──
function buildListCard(task) {
  const card = document.createElement("div");
  card.className = "flat-task-card";
  card.dataset.taskId = task.id;

  const info = document.createElement("div");
  info.className = "flat-task-info";

  const titleEl = document.createElement("div");
  titleEl.className = "flat-task-title";
  titleEl.textContent = task.title;

  const meta = document.createElement("div");
  meta.className = "flat-task-meta";

  const projSpan = document.createElement("span");
  projSpan.textContent = `Project #${task.project_id || 0}`;

  const dueSpan = document.createElement("span");
  dueSpan.textContent = `· Due: ${task.due_date || "—"}`;

  const badge = document.createElement("span");
  badge.className = `priority-badge ${task.priority || "low"}`;
  badge.textContent = task.priority || "low";

  meta.appendChild(projSpan);
  meta.appendChild(dueSpan);
  meta.appendChild(badge);

  info.appendChild(titleEl);
  info.appendChild(meta);

  const actions = document.createElement("div");
  actions.className = "flat-task-actions";

  const editBtn = document.createElement("button");
  editBtn.textContent = "Edit";
  editBtn.className = "flat-edit-btn";
  editBtn.addEventListener("click", () => handleEditTask(task));

  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "Delete";
  deleteBtn.className = "flat-delete-btn";
  deleteBtn.addEventListener("click", () => handleDeleteTask(task.id));

  actions.appendChild(editBtn);
  actions.appendChild(deleteBtn);

  card.appendChild(info);
  card.appendChild(actions);

  return card;
}

// ── Build a lane card (Image 2 style — no priority badge, column shows it) ──
function buildLaneCard(task) {
  const card = document.createElement("div");
  card.className = "task-card";
  card.dataset.taskId = task.id;

  const top = document.createElement("div");
  top.className = "task-card-top";

  const titleEl = document.createElement("span");
  titleEl.className = "task-title";
  titleEl.textContent = task.title;

  const idEl = document.createElement("span");
  idEl.className = "task-id";
  idEl.textContent = `#${String(task.id).padStart(3, "0")}`;

  top.appendChild(titleEl);
  top.appendChild(idEl);

  const meta = document.createElement("div");
  meta.className = "task-meta";
  meta.textContent = `proj:${task.project_id || 0} · due:${task.due_date || "—"}`;

  const actions = document.createElement("div");
  actions.className = "task-actions";

  const editBtn = document.createElement("button");
  editBtn.textContent = "edit";
  editBtn.className = "edit-btn";
  editBtn.addEventListener("click", () => handleEditTask(task));

  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "delete";
  deleteBtn.className = "delete-btn";
  deleteBtn.addEventListener("click", () => handleDeleteTask(task.id));

  actions.appendChild(editBtn);
  actions.appendChild(deleteBtn);

  card.appendChild(top);
  card.appendChild(meta);
  card.appendChild(actions);

  return card;
}

// ── Renders whichever view is currently active, using currentTasks ──
function renderCurrentView() {
  if (searchedTask !== null) {
    boardEl.hidden = true;
    flatListEl.hidden = false;
    renderFlatList([searchedTask]);
    return;
  }

  if (viewMode === "lanes") {
    flatListEl.hidden = true;
    boardEl.hidden = false;
    renderLaneBoard(currentTasks);
  } else {
    boardEl.hidden = true;
    flatListEl.hidden = false;
    renderFlatList(currentTasks);
  }
}

function renderFlatList(tasks) {
  flatListBody.textContent = "";

  if (!tasks || tasks.length === 0) {
    const emptyMsg = document.createElement("p");
    emptyMsg.className = "lane-empty";
    emptyMsg.textContent = "No tasks yet. Add one above.";
    flatListBody.appendChild(emptyMsg);
    return;
  }

  tasks.forEach((task) => {
    flatListBody.appendChild(buildListCard(task));
  });
}

function renderLaneBoard(tasks) {
  Object.values(laneBodies).forEach((el) => (el.textContent = ""));

  const grouped = { high: [], medium: [], low: [] };
  tasks.forEach((task) => {
    if (grouped[task.priority]) grouped[task.priority].push(task);
  });

  Object.keys(grouped).forEach((priority) => {
    const laneTasks = grouped[priority];
    laneCounts[priority].textContent = laneTasks.length;

    if (laneTasks.length === 0) {
      const emptyMsg = document.createElement("p");
      emptyMsg.className = "lane-empty";
      emptyMsg.textContent = "— empty —";
      laneBodies[priority].appendChild(emptyMsg);
      return;
    }

    laneTasks.forEach((task) => {
      laneBodies[priority].appendChild(buildLaneCard(task));
    });
  });
}

// ── Load tasks: cache first, then live backend, honoring sortBy ──
async function loadTasks() {
  currentTasks = loadTasksFromCache();
  renderCurrentView();

  try {
    const freshTasks =
      sortBy === "due_date"
        ? await fetchSortedTasks("due_date")
        : await fetchTasks();
    currentTasks = freshTasks;
    renderCurrentView();
    saveTasksToCache(freshTasks);
  } catch (err) {
    console.error("Could not load tasks from backend:", err);
  }
}

// ── Sort / view control buttons ──
sortButtons.forEach((btn) => {
  btn.addEventListener("click", async () => {
    const action = btn.dataset.action || btn.dataset.sort;

    if (action === "unsorted") {
      viewMode = "list";
      sortBy = "none";
      sortButtons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
    } else if (action === "priority") {
      viewMode = "lanes";
      btn.classList.add("active");
      const unsortedBtn = document.querySelector('[data-action="unsorted"], [data-sort="unsorted"]');
      if (unsortedBtn) unsortedBtn.classList.remove("active");
    } else if (action === "due_date") {
      sortBy = "due_date";
      btn.classList.add("active");
      const unsortedBtn = document.querySelector('[data-action="unsorted"], [data-sort="unsorted"]');
      if (unsortedBtn) unsortedBtn.classList.remove("active");
    }

    await loadTasks();
  });
});

// ── Search control with red/green feedback & 3s timeout ──
algoButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    algoButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    activeAlgo = btn.dataset.algo;
  });
});

// Helper function to display search feedback messages with 3s auto-clear timeout
const showTemporarySearchMessage = (text, type) => {
  searchResultMsg.textContent = text;
  searchResultMsg.className = `search-result-msg ${type}`;

  setTimeout(() => {
    searchResultMsg.textContent = "";
    searchResultMsg.className = "search-result-msg";
  }, 3000); // 3 seconds timeout
};

searchBtn.addEventListener("click", async () => {
  const title = searchInput.value.trim();
  if (!title) {
    showTemporarySearchMessage("enter a title to search", "error");
    return;
  }

  searchResultMsg.textContent = `searching (${activeAlgo})...`;
  searchResultMsg.className = "search-result-msg";

  try {
    const result = await searchTaskByTitle(title, activeAlgo);
    if (result.found) {
      searchedTask = result.task;
      showTemporarySearchMessage(
        `found: #${String(result.task.id).padStart(3, "0")} "${result.task.title}" via ${activeAlgo}_search`,
        "success"
      );
      renderCurrentView();
    } else {
      searchedTask = null;
      showTemporarySearchMessage(`no exact match for "${title}"`, "error");
      renderFlatList([]);
    }
  } catch (err) {
    console.error("Search failed:", err);
    showTemporarySearchMessage("search failed — check console", "error");
  }
});

searchInput.addEventListener("input", () => {
  if (searchInput.value.trim() === "") {
    searchedTask = null;
    searchResultMsg.textContent = "";
    searchResultMsg.className = "search-result-msg";
    renderCurrentView();
  }
});

searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") searchBtn.click();
});

clearSearchBtn.addEventListener("click", () => {
  searchInput.value = "";
  searchResultMsg.textContent = "";
  searchResultMsg.className = "search-result-msg";
  searchedTask = null;
  renderCurrentView();
});

// ── Project dropdown ──
async function loadProjectsIntoDropdown() {
  try {
    const response = await fetch(`${API_BASE_URL}/projects/`);
    if (!response.ok) throw new Error("Failed to fetch projects");
    const projects = await response.json();

    taskProjectSelect.textContent = "";
    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = "Select...";
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

// ── Create user with green/red messaging (with 3s auto-clear timeout) ──
addUserForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  userFormMsg.textContent = "";
  userFormMsg.className = "form-feedback-msg";

  const name = userNameInput.value.trim();
  const email = userEmailInput.value.trim();

  // Helper function to show message and set 3 second timeout
  const showTemporaryMessage = (text, type) => {
    userFormMsg.textContent = text;
    userFormMsg.className = `form-feedback-msg ${type}`;

    setTimeout(() => {
      userFormMsg.textContent = "";
      userFormMsg.className = "form-feedback-msg";
    }, 3000); // 3 seconds timeout
  };

  if (!name || !email) {
    showTemporaryMessage("Both name and email fields are required.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/users/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email }),
    });

    if (response.ok || response.status === 201) {
      let createdUser = {};
      try { createdUser = await response.json(); } catch (e) {}

      const userIdText = createdUser.id ? ` (User ID: ${createdUser.id})` : "";
      showTemporaryMessage(`User created successfully!${userIdText}`, "success");
      addUserForm.reset();
    } else {
      const errorBody = await response.json().catch(() => ({}));
      const errorDetail = errorBody.detail || "Failed to create user. Email might already exist.";
      const msgText = typeof errorDetail === "string" ? errorDetail : JSON.stringify(errorDetail);
      showTemporaryMessage(msgText, "error");
    }
  } catch (err) {
    console.error("Failed to create user:", err);
    showTemporaryMessage("Network error while creating user.", "error");
  }
});


// ── Create project with green/red messaging (with 3s auto-clear timeout) ──
addProjectForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  projectFormMsg.textContent = "";
  projectFormMsg.className = "form-feedback-msg";

  const name = projectNameInput.value.trim();
  const ownerId = parseInt(projectOwnerIdInput.value, 10);

  // Helper function to display message and automatically clear it after 3 seconds
  const showTemporaryMessage = (text, type) => {
    projectFormMsg.textContent = text;
    projectFormMsg.className = `form-feedback-msg ${type}`;

    setTimeout(() => {
      projectFormMsg.textContent = "";
      projectFormMsg.className = "form-feedback-msg";
    }, 3000); // 3 seconds timeout
  };

  if (!name || !ownerId) {
    showTemporaryMessage("All fields are required to create a project.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/projects/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, owner_id: ownerId }),
    });

    if (response.ok || response.status === 201) {
      showTemporaryMessage("Project created successfully!", "success");
      addProjectForm.reset();
      await loadProjectsIntoDropdown();
    } else {
      showTemporaryMessage("Failed to create project. Verify Owner User ID.", "error");
    }
  } catch (err) {
    console.error("Failed to create project:", err);
    showTemporaryMessage("Failed to create project.", "error");
  }
});

// ── Add task — with 3s auto-clear timeout for messages ──
addTaskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  taskFormMsg.textContent = "";
  taskFormMsg.className = "form-feedback-msg full-width-msg";

  // Helper function to display message and clear it after 3 seconds
  const showTemporaryMessage = (text, type, onComplete = null) => {
    taskFormMsg.textContent = text;
    taskFormMsg.className = `form-feedback-msg full-width-msg ${type}`;

    setTimeout(() => {
      taskFormMsg.textContent = "";
      taskFormMsg.className = "form-feedback-msg full-width-msg";
      if (onComplete) onComplete();
    }, 3000); // 3 seconds timeout
  };

  const title = titleInput.value.trim();
  if (!title) {
    showTemporaryMessage("Title field cannot be empty.", "error");
    return;
  }

  const projectId = parseInt(projectIdInput.value, 10);
  if (!projectId) {
    showTemporaryMessage("Please select a project for the task.", "error");
    return;
  }

  const newTaskData = {
    title: title,
    due_date: dueDateInput.value.trim() || null,
    priority: priorityInput.value,
    project_id: projectId,
  };

  try {
    await createTaskAPI(newTaskData);
    await loadTasks();
    addTaskForm.reset();
    priorityInput.value = "medium";

    showTemporaryMessage("Task added successfully!", "success", () => {
      addTaskForm.hidden = true;
      quickAddToggle.textContent = "+ New Task";
    });
  } catch (err) {
    console.error("Failed to create task:", err);
    showTemporaryMessage("Failed to create task. Check the console.", "error");
  }
});

titleInput.addEventListener("input", () => {
  if (titleInput.value.trim()) taskFormMsg.textContent = "";
});

// ── Edit / delete ──
async function handleEditTask(task) {
  const newTitle = prompt("Edit task title:", task.title);
  if (newTitle === null) return;

  const trimmedTitle = newTitle.trim();
  if (!trimmedTitle) {
    alert("Title cannot be empty.");
    return;
  }

  try {
    await updateTaskAPI(task.id, { title: trimmedTitle });
    await loadTasks();
  } catch (err) {
    console.error("Failed to update task:", err);
    alert("Failed to update task.");
  }
}

async function handleDeleteTask(taskId) {
  const confirmed = confirm("Delete this task?");
  if (!confirmed) return;

  try {
    await deleteTaskAPI(taskId);
    await loadTasks();
  } catch (err) {
    console.error("Failed to delete task:", err);
    alert("Failed to delete task.");
  }
}

// ── Initial load ──
loadTasks();
loadProjectsIntoDropdown();