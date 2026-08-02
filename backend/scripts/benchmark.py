"""
Benchmark script — Task 5.

Measures comparison counts for insertion_sort and binary_search across
input sizes (10, 500, 3000) and writes results to results.md.

Usage:
    python -m backend.scripts.benchmark
"""

import random
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.algorithms.sorting import insertion_sort_count
from backend.algorithms.searching import binary_search_count

SIZES = [10, 500, 3000]
RANDOM_SEED = 42


def make_tasks(n: int) -> list[dict]:
    rng = random.Random(RANDOM_SEED)
    priorities = list(range(1, 6))
    return [
        {"id": i, "title": f"Task {rng.randint(0, n * 10):07d}", "priority": rng.choice(priorities)}
        for i in range(n)
    ]


def run_benchmarks() -> list[dict]:
    results = []
    for n in SIZES:
        tasks = make_tasks(n)

        # --- Insertion sort (priority) ---
        random_tasks = list(tasks)
        _, sort_rand_cmp = insertion_sort_count(random_tasks, key="priority")

        already_sorted = sorted(tasks, key=lambda t: t["priority"])
        _, sort_best_cmp = insertion_sort_count(already_sorted, key="priority")

        worst_sorted = sorted(tasks, key=lambda t: t["priority"], reverse=True)
        _, sort_worst_cmp = insertion_sort_count(worst_sorted, key="priority")

        # --- Binary search on title (requires sorted list) ---
        sorted_by_title, _ = insertion_sort_count(tasks, key="title")
        target = sorted_by_title[n // 2]["title"]  # pick a guaranteed hit
        _, bs_cmp = binary_search_count(sorted_by_title, target, key="title")

        results.append({
            "n": n,
            "sort_best": sort_best_cmp,
            "sort_avg": sort_rand_cmp,
            "sort_worst": sort_worst_cmp,
            "binary_search": bs_cmp,
        })

        print(
            f"n={n:>5} | sort best={sort_best_cmp:>7,} avg={sort_rand_cmp:>10,} "
            f"worst={sort_worst_cmp:>10,} | binary_search={bs_cmp}"
        )

    return results


def write_results_md(results: list[dict]) -> None:
    lines = [
        "# Benchmark Results",
        "",
        "Comparison counts measured by `insertion_sort_count` and `binary_search_count`.",
        "",
        "| n | Sort (best) | Sort (avg) | Sort (worst) | Binary Search |",
        "|---|-------------|------------|--------------|---------------|",
    ]
    for r in results:
        lines.append(
            f"| {r['n']:,} | {r['sort_best']:,} | {r['sort_avg']:,} | "
            f"{r['sort_worst']:,} | {r['binary_search']} |"
        )
    lines += [
        "",
        "## Observations",
        "",
        "- **Insertion sort best case** approaches O(n): comparisons ≈ n-1 (already sorted).",
        "- **Insertion sort worst case** approaches O(n²): comparisons ≈ n(n-1)/2 (reverse sorted).",
        "- **Binary search** stays at O(log n): comparisons ≈ log₂(n) even for n=3000.",
    ]
    out_path = os.path.join(os.path.dirname(__file__), "..", "..", "results.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nWrote results to {os.path.abspath(out_path)}")


if __name__ == "__main__":
    results = run_benchmarks()
    write_results_md(results)
