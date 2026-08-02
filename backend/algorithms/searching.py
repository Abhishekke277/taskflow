"""
Search implementations: binary search (O(log n)) and linear search (O(n)).

Binary search requires the list to be sorted first; callers are responsible
for passing a sorted list or using the convenience wrappers below which sort
via insertion_sort before searching.

Complexity:
  binary_search : O(log n) after O(n²) sort  — best for repeated searches.
  linear_search : O(n)                        — works on unsorted data, substring-friendly.
"""

from typing import Any
from backend.algorithms.sorting import insertion_sort


# ---------------------------------------------------------------------------
# Core search functions
# ---------------------------------------------------------------------------

def binary_search(
    items: list[Any], target: str, key: str | None = None
) -> int:
    """
    Iterative binary search for an *exact* match.

    Args:
        items:  A **sorted** list of dicts/objects.
        target: The value to search for.
        key:    Attribute/key name to compare against.

    Returns:
        Index of the matching element, or -1 if not found.
    """
    low, high = 0, len(items) - 1

    def get_val(item: Any) -> Any:
        if key is None:
            return item
        return item[key] if isinstance(item, dict) else getattr(item, key)

    while low <= high:
        mid = (low + high) // 2
        mid_val = get_val(items[mid])
        if mid_val == target:
            return mid
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1


def linear_search(
    items: list[Any], target: str, key: str | None = None, substring: bool = False
) -> list[int]:
    """
    Linear scan returning *all* matching indices.

    Args:
        items:     List of dicts/objects (any order).
        target:    Value or substring to search for.
        key:       Attribute/key name to compare against.
        substring: If True, check whether target appears inside the field value.

    Returns:
        List of indices where a match was found (empty list if none).
    """
    def get_val(item: Any) -> Any:
        if key is None:
            return item
        return item[key] if isinstance(item, dict) else getattr(item, key)

    results = []
    for i, item in enumerate(items):
        val = str(get_val(item))
        if substring:
            if target.lower() in val.lower():
                results.append(i)
        else:
            if val == target:
                results.append(i)
    return results


# ---------------------------------------------------------------------------
# Comparison-count wrappers (used by benchmark.py / check_algorithms.py)
# ---------------------------------------------------------------------------

def binary_search_count(
    items: list[Any], target: str, key: str | None = None
) -> tuple[int, int]:
    """
    Binary search that also counts comparisons.

    Returns:
        (found_index_or_-1, comparison_count)
    """
    low, high = 0, len(items) - 1
    comparisons = 0

    def get_val(item: Any) -> Any:
        if key is None:
            return item
        return item[key] if isinstance(item, dict) else getattr(item, key)

    while low <= high:
        mid = (low + high) // 2
        mid_val = get_val(items[mid])
        comparisons += 1
        if mid_val == target:
            return mid, comparisons
        elif mid_val < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1, comparisons


def linear_search_count(
    items: list[Any], target: str, key: str | None = None, substring: bool = False
) -> tuple[list[int], int]:
    """
    Linear search that also counts comparisons.

    Returns:
        (list_of_matching_indices, comparison_count)
    """
    def get_val(item: Any) -> Any:
        if key is None:
            return item
        return item[key] if isinstance(item, dict) else getattr(item, key)

    results = []
    comparisons = 0
    for i, item in enumerate(items):
        comparisons += 1
        val = str(get_val(item))
        if substring:
            if target.lower() in val.lower():
                results.append(i)
        else:
            if val == target:
                results.append(i)
    return results, comparisons


# ---------------------------------------------------------------------------
# Convenience wrapper: sort-then-binary-search
# ---------------------------------------------------------------------------

def sorted_binary_search(
    items: list[Any], target: str, sort_key: str | None = None
) -> int:
    """
    Sort *items* by *sort_key* using insertion_sort, then binary-search for *target*.
    Useful when the caller has an unsorted list and wants a single call.
    """
    sorted_items = insertion_sort(items, key=sort_key)
    return binary_search(sorted_items, target, key=sort_key)
