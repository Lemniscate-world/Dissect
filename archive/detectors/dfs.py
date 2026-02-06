def detect_dfs(node, code_bytes):
    code = code_bytes.decode('utf-8')
    if node.type != "function_definition":
        return {"is_dfs": False, "confidence": 0.0}
    
    func_name = node.child_by_field_name('name').text.decode()
    
    # DFS hallmarks
    stack_usage = 0
    recursive_calls = 0
    backtracking = 0
    
    has_visited = "visited" in code or "seen" in code
    has_neighbor_traversal = any(
        keyword in code 
        for keyword in ["neighbors", "children", "adjacent"]
    )
    
    for child in node.children:
        child_code = code[child.start_byte:child.end_byte]
        
        # Stack initialization (LIFO)
        if 'stack' in child_code and ('append' in child_code or 'pop()' in child_code):
            stack_usage += 1
        
        # Recursive calls (for recursive DFS)
        if f"{func_name}(" in child_code:
            recursive_calls += 1
        
        # Backtracking patterns
        if 'visited.remove' in child_code or 'path.pop' in child_code:
            backtracking += 1
    
    confidence = 0.0
    if (stack_usage or recursive_calls) and (has_visited or has_neighbor_traversal):
        confidence += 0.7
    if backtracking:
        confidence += 0.3

    return {"is_dfs": confidence >= 0.7, "confidence": confidence}