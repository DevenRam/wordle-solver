# Let's reload the new example .tree file and parse it with the patched logic

def parse_tree_file_fixed(filepath):
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
            node_data['ranking'] = {'counts': [int(n) for n in counts_str.split(',')] }
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
            else:
                if not root:
                    root = {'map': {}}
                root['map'][key] = value
        elif node_data == 'MAP_MARKER':
            if stack:
                current_node = stack[-1][0]
                if 'map' not in current_node:
                    current_node['map'] = {}
            elif not root:
                root = {'map': {}}
        else:
            if stack:
                current_node = stack[-1][0]
                if 'map' not in current_node:
                    current_node['map'] = {}
            else:
                if not root:
                    root = node_data
                else:
                    if 'map' not in root:
                        root['map'] = {}
            stack.append((node_data, indent))

    return root

# Parse the newly uploaded tree file
tree_data_fixed = parse_tree_file_fixed('tarse.tree')
tree_data_fixed  # Show parsed result
