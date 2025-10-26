import re
import json
import sys

# Map B/Y/G to 0/1/2 (case-insensitive)
def convert_hint(hint):
    # Only process the first 5 characters (the actual hint pattern)
    hint_pattern = hint[:5]
    return ''.join({'B': '0', 'Y': '1', 'G': '2'}[c.upper()] for c in hint_pattern)

def parse_tree_line(line):
    """Parse a single line to extract guess-outcome pairs"""
    # Remove trailing whitespace but keep leading spaces for depth calculation
    line = line.rstrip()
    if not line.strip():
        return [], 0
    
    # Calculate depth from leading spaces (assuming 12 spaces per level)
    leading_spaces = len(line) - len(line.lstrip(' '))
    depth = leading_spaces // 12
    
    # Get the content without leading spaces
    content = line.lstrip()
    
    # Split by whitespace
    tokens = content.split()
    if not tokens:
        return [], depth
    
    pairs = []
    
    if depth == 0:
        # Root level: format is "guess outcome guess outcome ..."
        i = 0
        while i + 1 < len(tokens):
            guess = tokens[i]
            outcome = tokens[i + 1]
            if len(guess) == 5 and len(outcome) >= 5 and outcome[0] in 'BGY':
                pairs.append((guess, outcome))
            i += 2
    else:
        # Continuation level: format is "outcome1 guess1 outcome2 guess2 outcome3 ..."
        # This means: after outcome1, guess guess1 and get outcome2, then guess guess2 and get outcome3, etc.
        if len(tokens) == 1:
            # Just an outcome, no further guesses
            return [], depth
        
        i = 1  # Start from second token (first is starting outcome)
        while i + 1 < len(tokens):
            guess = tokens[i]
            outcome = tokens[i + 1]
            if len(guess) == 5 and len(outcome) >= 5 and outcome[0] in 'BGY':
                pairs.append((guess, outcome))
            i += 2
    
    return pairs, depth

def build_tree_from_paths(lines):
    """Build tree from path-based format using level numbering to determine structure"""
    if not lines:
        return {}
    
    # First, parse the entire tree to understand the structure
    root_guess = lines[0].strip().split()[0]
    root = {'guess': root_guess, 'map': {}}
    
    # Track the current path through the tree: level -> node
    path_nodes = {0: root}  # Level 0 is the root
    
    # Process all lines
    for line_num, line in enumerate(lines):
        if not line.strip():
            continue
            
        stripped = line.strip()
        tokens = stripped.split()
        
        if not tokens:
            continue
            
        # Parse all outcome-guess pairs in this line
        i = 0
        if line_num == 0:
            i = 1  # Skip root guess on first line
            
        while i < len(tokens):
            if i + 1 < len(tokens):
                # outcome guess pair
                outcome = tokens[i]
                guess = tokens[i + 1]
                
                if len(outcome) >= 6 and outcome[-1].isdigit():
                    level = int(outcome[-1])
                    clean_outcome = outcome[:-1]
                    color = convert_hint(clean_outcome)
                    
                    # Find the parent node (at level - 1)
                    parent_level = level - 1
                    if parent_level in path_nodes:
                        parent_node = path_nodes[parent_level]
                        
                        # Check if the next token indicates this is terminal
                        is_terminal = (i + 2 < len(tokens) and 
                                     len(tokens[i + 2]) >= 6 and 
                                     tokens[i + 2][:-1].startswith('GGGGG'))
                        
                        if is_terminal or clean_outcome.startswith('GGGGG'):
                            # Terminal - map directly to word
                            parent_node['map'][color] = guess
                            i += 3 if is_terminal else 2
                        else:
                            # Non-terminal - create new node
                            new_node = {'guess': guess, 'map': {}}
                            parent_node['map'][color] = new_node
                            path_nodes[level] = new_node
                            i += 2
                    else:
                        i += 2
                else:
                    i += 2
            elif i < len(tokens):
                # Just an outcome (terminal indicator)
                outcome = tokens[i]
                if len(outcome) >= 6 and outcome[-1].isdigit():
                    level = int(outcome[-1])
                    clean_outcome = outcome[:-1]
                    color = convert_hint(clean_outcome)
                    
                    # Find the parent node
                    parent_level = level - 1
                    if parent_level in path_nodes:
                        parent_node = path_nodes[parent_level]
                        # The parent's guess was the solution for this outcome
                        if 'guess' in parent_node:
                            parent_node['map'][color] = parent_node['guess']
                i += 1
            else:
                break
    
    return root

def convert_children_to_map(children):
    """Recursively convert children dict to map format"""
    map_dict = {}
    for outcome, child in children.items():
        color = convert_hint(outcome)
        if isinstance(child, dict) and 'children' in child:
            # Internal node
            child_guess = child.get('guess', 'unknown')
            map_dict[color] = {
                'guess': child_guess,
                'map': convert_children_to_map(child['children'])
            }
        else:
            # Leaf node
            map_dict[color] = child
    return map_dict
    
    return root

def main():
    if len(sys.argv) < 3:
        print('Usage: python convert_tree_to_js.py <input.tree> <output.js>')
        return
    infile = sys.argv[1]
    outfile = sys.argv[2]
    with open(infile, 'r') as f:
        lines = [line.rstrip('\n') for line in f if line.strip() and not line.strip().startswith('//')]
    
    tree = build_tree_from_paths(lines)
    
    # Custom JSON serialization to match salet format
    def custom_json_encode(obj, indent=0):
        if isinstance(obj, dict):
            if not obj:
                return "{}"
            
            items = []
            indent_str = "    " * indent
            next_indent_str = "    " * (indent + 1)
            
            for key, value in obj.items():
                # Format key - special handling for 'guess' and 'map' properties
                if key in ['guess', 'map']:
                    formatted_key = key  # unquoted for property names
                elif key.isdigit() and not key.startswith('0'):
                    formatted_key = key  # unquoted for numeric keys not starting with 0
                else:
                    formatted_key = f'"{key}"'  # quoted for keys starting with 0
                
                # Format value
                if isinstance(value, str):
                    formatted_value = f'"{value}"'
                else:
                    formatted_value = custom_json_encode(value, indent + 1)
                
                items.append(f"{next_indent_str}{formatted_key}: {formatted_value}")
            
            # Check for compact single-item maps
            if len(items) == 1 and isinstance(list(obj.values())[0], str):
                key, value = list(obj.items())[0]
                if key.isdigit() and not key.startswith('0'):
                    formatted_key = key
                else:
                    formatted_key = f'"{key}"'
                return f"{{ {formatted_key}: \"{value}\" }}"
            
            return "{\n" + ",\n".join(items) + "\n" + indent_str + "}"
        elif isinstance(obj, str):
            return f'"{obj}"'
        else:
            return str(obj)
    
    with open(outfile, 'w') as f:
        f.write('export default ')
        f.write(custom_json_encode(tree))
        f.write(';\n')

if __name__ == '__main__':
    main()
