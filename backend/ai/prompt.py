def build_quick_add_prompt(description: str) -> dict:
    """
    Constructs the "prompt" using the standard role-based structure
    for LLM messaging — a system-role instruction describing the
    parsing behavior, and a user-role message carrying the free-text
    description. Used even though the mock parser answers it, so the
    code is structured identically whether a mock or a real model
    handles the request.
    """
    system_message = (
        "You are a task-parsing assistant. Given a free-text task "
        "description, extract three fields: "
        "1) title — the task description with any priority or "
        "date-related keywords removed, trimmed of whitespace; "
        "2) priority — exactly one of 'low', 'medium', or 'high', "
        "based on urgency keywords in the text; "
        "3) due_date_hint — a date phrase found in the text (e.g. "
        "'tomorrow', 'next friday'), or null if none is present. "
        "Respond with these three fields only."
    )

    user_message = description

    return {
        "system": system_message,
        "user": user_message,
    }