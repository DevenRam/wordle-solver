import re

def compute_depth_and_ranking(node, current_depth=0):
    """Compute depth and ranking for each node in the tree"""
    if isinstance(node, str):
        # Leaf node: word is found at this depth
        # Return depth=1 (1 more step needed) and counts=[1] (1 word solvable in 1 step)
        return 1, [1]
    
    if not isinstance(node, dict) or 'map' not in node:
        return 1, [1]
    
    # Internal node: compute from children
    min_depth = float('inf')
    total_counts = []
    
    for outcome, child in node['map'].items():
        child_depth, child_counts = compute_depth_and_ranking(child, current_depth + 1)
        min_depth = min(min_depth, child_depth)
        
        # Extend total_counts array as needed to accommodate child_counts + 1 position
        needed_length = len(child_counts) + 1
        while len(total_counts) < needed_length:
            total_counts.append(0)
        
        # Add child counts to total, shifting by 1 position since we need one more step
        for i, count in enumerate(child_counts):
            total_counts[i + 1] += count
    
    # Remove trailing zeros (but keep at least one element)
    while len(total_counts) > 1 and total_counts[-1] == 0:
        total_counts.pop()
    
    # The depth is the minimum steps needed to solve any word from this node
    node_depth = min_depth + 1
    
    # Add depth and ranking to the node
    node['depth'] = min_depth
    node['ranking'] = {'counts': total_counts}
    
    return node_depth, total_counts

def parse_js_object(content):
    """Simple parser for JavaScript object literals"""
    # This is a simplified parser - for production use, you'd want a proper JS parser
    # But for our specific format, this should work
    
    # Remove export default and trailing semicolon
    content = content.strip()
    if content.startswith('export default '):
        content = content[len('export default '):]
    content = content.rstrip(';').strip()
    
    # Use eval with some safety (only for trusted input!)
    # Replace unquoted keys with quoted keys for Python
    def quote_keys(match):
        key = match.group(1)
        if key.isdigit() or key in ['guess', 'map', 'depth', 'ranking', 'counts']:
            return f'"{key}":'
        return match.group(0)
    
    # Quote unquoted property names
    content = re.sub(r'(\w+):', quote_keys, content)
    
    # Replace JavaScript object syntax with Python dict syntax
    content = content.replace('true', 'True').replace('false', 'False').replace('null', 'None')
    
    try:
        return eval(content)
    except:
        print("Failed to parse JavaScript object. Using alternative approach...")
        return None

def format_js_output(obj, indent=0):
    """Format Python object back to JavaScript syntax matching our style"""
    if isinstance(obj, str):
        return f'"{obj}"'
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, list):
        if not obj:
            return "[]"
        items = [format_js_output(item, indent) for item in obj]
        if len(obj) <= 3:  # Short arrays on one line
            return "[" + ", ".join(items) + "]"
        else:
            indent_str = "    " * (indent + 1)
            return "[\n" + indent_str + f",\n{indent_str}".join(items) + "\n" + ("    " * indent) + "]"
    elif isinstance(obj, dict):
        if not obj:
            return "{}"
        
        items = []
        indent_str = "    " * indent
        next_indent_str = "    " * (indent + 1)
        
        for key, value in obj.items():
            # Format key - same logic as convert_tree_to_js.py
            if key in ['guess', 'map', 'depth', 'ranking', 'counts']:
                formatted_key = key  # unquoted for property names
            elif key.isdigit() and not key.startswith('0'):
                formatted_key = key  # unquoted for numeric keys not starting with 0
            else:
                formatted_key = f'"{key}"'  # quoted for keys starting with 0
            
            formatted_value = format_js_output(value, indent + 1)
            items.append(f"{next_indent_str}{formatted_key}: {formatted_value}")
        
        # Handle compact single-item maps
        if len(items) == 1 and isinstance(list(obj.values())[0], str):
            key, value = list(obj.items())[0]
            if key.isdigit() and not key.startswith('0'):
                formatted_key = key
            else:
                formatted_key = f'"{key}"'
            return f"{{ {formatted_key}: \"{value}\" }}"
        
        return "{\n" + ",\n".join(items) + "\n" + indent_str + "}"
    else:
        return str(obj)

# Read the current file
with open('tarse.tree.total.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Parse the JavaScript object
tree = parse_js_object(content)

if tree is None:
    print("Failed to parse the file. Please check the format.")
    exit(1)

# Compute depth and ranking
print("Computing depth and ranking...")
compute_depth_and_ranking(tree)

# Write back the updated tree
with open('tarse.tree.total.js', 'w', encoding='utf-8') as f:
    f.write('export default ')
    f.write(format_js_output(tree))
    f.write(';\n')

print("Depth and ranking added to tarse.tree.total.js")