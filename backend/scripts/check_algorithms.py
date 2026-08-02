"""
Automated PASS/FAIL checks for the algorithms engine.
Run with: python backend/scripts/check_algorithms.py
"""

import sys
import os

# Allows this script to import from backend/ when run directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.algorithms.sorting import insertion_sort, insertion_sort_count
from backend.algorithms.searching import binary_search, binary_search_count, linear_search_count


def check(case_name, result, expected):
    if result == expected:
        print(f"PASS: {case_name}")
    else:
        print(f"FAIL: {case_name} — expected {expected}, got {result}")


# ── Case 1: insertion_sort on empty list leaves it empty, no error ──
empty_list = []
insertion_sort(empty_list, key="value")
check("insertion_sort empty list", empty_list, [])

# ── Case 2: insertion_sort on single-element list unchanged ──
single_item = [{"value": 5}]
insertion_sort(single_item, key="value")
check("insertion_sort single element", single_item, [{"value": 5}])

# ── Case 3: binary_search finds value at first, last, and middle ──
sorted_list = [
    {"value": 10}, {"value": 20}, {"value": 30}, {"value": 40}, {"value": 50}
]

result_first = binary_search(sorted_list, 10, key="value")
check("binary_search finds first index", result_first, 0)

result_last = binary_search(sorted_list, 50, key="value")
check("binary_search finds last index", result_last, 4)

result_middle = binary_search(sorted_list, 30, key="value")
check("binary_search finds middle index", result_middle, 2)

# ── Case 4: binary_search returns not-found (-1) when target absent ──
result_absent = binary_search(sorted_list, 999, key="value")
check("binary_search absent value returns -1", result_absent, -1)

# ── Case 5: insertion_sort_count sorts correctly and returns int > 0 ──
small_list = [{"value": 3}, {"value": 1}, {"value": 2}]
count_result = insertion_sort_count(small_list, key="value")

sorted_correctly = small_list == [{"value": 1}, {"value": 2}, {"value": 3}]
check("insertion_sort_count sorts correctly", sorted_correctly, True)

is_positive_int = isinstance(count_result, int) and count_result > 0
check("insertion_sort_count returns positive int", is_positive_int, True)

# ── Case 6: binary_search_count returns correct index + comparison_count > 0 ──
sorted_list_2 = [
    {"value": 10}, {"value": 20}, {"value": 30}, {"value": 40}, {"value": 50}
]
search_result = binary_search_count(sorted_list_2, 30, key="value")

check("binary_search_count returns correct index", search_result["index"], 2)
comparison_positive = search_result["comparison_count"] > 0
check("binary_search_count comparison_count > 0", comparison_positive, True)

# ── Case 7: linear_search_count on absent value — index not-found, count == len ──
unsorted_list = [{"value": 5}, {"value": 15}, {"value": 25}]
absent_result = linear_search_count(unsorted_list, 999, key="value")

check("linear_search_count absent index is -1", absent_result["index"], -1)
check(
    "linear_search_count absent comparison_count equals list length",
    absent_result["comparison_count"],
    len(unsorted_list),
)

print("\nAll checks completed.")