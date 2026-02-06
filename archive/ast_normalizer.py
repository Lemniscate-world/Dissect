import re

def extract_identifier(node):
    if hasattr(node, 'name'):
        return node.name
    if hasattr(node, 'text'):
        return node.text
    if hasattr(node, 'value'):
        return node.value
    if hasattr(node, 'type'):
        return node.type
    if hasattr(node, 'code'):
        return node.code
    
    # Extract identifier from children
    for child in node.children:
        identifier = extract_identifier(child)
        if identifier:
            return identifier
    
    # Extract identifier from string literals
    for child in node.children:
        if hasattr(child, 'type') and child.type =='string_literal':
            return child.text
    
    # Extract identifier from array elements
    for child in node.children:
        if hasattr(child, 'type') and child.type == 'array_element_expression':
            identifier = extract_identifier(child.child_by_field_name('expression'))
            if identifier:
                return identifier
    
    # Extract identifier from object properties
    for child in node.children:
        if hasattr(child, 'type') and child.type == 'object_property':
            identifier = extract_identifier(child.child_by_field_name('value'))
            if identifier:
                return identifier
    
    # Extract identifier from function calls
    for child in node.children:
        if hasattr(child, 'type') and child.type == 'call_expression':
            return 'function_call'
    
    # Extract identifier from member expressions
    for child in node.children:
        if hasattr(child, 'type') and child.type == 'member_expression':
            return 'member_access'
    
    # Extract identifier from function arguments
    for child in node.children:
        if hasattr(child, 'type') and child.type == 'argument':
            return 'argument'
        
    return None

def detect_operations(node):
    operations = []
    
    # Binary operators
    for child in node.children:
        if hasattr(child, 'type') and child.type in ['binary_expression', 'assignment_expression']:
            operator = child.child_by_field_name('operator').text
            if operator:
                operations.append(operator)
    
    # Unary operators
    for child in node.children:
        if hasattr(child, 'type') and child.type in ['unary_expression']:
            operator = child.child_by_field_name('operator').text
            if operator:
                operations.append(operator)
    
    # Ternary operators
    for child in node.children:
        if hasattr(child, 'type') and child.type == 'ternary_expression':
            operations.append('ternary')
    
    # Logical operators
    for child in node.children:
        if hasattr(child, 'type') and child.type in ['logical_expression']:
            for operator in ['&&', '||', '?', ':']:
                if operator in child.code:
                    operations.append(operator)
    
    # Other operators
    for child in node.children:
        if hasattr(child, 'type') and child.type in ['call_expression', 'member_expression']:
            operations.append('call')
    
    # Array/list operations
    for child in node.children:
        if hasattr(child, 'type') and child.type in ['array_expression', 'object_expression']:
            operations.append('array_access')
    
    # String operations
    for child in node.children:
        if hasattr(child, 'type') and child.type == 'string_literal':
            operations.append('string_concatenation')
    
    # Template literals
    for child in node.children:
        if hasattr(child, 'type') and child.type == 'template_literal':
            operations.append('template_literal')
    
    # Arrow function operations
    for child in node.children:
        if hasattr(child, 'type') and child.type == 'arrow_function':
            operations.append('arrow_function')
    
    # Class expression
    for child in node.children:
        if hasattr(child, 'type') and child.type == 'class_declaration':
            operations.append('class_expression')
    
    # Function expression
    for child in node.children:
        if hasattr(child, 'type') and child.type == 'function_declaration':
            operations.append('function_expression')   
    
    # Destructuring assignments
    for child in node.children:
        if hasattr(child, 'type') and child.type == 'assignment_expression' and child.child_by_field_name('left').type == 'object_pattern':
            operations.append('destructuring_assignment')
    
    # Await expression
    for child in node.children:
        if hasattr(child, 'type') and child.type == 'await_expression':
            operations.append('await')
    
    return operations

def normalize_ast(node):
    # Normalize AST node into a language-agnostic format
    if not hasattr(node, 'type'):
        return None
    
    return {
        'type': NODE_TYPE_MAP.get(node.type, 'generic'),
        'name': extract_identifier(node),
        'children': [normalize_ast(c) for c in node.children],
        'operations': detect_operations(node)
    }

NODE_TYPE_MAP = {
    # Python
    'function_definition': 'function',
    'for_statement': 'loop_block',
    
    # JavaScript
    'function_declaration': 'function',
    'for_statement': 'loop_block',
    
    # Java
    'method_declaration': 'function'
}