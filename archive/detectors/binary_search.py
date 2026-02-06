def detect_binary_search(node, code_bytes):
    code = code_bytes.decode()
    low_high = "low" in code and "high" in code
    mid = "mid" in code and ("//2" in code or ">>1" in code)
    loop = "while low <= high:" in code
    
    return {
        "is_binary_search": low_high and mid and loop,
        "confidence": 0.3*low_high + 0.4*mid + 0.3*loop
    }