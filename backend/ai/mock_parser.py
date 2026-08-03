def parse_task_description(description: str) -> dict:
    """
    Deterministic, rule-based mock parser. Simulates what an LLM
    response would contain, given a free-text task description.
    Runs with zero network calls and zero API keys.

    Returns a dict with: title, priority, due_date_hint
    """
    original_description = description
    lowered = description.lower()

    # ── Step b: Priority ──
    # Group (i) keywords — checked first, "high" wins if present
    high_keywords = ["urgent", "asap"]
    # Group (ii) keywords — checked second
    low_keywords = ["whenever", "low priority"]

    matched_high = [kw for kw in high_keywords if kw in lowered]
    matched_low = [kw for kw in low_keywords if kw in lowered]

    if matched_high:
        priority = "high"
    elif matched_low:
        priority = "low"
    else:
        priority = "medium"

    # ── Step c: Due-date hint ──
    # Checked in this exact order: today, tomorrow, next week,
    # then "next <weekday>" (Mon-Sun), then bare weekday (Mon-Sun)
    due_date_hint = None
    matched_date_phrase = None

    simple_date_keywords = ["today", "tomorrow", "next week"]
    for keyword in simple_date_keywords:
        if keyword in lowered:
            due_date_hint = keyword
            matched_date_phrase = keyword
            break

    if due_date_hint is None:
        next_weekday_phrases = [
            "next monday", "next tuesday", "next wednesday", "next thursday",
            "next friday", "next saturday", "next sunday",
        ]
        for phrase in next_weekday_phrases:
            if phrase in lowered:
                due_date_hint = phrase
                matched_date_phrase = phrase
                break

    if due_date_hint is None:
        bare_weekdays = [
            "monday", "tuesday", "wednesday", "thursday",
            "friday", "saturday", "sunday",
        ]
        for day in bare_weekdays:
            if day in lowered:
                due_date_hint = day
                matched_date_phrase = day
                break

    # ── Step d: Title ──
    # Remove every occurrence of every group (i)/(ii) keyword found,
    # plus every occurrence of the matched date phrase (if any),
    # from the ORIGINAL-cased description. Case-insensitive removal.
    title = original_description

    all_priority_keywords_found = matched_high + matched_low
    for keyword in all_priority_keywords_found:
        title = _remove_case_insensitive(title, keyword)

    if matched_date_phrase:
        title = _remove_case_insensitive(title, matched_date_phrase)

    title = title.strip()

    if not title:
        title = "Untitled task"

    return {
        "title": title,
        "priority": priority,
        "due_date_hint": due_date_hint,
    }


def _remove_case_insensitive(text: str, phrase: str) -> str:
    """
    Removes every occurrence of `phrase` from `text`, matching
    case-insensitively but preserving the original casing of
    the surrounding text that isn't removed.
    """
    import re
    pattern = re.compile(re.escape(phrase), re.IGNORECASE)
    return pattern.sub("", text)