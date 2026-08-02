"""
Benchmark script — runs the counting-wrapper functions against
synthetic in-memory task data at three sizes (10, 500, 3000) and
prints/saves the raw comparison counts.

Run with: python backend/scripts/benchmark.py
"""

import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.algorithms.sorting import insertion_sort_count
from backend.algorithms.searching import binary_search_count, linear_search_count

PRIORITIES = ["low", "medium", "high"]
DUE_DATE_OPTIONS = ["today", "tomorrow", "next week", "next friday", None]


def generate_synthetic_tasks(count):
    """
    Generates synthetic task dicts using the exact same fields as
    the real tasks table: title, priority, due_date.
    """
    tasks = []
    for i in range(count):
        tasks.append({
            "title": f"Task {i}",
            "priority": random.choice(PRIORITIES),
            "due_date": random.choice(DUE_DATE_OPTIONS),
        })
    return tasks


def run_benchmark_for_size(size):
    print(f"\n--- Data size: {size} ---")

    # ── Sorting benchmark ──
    # Fresh copy each time since insertion_sort_count mutates in place
    tasks_for_sort = generate_synthetic_tasks(size)
    sort_comparisons = insertion_sort_count(tasks_for_sort, key="title")
    print(f"insertion_sort_count on {size} tasks (by title): {sort_comparisons} comparisons")

    # ── Search benchmark: binary (on the now-sorted list) ──
    # Pick a target that exists (last element after sort, to get a
    # realistic near-worst-case for binary search too)
    target_title = tasks_for_sort[-1]["title"]
    binary_result = binary_search_count(tasks_for_sort, target_title, key="title")
    print(f"binary_search_count for existing title: {binary_result}")

    # ── Search benchmark: linear (on unsorted data, worst case — absent value) ──
    tasks_for_linear = generate_synthetic_tasks(size)
    linear_result = linear_search_count(tasks_for_linear, "NON_EXISTENT_TITLE_XYZ", key="title")
    print(f"linear_search_count for absent title: {linear_result}")

    return {
        "size": size,
        "insertion_sort_comparisons": sort_comparisons,
        "binary_search_comparisons": binary_result["comparison_count"],
        "linear_search_comparisons": linear_result["comparison_count"],
    }


def main():
    sizes = [10, 500, 3000]
    results = []

    print("Running algorithm benchmarks on synthetic task data...")

    for size in sizes:
        results.append(run_benchmark_for_size(size))

    # Save raw results to a markdown file for the README
    output_path = os.path.join(os.path.dirname(__file__), "..", "results", "benchmark_results.md")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        f.write("# Benchmark Results\n\n")
        f.write("Synthetic in-memory task data (title, priority, due_date fields).\n\n")
        f.write("| Size | insertion_sort comparisons | binary_search comparisons | linear_search comparisons |\n")
        f.write("|------|------------------------------|-----------------------------|------------------------------|\n")
        for r in results:
            f.write(
                f"| {r['size']} | {r['insertion_sort_comparisons']} | "
                f"{r['binary_search_comparisons']} | {r['linear_search_comparisons']} |\n"
            )

    print(f"\nResults saved to {output_path}")


if __name__ == "__main__":
    main()