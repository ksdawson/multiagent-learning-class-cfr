import re

class DecisionNode:
    def __init__(self, player, actions):
        self.actions = actions # list of strs
        self.player = player # str

class ChanceNode:
    def __init__(self, probs):
        self.actions = list(probs.keys()) # list of strs
        self.probs = probs # dict mapping strs to floats

class TerminalNode:
    def __init__(self, payoffs):
        self.actions = [] # no edges for a terminal node
        self.payoffs = payoffs # dict of player:payoff

class TreeNode:
    def __init__(self, node):
        # node types: decision, chance, terminal
        self.type = node.__class__.__name__
        self.node = node
        # edges are based on action history
        self.parent = None # node
        self.children = {} # dict mapping actions to nodes
        # info set
        self.info_set = None

    def set_info_set(self, info_set_name):
        self.info_set = info_set_name

    def set_parent(self, parent):
        self.parent = parent

    def set_child(self, edge, node):
        self.children[edge] = node

    def add_node(self, tree_node, path):
        # Find the last node on the path
        next_node = self
        for i in range(len(path)-1):
            act = path[i]
            next_node = next_node.children[act]
        # Add last node on path as parent
        tree_node.set_parent(next_node)
        # Add new node to children for the parent node
        next_node.set_child(path[-1], tree_node)

    def get_node(self, path):
        next_node = self
        for act in path:
            next_node = next_node.children[act]
        return next_node

class InformationSets:
    def __init__(self):
        self.info_sets = {} # dict mapping names to lists of nodes

    def add_info_set(self, name, nodes):
        self.info_sets[name] = nodes

    def get_info_set(self, name):
        return self.info_sets[name]

def convert_history_to_path(history):
    path = history.split('/')[1:-1]
    path = [act.split(':')[1] for act in path]
    return path

def parse_node(line):
    # Parse the nodes to get the node and history
    if 'player' in line:
        # Parse decision nodes
        match = re.match(r'node\s+(\/.*?)\s+player\s+(\d+)\s+actions\s+(.+)', line)
        if not match:
            raise Exception
        history, player, actions_str = match.groups()
        actions = actions_str.split()
        node = DecisionNode(player, actions)
    elif 'chance' in line:
        # Parse chance nodes
        match = re.match(r'node\s+(\/.*?)\s+chance\s+actions\s+(.+)', line)
        if not match:
            raise Exception
        history, actions_str = match.groups()
        probs = {}
        for a in actions_str.split():
            if '=' in a:
                act, prob = a.split('=')
                probs[act.strip()] = float(prob)
        node = ChanceNode(probs)
    elif 'terminal' in line:
        # Parse terminal nodes
        match = re.match(r'node\s+(\/.*?)\s+terminal\s+payoffs\s+(.+)', line)
        if not match:
            raise Exception
        history, payoff_str = match.groups()
        payoffs = {p.split('=')[0]: float(p.split('=')[1]) for p in payoff_str.split()}
        node = TerminalNode(payoffs)
    else:
        # Shouldn't happen
        raise Exception
    
    # Parse the history to create the edges to traverse to get to where to insert the node in the tree
    path = convert_history_to_path(history)
    
    return node, path

def parse_infoset(line):
    match = re.match(r'infoset\s+(\/.*?)\s+nodes\s+(.+)', line)
    if not match:
        raise Exception
    name, nodes_str = match.groups()
    node_histories = [s.strip() for s in nodes_str.split() if s.startswith('/')]
    # Convert the histories to paths
    paths = [convert_history_to_path(history) for history in node_histories]
    return name, paths

def load_game_from_txt(filepath):
    with open(filepath, 'r') as f:
        # Convert the file into lines
        content = f.read()
        lines = content.splitlines()

        # Create the info sets
        info_sets = InformationSets()

        # Create the root node
        node, path = parse_node(lines[0])
        root = TreeNode(node)

        # Iterate over the rest of the lines
        for i in range(1, len(lines)):
            line = lines[i].strip() # remove spaces
            if line.startswith('node'):
                # Parse the node
                node, path = parse_node(line)
                # Create a tree node
                tree_node = TreeNode(node)
                # Add the new node to the tree
                root.add_node(tree_node, path)
            elif line.startswith('infoset'):
                # Parse infoset
                name, paths = parse_infoset(line)
                # Add the infoset
                tree_nodes = []
                for path in paths:
                    tree_node = root.get_node(path)
                    # Add the info set to the node
                    tree_node.set_info_set(name)
                    # Keep track of all the nodes
                    tree_nodes.append(tree_node)
                info_sets.add_info_set(name, tree_nodes)
            else:
                # Shouldn't happen
                raise Exception
            
        return root, info_sets

if __name__ == '__main__':
    load_game_from_txt('./rock_paper_superscissors.txt')