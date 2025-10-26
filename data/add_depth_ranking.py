import json5
import re

def compute_depth_and_ranking(node, is_root=False):
    if node is None or isinstance(node, str):
        # This shouldn't happen in our tree structure
        return 0, {'counts': [1]}
    else:
        min_depth = float('inf')
        ranking_counts = [0, 0]  # Start with [0, 0] like the JavaScript
        
        for score, child in node['map'].items():
            if isinstance(child, str):
                if score == '22222':
                    # Perfect score: addSelf() -> counts[0]++
                    ranking_counts[0] += 1
                    min_depth = min(min_depth, 1)
                else:
                    # Direct word match: addString() -> counts[1]++
                    ranking_counts[1] += 1
                    min_depth = min(min_depth, 1)
            else:
                # Recursive case: addRanking(child_ranking)
                child_depth, child_ranking = compute_depth_and_ranking(child, False)
                min_depth = min(min_depth, child_depth + 1)
                
                # addRanking logic: counts[i + 1] += child_ranking.counts[i]
                child_counts = child_ranking['counts']
                for i in range(len(child_counts)):
                    # Extend ranking_counts if needed
                    while len(ranking_counts) <= i + 1:
                        ranking_counts.append(0)
                    ranking_counts[i + 1] += child_counts[i]
        
        # Clean up trailing zeros like the JavaScript does
        while len(ranking_counts) > 1 and ranking_counts[-1] == 0:
            ranking_counts.pop()
            
        node['depth'] = min_depth
        node['ranking'] = {'counts': ranking_counts}
        return node['depth'], node['ranking']

def normalize_for_json5(content):
    """Normalize JavaScript object to be more json5-friendly"""
    # Quote all numeric keys to avoid mixed quoting issues
    def quote_numeric_keys(match):
        key = match.group(1)
        if key.isdigit():
            return f'"{key}":'
        return match.group(0)
    
    # Find unquoted numeric keys and quote them
    content = re.sub(r'\b(\d+):', quote_numeric_keys, content)
    return content

# Read and parse the file
import sys
filename = sys.argv[1] if len(sys.argv) > 1 else 'tarse.tree.total.js'
with open(filename, 'r', encoding='utf-8') as f:
    content = f.read()
    if content.startswith('export default '):
        content = content[len('export default '):]
    # Remove trailing semicolon and whitespace
    content = content.rstrip().rstrip(';').rstrip()
    
    # Normalize for json5 parsing
    content = normalize_for_json5(content)
    
    tree = json5.loads(content)

compute_depth_and_ranking(tree, is_root=True)

# Write back with proper formatting (restore unquoted numeric keys that don't start with 0)
def format_js(obj, indent=0):
    if isinstance(obj, str):
        return f'"{obj}"'
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, list):
        if not obj:
            return "[]"
        items = [format_js(item, indent) for item in obj]
        return "[" + ", ".join(items) + "]"
    elif isinstance(obj, dict):
        if not obj:
            return "{}"
        
        items = []
        indent_str = "    " * indent
        next_indent_str = "    " * (indent + 1)
        
        for key, value in obj.items():
            # Format key according to our rules
            if key in ['guess', 'map', 'depth', 'ranking', 'counts']:
                formatted_key = key  # unquoted for property names
            elif key.isdigit() and not key.startswith('0'):
                formatted_key = key  # unquoted for numeric keys not starting with 0
            else:
                formatted_key = f'"{key}"'  # quoted for keys starting with 0
            
            formatted_value = format_js(value, indent + 1)
            items.append(f"{next_indent_str}{formatted_key}: {formatted_value}")
        
        return "{\n" + ",\n".join(items) + "\n" + indent_str + "}"

with open(filename, 'w', encoding='utf-8') as f:
    f.write('export default ')
    f.write(format_js(tree))
    f.write(';\n')

print(f"Depth and ranking added to {filename}")