def estimate_complexity(algorithm):
    complexity_map = {
        "Quicksort": "O(n log n)",
        "BFS": "O(V + E)",
        "DFS": "O(V + E)",  # Added DFS complexity
        "Binary Search": "O(log n)",
    }
    return complexity_map.get(algorithm, "Unknown")
