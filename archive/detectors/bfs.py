from collections import deque

def detect_bfs(node, code_bytes):
    code = code_bytes.decode('utf-8')
    if node.type != "function_definition":
        return {"is_bfs": False, "confidence": 0.0}
    
    func_name = node.child_by_field_name('name').text.decode()
    
    # BFS hallmarks
    queue_usage = 0
    while_loop = 0
    neighbor_processing = 0
    
    for child in node.children:
        child_code = code[child.start_byte:child.end_byte]
        
        # Queue initialization
        if 'deque' in child_code or 'queue =' in child_code:
            queue_usage += 1
        
        # While loop with popleft()
        if child.type == 'while_statement' and 'popleft()' in child_code:
            while_loop += 1
        
        # Neighbor traversal
        if 'for' in child_code and ('neighbor' in child_code or 'adjacent' in child_code):
            neighbor_processing += 1
    
    confidence = 0.0
    if queue_usage: confidence += 0.4
    if while_loop: confidence += 0.4
    if neighbor_processing: confidence += 0.2
    
    return {
        "is_bfs": confidence >= 0.8,
        "confidence": confidence
    }