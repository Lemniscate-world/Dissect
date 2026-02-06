def detect_mergesort(node, code_bytes):
    code = code_bytes.decode()
    has_split = "//2" in code or ">>1" in code  # Midpoint calculation
    has_merge = "merge(" in code  # Merge helper call
    has_recursion = "mergesort(" in code
    
    return {
        "is_mergesort": has_split and has_merge and has_recursion,
        "confidence": 0.9 if (has_split and has_merge) else 0.2
    }