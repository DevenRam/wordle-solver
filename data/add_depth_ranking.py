import json5

def compute_depth_and_ranking(node):
    if node is None or isinstance(node, str):
        # Leaf node: solved in 1 guess or dead end
        return 1, {'counts': [1]}
    else:
        min_depth = float('inf')
        ranking_counts = []
        for score, child in node['map'].items():
            child_depth, child_ranking = compute_depth_and_ranking(child)
            min_depth = min(min_depth, child_depth)
            # Extend ranking_counts array as needed
            while len(ranking_counts) < len(child_ranking['counts']) + 1:
                ranking_counts.append(0)
            for i, count in enumerate(child_ranking['counts']):
                ranking_counts[i + 1] += count
        node['depth'] = min_depth + 1
        node['ranking'] = {'counts': ranking_counts}
        return node['depth'], node['ranking']

# Remove "export default " from the start of the file before loading
with open('tarse.tree.total.js', 'r', encoding='utf-8') as f:
    content = f.read()
    if content.startswith('export default '):
        content = content[len('export default '):]
    # Remove trailing semicolon and whitespace
    content = content.rstrip().rstrip(';').rstrip()
    tree = json5.loads(content)

compute_depth_and_ranking(tree)

# Write back with "export default " prefix
with open('tarse.tree.total.js', 'w', encoding='utf-8') as f:
    f.write('export default ')
    json5.dump(tree, f, separators=(',', ':'))

print("Depth and ranking added to tarse.tree.total.js")