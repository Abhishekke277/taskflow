"""
Insertion Sort implementation with optional comparison counter.

Complexity:
  Best case  : O(n)   — already-sorted input; inner while never executes.
  Average    : O(n²)  — each element shifts past ~half the sorted prefix.
  Worst case : O(n²)  — reverse-sorted input; every element shifts all the way.
  Space      : O(1)   — in-place, only a constant amount of extra memory.
"""

from typing import Any


def insertion_sort(items: list[Any], key: str | None = None, reverse: bool = False) -> list[Any]:
    """
    Sort *items* in-place using insertion sort and return the sorted list.

    Args:
        items:   List of dicts (or objects) to sort.
        key:     Attribute/key name to sort by. If None, items are compared directly.
        reverse: If True, sort in descending order.
    """
    arr = list(items)  # work on a copy so callers keep original order if needed

    def get_val(item: Any) -> Any:
        if key is None:
            return item
        return item[key] if isinstance(item, dict) else getattr(item, key)

    for i in range(1, len(arr)):
        current = arr[i]
        j = i - 1
        if not reverse:
            while j >= 0 and get_val(arr[j]) > get_val(current):
                arr[j + 1] = arr[j]
                j -= 1
        else:
            while j >= 0 and get_val(arr[j]) < get_val(current):
                arr[j + 1] = arr[j]
                j -= 1
        arr[j + 1] = current

    return arr


def insertion_sort_count(
    items: list[Any], key: str | None = None, reverse: bool = False
) -> tuple[list[Any], int]:
    """
    Same as insertion_sort but also returns the number of comparisons made.
    Used by benchmark.py to measure algorithmic work empirically.

    Returns:
        (sorted_list, comparison_count)
    """
    arr = list(items)
    comparisons = 0

    def get_val(item: Any) -> Any:
        if key is None:
            return item
        return item[key] if isinstance(item, dict) else getattr(item, key)

    for i in range(1, len(arr)):
        current = arr[i]
        j = i - 1
        if not reverse:
            while j >= 0:
                comparisons += 1
                if get_val(arr[j]) > get_val(current):
                    arr[j + 1] = arr[j]
                    j -= 1
                else:
                    break
        else:
            while j >= 0:
                comparisons += 1
                if get_val(arr[j]) < get_val(current):
                    arr[j + 1] = arr[j]
                    j -= 1
                else:
                    break
        arr[j + 1] = current

    return arr, comparisons
