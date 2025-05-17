import re
import json
import sys

# Map B/Y/G to 0/1/2 (case-insensitive)
def convert_hint(hint):
    return ''.join({'B': '0', 'Y': '1', 'G': '2'}[c.upper()] for c in hint)

def parse_nodes(lines, col=0, start=0, end=None):
    COL_WIDTH = 12
    if end is None:
        end = len(lines)
    nodes = []
    i = start
    while i < end:
        line = lines[i]
        padded = line.ljust((col+1)*COL_WIDTH)
        col_text = padded[col*COL_WIDTH:(col+1)*COL_WIDTH]
        guess = col_text[:5].strip()
        outcome = col_text[6:12].strip()
        if not (guess and outcome):
            i += 1
            continue
        # Find the region for this node's subtree
        subtree_start = i
        i += 1
        while i < end:
            next_line = lines[i]
            next_padded = next_line.ljust((col+1)*COL_WIDTH)
            next_col_text = next_padded[col*COL_WIDTH:(col+1)*COL_WIDTH]
            next_guess = next_col_text[:5].strip()
            next_outcome = next_col_text[6:12].strip()
            if next_guess and next_outcome:
                break  # next sibling at this level
            i += 1
        # Recursively parse children in the next column
        children = parse_nodes(lines, col+1, subtree_start, i)
        nodes.append({
            'guess': guess,
            'outcome': outcome,
            'children': children
        })
    return nodes

def build_js_tree(nodes):
    # nodes: list of dicts with 'guess', 'outcome', 'children'
    if not nodes:
        return {}
    root = nodes[0]
    def build(node):
        color = convert_hint(node['outcome'][:5])
        # If no children, this is a leaf
        if not node['children']:
            return node['guess']
        # Otherwise, build children map
        child_map = {}
        for child in node['children']:
            child_color = convert_hint(child['outcome'][:5])
            child_map[child_color] = build(child)
        return {'guess': node['guess'], 'map': child_map}
    return build(root)

def main():
    if len(sys.argv) < 3:
        print('Usage: python convert_tree_to_js.py <input.tree> <output.js>')
        return
    infile = sys.argv[1]
    outfile = sys.argv[2]
    with open(infile, 'r') as f:
        lines = [line.rstrip('\n') for line in f if line.strip() and not line.strip().startswith('//')]
    nodes = parse_nodes(lines)
    tree = build_js_tree(nodes)
    with open(outfile, 'w') as f:
        f.write('export default ')
        json.dump(tree, f, indent=2)
        f.write(';\n')

if __name__ == '__main__':
    main()
