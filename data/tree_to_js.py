
import json
import sys

def parse_tree_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = [line.rstrip('\n') for line in file]

    root = None
    stack = []

    for line in lines:
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(' '))
        content = line.strip()

        node_data = {}
        if content.startswith('guess:'):
            node_data['guess'] = content.split(':', 1)[1].strip()
        elif content.startswith('map:'):
            node_data = 'MAP_MARKER'
        elif content.startswith('depth:'):
            node_data['depth'] = int(content.split(':', 1)[1].strip())
        elif content.startswith('ranking:'):
            counts_str = content.split('[', 1)[1].split(']')[0]
            node_data['ranking'] = {'counts': [int(n) for n in counts_str.split(',')]}
        else:
            if ':' in content:
                key, value = content.split(':', 1)
                key = key.strip().strip('"')
                value = value.strip().strip('"')
                node_data = (key, value)
            else:
                continue

        while stack and stack[-1][1] >= indent:
            stack.pop()

        if isinstance(node_data, tuple):
            key, value = node_data
            if stack:
                current_node = stack[-1][0]
                if 'map' not in current_node:
                    current_node['map'] = {}
                current_node['map'][key] = value
        elif node_data == 'MAP_MARKER':
            if stack:
                current_node = stack[-1][0]
                if 'map' not in current_node:
                    current_node['map'] = {}
        else:
            if stack:
                current_node = stack[-1][0]
                if 'map' not in current_node:
                    current_node['map'] = {}
            else:
                root = node_data

            stack.append((node_data, indent))

    return root

def convert_tree_to_js(tree_data, output_file):
    js_output = 'export default ' + json.dumps(tree_data, indent=4) + ';'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(js_output)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python tree_to_js.py input.tree output.js")
        sys.exit(1)

    tree_file = sys.argv[1]
    js_file = sys.argv[2]

    tree_data = parse_tree_file(tree_file)
    convert_tree_to_js(tree_data, js_file)
