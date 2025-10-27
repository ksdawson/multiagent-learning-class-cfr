from utils import load_game_from_txt

def expectimax(tree, player):
    # Base case
    if tree.type == 'TerminalNode':
        # Return payoff of player
        for player_name, payoff in tree.payoffs:
            if player == player_name:
                return [], payoff

    # Recursive step
    if tree.type == 'DecisionNode':
        if tree.node.player == player:
            # Player
            best_response = None
            recursive_best_response = None
            best_expected_payoff = float('-inf')
            for edge, child_node in tree.children:
                strategy, expected_payoff = expectimax(child_node, player)
                if expected_payoff > best_expected_payoff:
                    best_response = edge
                    recursive_best_response = strategy
                    best_expected_payoff = expected_payoff
        else:
            # Opponent
    elif tree.type == 'ChanceNode':
        # TODO

def find_the_best_response():
    pass

def learning_to_best_respond():
    pass

def learning_the_nash_equilibrium():
    pass

def main():
    games = [
        './rock_paper_superscissors.txt',
        # './kuhn.txt',
        # './leduc2.txt'
    ]

    for game in games:
        # Construct the game tree
        tree, info_sets = load_game_from_txt(game)

        # TODO: Plot results

if __name__ == "__main__":
    main()