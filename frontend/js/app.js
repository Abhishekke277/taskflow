// ── AUTH LOGIC ──
const authScreen = document.getElementById("auth-screen");
const appContent = document.getElementById("app-content");

const tabSignin = document.getElementById("tab-signin");
const tabRegister = document.getElementById("tab-register");
const signinForm = document.getElementById("signin-form");
const registerForm = document.getElementById("register-form");
const signinMsg = document.getElementById("signin-msg");
const registerMsg = document.getElementById("register-msg");

tabSignin.addEventListener("click", () => {
  tabSignin.classList.add("active");
  tabRegister.classList.remove("active");
  signinForm.hidden = false;
  registerForm.hidden = true;
});

tabRegister.addEventListener("click", () => {
  tabRegister.classList.add("active");
  tabSignin.classList.remove("active");
  registerForm.hidden = false;
  signinForm.hidden = true;
});

document.querySelectorAll(".eye-toggle").forEach((btn) => {
  btn.addEventListener("click", () => {
    const targetInput = document.getElementById(btn.dataset.target);
    const isHidden = targetInput.type === "password";
    targetInput.type = isHidden ? "text" : "password";
    btn.classList.toggle("showing", isHidden);
  });
});

function showAuthMessage(el, text, type) {
  el.textContent = text;
  el.className = `form-feedback-msg ${type}`;
  setTimeout(() => {
    el.textContent = "";
    el.className = "form-feedback-msg";
  }, 3000);
}

function loginSuccess(data) {
  localStorage.setItem("taskflow_token", data.access_token);
  localStorage.setItem("taskflow_user_name", data.name);
  localStorage.setItem("taskflow_user_email", data.email);

  authScreen.hidden = true;
  appContent.hidden = false;

  updateProfileDisplay();
  loadTasks();
  loadProjectsIntoDropdown();
}

signinForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const email = document.getElementById("signin-email").value.trim();
  const password = document.getElementById("signin-password").value;

  if (!email || !password) {
    showAuthMessage(signinMsg, "Email and password are required.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      showAuthMessage(signinMsg, "Incorrect email or password.", "error");
      return;
    }

    
    const data = await response.json();
    signinForm.reset();
    showAuthMessage(signinMsg, "Signed in!", "success");
    loginSuccess(data);
  } catch (err) {
    console.error("Login failed:", err);
    showAuthMessage(signinMsg, "Network error — check console.", "error");
  }
});

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = document.getElementById("register-name").value.trim();
  const email = document.getElementById("register-email").value.trim();
  const password = document.getElementById("register-password").value;

  if (!name || !email || !password) {
    showAuthMessage(registerMsg, "All fields are required.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password }),
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      showAuthMessage(registerMsg, errorBody.detail || "Registration failed.", "error");
      return;
    }

    const data = await response.json();
    registerForm.reset();
    showAuthMessage(registerMsg, "Account created!", "success");
    loginSuccess(data);
  } catch (err) {
    console.error("Registration failed:", err);
    showAuthMessage(registerMsg, "Network error — check console.", "error");
  }
});

const existingToken = localStorage.getItem("taskflow_token");
if (existingToken) {
  authScreen.hidden = true;
  appContent.hidden = false;
} else {
  authScreen.hidden = false;
  appContent.hidden = true;
}

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

// ── Profile popup + Logout ──
const profileBtn = document.getElementById("profile-btn");
const profilePopup = document.getElementById("profile-popup");
const profilePopupClose = document.getElementById("profile-popup-close");
const profileNameEl = document.getElementById("profile-name");
const profileEmailEl = document.getElementById("profile-email");
const logoutBtn = document.getElementById("logout-btn");

function updateProfileDisplay() {
  profileNameEl.textContent = localStorage.getItem("taskflow_user_name") || "";
  profileEmailEl.textContent = localStorage.getItem("taskflow_user_email") || "";
}

profileBtn.addEventListener("click", () => {
  profilePopup.hidden = !profilePopup.hidden;
});

profilePopupClose.addEventListener("click", () => {
  profilePopup.hidden = true;
});

logoutBtn.addEventListener("click", () => {
  localStorage.removeItem("taskflow_token");
  localStorage.removeItem("taskflow_user_name");
  localStorage.removeItem("taskflow_user_email");

  // Clear both forms so no leftover credentials are visible to
  // the next person who opens the sign-in screen
  signinForm.reset();
  registerForm.reset();

  profilePopup.hidden = true;
  appContent.hidden = true;
  authScreen.hidden = false;

  // Always land back on the Sign In tab, not wherever the user last was
  tabSignin.classList.add("active");
  tabRegister.classList.remove("active");
  signinForm.hidden = false;
  registerForm.hidden = true;
});


if (existingToken) {
  updateProfileDisplay();
}

// ── Element references ──
const quickAddToggle = null; // no longer used — both forms always visible
const addTaskForm = document.getElementById("add-task-form");
const titleInput = document.getElementById("task-title");
const dueDateInput = document.getElementById("task-due-date");
const priorityInput = document.getElementById("task-priority");
const projectIdInput = document.getElementById("task-project-id");
const taskFormMsg = document.getElementById("task-form-msg");

const addProjectForm = document.getElementById("add-project-form");
const projectNameInput = document.getElementById("project-name");
const projectFormMsg = document.getElementById("project-form-msg");
const taskProjectSelect = document.getElementById("task-project-id");

const quickAddForm = document.getElementById("quick-add-form");
const quickAddDescription = document.getElementById("quick-add-description");
const quickAddProjectSelect = document.getElementById("quick-add-project-id");
const quickAddMsg = document.getElementById("quick-add-msg");

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
let viewMode = "list";
let sortBy = "none";
let searchedTask = null;

// ── Task card builders ──
function buildListCard(task) {
  const card = document.createElement("div");
  card.className = "flat-task-card";
  card.dataset.taskId = task.id;

  const info = document.createElement("div");
  info.className = "flat-task-info";

  const titleEl = document.createElement("div");
  titleEl.className = task.completed ? "flat-task-title completed" : "flat-task-title";
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

  const toggleBtn = document.createElement("button");
  toggleBtn.textContent = task.completed ? "↺ Undo" : "✓ Complete";
  toggleBtn.className = "flat-toggle-btn";
  toggleBtn.addEventListener("click", () => handleToggleComplete(task));


  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "Delete";
  deleteBtn.className = "flat-delete-btn";
  deleteBtn.addEventListener("click", () => handleDeleteTask(task.id));

  actions.appendChild(editBtn);
  actions.appendChild(toggleBtn);
  actions.appendChild(deleteBtn);

  card.appendChild(info);
  card.appendChild(actions);

  return card;
}

function buildLaneCard(task) {
  const card = document.createElement("div");
  card.className = "task-card";
  card.dataset.taskId = task.id;

  const top = document.createElement("div");
  top.className = "task-card-top";

  const titleEl = document.createElement("span");
  titleEl.className = task.completed ? "flat-task-title completed" : "flat-task-title";
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

  const toggleBtn = document.createElement("button");
  toggleBtn.textContent = task.completed ? "↺ Undo" : "✓ Complete";
  toggleBtn.className = "toggle-btn";
  toggleBtn.addEventListener("click", () => handleToggleComplete(task));
  actions.appendChild(toggleBtn);

  const deleteBtn = document.createElement("button");
  deleteBtn.textContent = "delete";
  deleteBtn.className = "delete-btn";
  deleteBtn.addEventListener("click", () => handleDeleteTask(task.id));

  actions.appendChild(editBtn);
  actions.appendChild(toggleBtn);
  actions.appendChild(deleteBtn);

  card.appendChild(top);
  card.appendChild(meta);
  card.appendChild(actions);

  return card;
}

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

async function loadTasks() {
  currentTasks = loadTasksFromCache();
  renderCurrentView();

  try {
    const freshTasks =
      sortBy === "due_date" ? await fetchSortedTasks("due_date") : await fetchTasks();
    currentTasks = freshTasks;
    renderCurrentView();
    saveTasksToCache(freshTasks);
  } catch (err) {
    console.error("Could not load tasks from backend:", err);
  }
}

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
      const unsortedBtn = document.querySelector('[data-sort="unsorted"]');
      if (unsortedBtn) unsortedBtn.classList.remove("active");
    } else if (action === "due_date") {
      sortBy = "due_date";
      btn.classList.add("active");
      const unsortedBtn = document.querySelector('[data-sort="unsorted"]');
      if (unsortedBtn) unsortedBtn.classList.remove("active");
    }

    await loadTasks();
  });
});

algoButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    algoButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    activeAlgo = btn.dataset.algo;
  });
});

const showTemporarySearchMessage = (text, type) => {
  searchResultMsg.textContent = text;
  searchResultMsg.className = `search-result-msg ${type}`;
  setTimeout(() => {
    searchResultMsg.textContent = "";
    searchResultMsg.className = "search-result-msg";
  }, 3000);
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

// ── Project dropdown (fills both manual-add and quick-add selects) ──
async function loadProjectsIntoDropdown() {
  try {
    const response = await fetch(`${API_BASE_URL}/projects/`, { headers: authHeaders() });
    if (!response.ok) throw new Error("Failed to fetch projects");
    const projects = await response.json();

    taskProjectSelect.textContent = "";
    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = "Select...";
    taskProjectSelect.appendChild(placeholderOption);

    quickAddProjectSelect.textContent = "";
    const qaPlaceholder = document.createElement("option");
    qaPlaceholder.value = "";
    qaPlaceholder.textContent = "Select...";
    quickAddProjectSelect.appendChild(qaPlaceholder);

    projects.forEach((project) => {
      const option1 = document.createElement("option");
      option1.value = project.id;
      option1.textContent = `${project.name} (#${project.id})`;
      taskProjectSelect.appendChild(option1);

      const option2 = document.createElement("option");
      option2.value = project.id;
      option2.textContent = `${project.name} (#${project.id})`;
      quickAddProjectSelect.appendChild(option2);
    });
  } catch (err) {
    console.error("Could not load projects:", err);
  }
}

// ── Create project ──
addProjectForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  projectFormMsg.textContent = "";
  projectFormMsg.className = "form-feedback-msg";

  const name = projectNameInput.value.trim();

  const showTemporaryMessage = (text, type) => {
    projectFormMsg.textContent = text;
    projectFormMsg.className = `form-feedback-msg ${type}`;
    setTimeout(() => {
      projectFormMsg.textContent = "";
      projectFormMsg.className = "form-feedback-msg";
    }, 3000);
  };

  if (!name) {
    showTemporaryMessage("Project name is required.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/projects/`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ name }),
    });

    if (response.ok || response.status === 201) {
      showTemporaryMessage("Project created successfully!", "success");
      addProjectForm.reset();
      await loadProjectsIntoDropdown();
    } else {
      showTemporaryMessage("Failed to create project.", "error");
    }
  } catch (err) {
    console.error("Failed to create project:", err);
    showTemporaryMessage("Failed to create project.", "error");
  }
});

// ── Add task manually ──
addTaskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  taskFormMsg.textContent = "";
  taskFormMsg.className = "form-feedback-msg full-width-msg";

  const showTemporaryMessage = (text, type) => {
    taskFormMsg.textContent = text;
    taskFormMsg.className = `form-feedback-msg full-width-msg ${type}`;
    setTimeout(() => {
      taskFormMsg.textContent = "";
      taskFormMsg.className = "form-feedback-msg full-width-msg";
    }, 3000);
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
    showTemporaryMessage("Task added successfully!", "success");
  } catch (err) {
    console.error("Failed to create task:", err);
    showTemporaryMessage("Failed to create task. Check the console.", "error");
  }
});

titleInput.addEventListener("input", () => {
  if (titleInput.value.trim()) taskFormMsg.textContent = "";
});

// ── Quick-Add (AI) ──
quickAddForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const description = quickAddDescription.value.trim();
  const projectId = parseInt(quickAddProjectSelect.value, 10);

  const showTemporaryMessage = (text, type) => {
    quickAddMsg.textContent = text;
    quickAddMsg.className = `form-feedback-msg ${type}`;
    setTimeout(() => {
      quickAddMsg.textContent = "";
      quickAddMsg.className = "form-feedback-msg";
    }, 3000);
  };

  if (!description) {
    showTemporaryMessage("Please describe the task.", "error");
    return;
  }
  if (!projectId) {
    showTemporaryMessage("Please select a project.", "error");
    return;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/tasks/quick-add`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify({ description, project_id: projectId }),
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail || "Failed to quick-add task");
    }

    await loadTasks();
    quickAddForm.reset();
    showTemporaryMessage("Task added via AI!", "success");
  } catch (err) {
    console.error("Quick-add failed:", err);
    showTemporaryMessage("Failed to add task via AI.", "error");
  }
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

async function handleToggleComplete(task) {
  try {
    await updateTaskAPI(task.id, { completed: !task.completed });
    await loadTasks();
  } catch (err) {
    console.error("Failed to toggle task completion:", err);
    alert("Failed to update task status.");
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
if (existingToken) {
  loadTasks();
  loadProjectsIntoDropdown();
}