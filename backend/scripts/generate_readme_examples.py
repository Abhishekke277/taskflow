"""
Generates 5 worked examples for the README, using the real
mock_parser.py logic — output is guaranteed accurate since it's
not hand-calculated.

Run with: python backend/scripts/generate_readme_examples.py
"""

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.ai.mock_parser import parse_task_description

examples = [
    "Call the vendor whenever you get a chance",
    "Submit invoice by next Monday",
    "urgent: fix the payment bug asap",
    "low priority - clean up old logs",
    "Review PR on Sunday",
]

print("## AI Quick-Add: Worked Examples\n")
print("| # | Input Description | Parsed Output |")
print("|---|--------------------|-----------------|")

for i, description in enumerate(examples, start=1):
    result = parse_task_description(description)
    print(f"| {i} | `{description}` | `{result}` |")