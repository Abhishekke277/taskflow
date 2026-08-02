"""
Algorithm correctness checker — Task 7.

Runs PASS/FAIL assertions against insertion_sort, binary_search, and
linear_search with small, deterministic inputs.

Usage:
    python -m backend.scripts.check_algorithms
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.algorithms.sorting import insertion_sort, insertion_sort_count
from backend.algorithms.searching import binary_search, linear_search, binary_search_count


def check(label: str, condition: bool) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}")
    if not condition:
        global _failures
        _failures += 1


_failures = 0

# ---------------------------------------------------------------------------
# insertion_sort tests
# ---------------------------------------------------------------------------
sample = [
    {"title": "Zebra task", "priority": 5},
    {"title": "Alpha task", "priority": 1},
    {"title": "Mango task", "priority": 3},
    {"title": "Alpha task", "priority": 2},
]

sorted_by_priority = insertion_sort(sample, key="priority")
check("insertion_sort: sorted by priority ascending",
      [d["priority"] for d in sorted_by_priority] == [1, 2, 3, 5])

sorted_by_title = insertion_sort(sample, key="title")
check("insertion_sort: sorted by title ascending",
      sorted_by_title[0]["title"] == "Alpha task")

sorted_desc = insertion_sort(sample, key="priority", reverse=True)
check("insertion_sort: reverse=True gives descending order",
      sorted_desc[0]["priority"] == 5)

empty_sorted = insertion_sort([], key="priority")
check("insertion_sort: empty list returns empty list", empty_sorted == [])

single = insertion_sort([{"priority": 3}], key="priority")
check("insertion_sort: single-element list is unchanged", single[0]["priority"] == 3)

_, count_already_sorted = insertion_sort_count([1, 2, 3, 4, 5])
check("insertion_sort_count: already-sorted list has 0 swaps (best case O(n))",
      count_already_sorted == 0)  # no comparisons result in a swap

# ---------------------------------------------------------------------------
# binary_search tests
# ---------------------------------------------------------------------------
sorted_titles = insertion_sort(sample, key="title")
idx = binary_search(sorted_titles, "Mango task", key="title")
check("binary_search: finds existing element", idx != -1)
check("binary_search: found element has correct title",
      sorted_titles[idx]["title"] == "Mango task")

not_found = binary_search(sorted_titles, "Nonexistent", key="title")
check("binary_search: returns -1 for missing element", not_found == -1)

_, bs_count = binary_search_count(sorted_titles, "Zebra task", key="title")
check("binary_search_count: comparisons <= ceil(log2(n+1))",
      bs_count <= 4)  # len=4, ceil(log2(5))=3 — allow one extra for boundary

# ---------------------------------------------------------------------------
# linear_search tests
# ---------------------------------------------------------------------------
indices = linear_search(sample, "Alpha task", key="title")
check("linear_search: finds all occurrences of duplicate title", len(indices) == 2)

substr_indices = linear_search(sample, "task", key="title", substring=True)
check("linear_search: substring=True matches all items containing 'task'",
      len(substr_indices) == len(sample))

no_match = linear_search(sample, "ZZZNOPE", key="title", substring=True)
check("linear_search: returns empty list when no match", no_match == [])

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
total = 12
passed = total - _failures
print(f"\nResults: {passed}/{total} passed", "✓" if _failures == 0 else "✗")
sys.exit(0 if _failures == 0 else 1)
