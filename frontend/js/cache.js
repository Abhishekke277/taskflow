const CACHE_KEY = "taskflow_cached_tasks";

/**
 * Saves the current task list to localStorage as a JSON string.
 * Called every time the task list changes.
 */
function saveTasksToCache(tasks) {
  localStorage.setItem(CACHE_KEY, JSON.stringify(tasks));
}

/**
 * Reads the cached task list from localStorage.
 * Returns an empty array if nothing is cached yet.
 */
function loadTasksFromCache() {
  const cached = localStorage.getItem(CACHE_KEY);
  if (!cached) return [];
  try {
    return JSON.parse(cached);
  } catch {
    return [];
  }
}