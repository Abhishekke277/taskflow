def binary_search(sorted_records, target_value, key):
    """
    Operates on a list already sorted by key (as produced by
    insertion_sort). Returns the index of a record whose
    record[key] == target_value, or -1 if no such record exists.

    Standard low/high/mid pointer implementation.
    """
    low = 0
    high = len(sorted_records) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_value = sorted_records[mid][key]

        if mid_value == target_value:
            return mid
        elif mid_value < target_value:
            low = mid + 1
        else:
            high = mid - 1

    return -1  # not found


def linear_search(records, target_value, key):
    """
    Baseline search: scans every record in order and returns the
    index of the first match, or -1 if absent. Does not require
    the list to be sorted.
    """
    for index, record in enumerate(records):
        if record[key] == target_value:
            return index

    return -1  # not found


def binary_search_count(sorted_records, target_value, key):
    """
    Identical logic to binary_search, but returns a dictionary with
    exactly two keys: "index" and "comparison_count". Used for the
    Task 5 benchmark, not the live endpoints.
    """
    low = 0
    high = len(sorted_records) - 1
    comparison_count = 0

    while low <= high:
        mid = (low + high) // 2
        mid_value = sorted_records[mid][key]
        comparison_count += 1  # one comparison per loop iteration

        if mid_value == target_value:
            return {"index": mid, "comparison_count": comparison_count}
        elif mid_value < target_value:
            low = mid + 1
        else:
            high = mid - 1

    return {"index": -1, "comparison_count": comparison_count}


def linear_search_count(records, target_value, key):
    """
    Identical logic to linear_search, but returns a dictionary with
    exactly two keys: "index" and "comparison_count".
    """
    comparison_count = 0

    for index, record in enumerate(records):
        comparison_count += 1  # one comparison per element checked
        if record[key] == target_value:
            return {"index": index, "comparison_count": comparison_count}

    return {"index": -1, "comparison_count": comparison_count}