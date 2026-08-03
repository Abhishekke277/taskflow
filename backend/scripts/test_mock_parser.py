"""
Quick manual verification of mock_parser.py against the 4 worked
examples from the brief. Run with:
    python backend/scripts/test_mock_parser.py
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.ai.mock_parser import parse_task_description

test_cases = [
    {
        "input": "This is urgent, mark it ASAP please",
        "expected": {"title": "This is , mark it  please", "priority": "high", "due_date_hint": None},
    },
    {
        "input": " ",
        "expected": {"title": "Untitled task", "priority": "medium", "due_date_hint": None},
    },
    {
        "input": "Finish the report next Friday, it's urgent",
        "expected": {"title": "Finish the report , it's", "priority": "high", "due_date_hint": "next friday"},
    },
    {
        "input": "tomorrow review tomorrow",
        "expected": {"title": "review", "priority": "medium", "due_date_hint": "tomorrow"},
    },
]

for i, case in enumerate(test_cases, start=1):
    result = parse_task_description(case["input"])
    # Normalize whitespace for comparison since exact spacing after
    # removal can have double spaces — we compare against the
    # brief's exact expected strings including that spacing
    match = result == case["expected"]

    status = "PASS" if match else "FAIL"
    print(f"{status}: Example {i} — input: {case['input']!r}")
    print(f"  expected: {case['expected']}")
    print(f"  got:      {result}")
    print()