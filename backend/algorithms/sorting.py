def insertion_sort(records, key):
    """
    Sorts a list of dictionaries in place by the value at record[key],
    using the standard insertion-sort algorithm: starting from the
    second element, comparing against previous elements, and shifting
    elements to insert each one into its correct position.

    Mutates `records` directly. No return value needed.
    """
    for i in range(1, len(records)):
        current = records[i]
        j = i - 1

        # Shift elements greater than current one position to the right
        while j >= 0 and records[j][key] > current[key]:
            records[j + 1] = records[j]
            j -= 1

        records[j + 1] = current


def insertion_sort_count(records, key):
    """
    Identical logic to insertion_sort — sorts `records` in place by
    record[key] — but returns only a single integer: the number of
    comparisons performed. Used for the Task 5 benchmark, not for
    the live endpoints.
    """
    comparison_count = 0

    for i in range(1, len(records)):
        current = records[i]
        j = i - 1

        while j >= 0:
            comparison_count += 1  # counts the comparison in the while condition
            if records[j][key] > current[key]:
                records[j + 1] = records[j]
                j -= 1
            else:
                break

        records[j + 1] = current

    return comparison_count