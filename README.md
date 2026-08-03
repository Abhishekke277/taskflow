Algorithm Complexity & Benchmark Analysis

Time Complexity:

insertion_sort: Best case O(n) — already-sorted input, one comparison per element. Worst case O(n²) — reverse-sorted input, each element compared against and shifted past all previously placed elements.
binary_search: Best case O(1) — target found at the middle index immediately. Worst case O(log n) — search space halves each iteration until exhausted.
linear_search: Best case O(1) — target is the first element checked. Worst case O(n) — target is last or absent, requiring a full scan.

Is sorting-first worth it?

Our benchmark confirms the theoretical complexity: sorting 3,000 tasks with insertion_sort took 1,820,009 comparisons, while searching that same sorted list with binary_search took only 12 comparisons — versus 3,000 comparisons for linear_search on unsorted data. Given TaskFlow's real usage pattern — a team listing/sorting tasks repeatedly throughout the day, while adding or renaming tasks comparatively rarely — paying the steep one-time O(n²) sorting cost is justified whenever the sorted list can be reused across multiple reads (e.g. a session cache), since each subsequent binary search stays near-constant even as the dataset grows into the thousands. However, if GET /tasks?sort=priority re-sorts from scratch on every single request without caching, the O(n²) cost is paid repeatedly, and at 3,000+ tasks this becomes the dominant cost of the endpoint — in that case, a database-level ORDER BY (O(n log n), or effectively free with an index) would outperform our hand-rolled sort at scale, even though the assignment intentionally requires implementing it manually here.


## AI Quick-Add: Prompting Technique Rationale

The quick-add feature's system message and mock parser are modeled on a **zero-shot** prompting approach, rather than few-shot or chain-of-thought.

The system message directly states the extraction task and the exact output format expected (title, priority, due_date_hint) without providing worked examples inside the prompt itself. This was chosen for three reasons specific to TaskFlow's use case:

1. **Token efficiency.** Few-shot prompting requires embedding several example input/output pairs directly in every request, which multiplies token usage on every single quick-add call — a cost that adds up quickly for a feature meant to be used dozens of times a day across a team. Zero-shot keeps the system message short and constant.

2. **Deterministic domain, not open-ended reasoning.** Chain-of-thought prompting is most valuable when a task benefits from step-by-step reasoning over ambiguous or multi-step problems. Task parsing here is a narrow, rule-based classification task (keyword matching for priority and date phrases) — it doesn't benefit from a model "thinking out loud," and forcing that would only inflate token usage without improving reliability.

3. **Reliability via explicit rules, not model inference.** Because the actual parsing logic is deterministic (see `mock_parser.py`), the system message's role is really to document intended behavior for a future real-LLM integration — not to carry the reasoning burden itself. A zero-shot instruction that precisely enumerates the exact fields and rules is more reliable here than relying on the model to infer structure from examples, since our fallback (the mock) already guarantees correctness regardless of what a real LLM would produce.

If TaskFlow later needed to handle more ambiguous, free-form task descriptions (e.g. instructions requiring inference about implied urgency), a few-shot approach with 2-3 worked examples embedded in the prompt would likely improve reliability at the cost of higher token usage per call.

## AI Quick-Add: Worked Examples

| # | Input Description | Parsed Output |
|---|--------------------|-----------------|
| 1 | `Call the vendor whenever you get a chance` | `{'title': 'Call the vendor  you get a chance', 'priority': 'low', 'due_date_hint': None}` |
| 2 | `Submit invoice by next Monday` | `{'title': 'Submit invoice by', 'priority': 'medium', 'due_date_hint': 'next monday'}` |
| 3 | `urgent: fix the payment bug asap` | `{'title': ': fix the payment bug', 'priority': 'high', 'due_date_hint': None}` |
| 4 | `low priority - clean up old logs` | `{'title': '- clean up old logs', 'priority': 'low', 'due_date_hint': None}` |
| 5 | `Review PR on Sunday` | `{'title': 'Review PR on', 'priority': 'medium', 'due_date_hint': 'sunday'}` |