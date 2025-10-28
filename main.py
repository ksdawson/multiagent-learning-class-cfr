from utils import load_game_from_txt

def expectimax(tree, info_sets, player, info_set_memo):
    # Base case
    if tree.type == 'TerminalNode':
        # Return payoff of player
        return tree.node.payoffs[player]
    # Recursive steps
    elif tree.type == 'DecisionNode' and tree.node.player == player:
        # Player -> determine best action for info set
        info_set_name = tree.info_set
        if info_set_name in info_set_memo:
            # Already considered all decision nodes in this info set
            best_action = info_set_memo[info_set_name]
            return expectimax(tree.children[best_action], info_sets, player, info_set_memo)
        info_set = info_sets.get_info_set(info_set_name)

        # Get best action utility over all nodes in the info set
        actions = tree.children.keys()
        best_action = None
        best_expected_payoff = float('-inf')
        for action in actions:
            action_expected_payoff = 0
            for decision_node in info_set:
                child_node = decision_node.children[action]
                expected_payoff = expectimax(child_node, info_sets, player, info_set_memo)
                action_expected_payoff += expected_payoff / len(info_set)
            if action_expected_payoff > best_expected_payoff:
                best_action = action
                best_expected_payoff = action_expected_payoff

        # Update memo
        info_set_memo[info_set_name] = best_action
        
        # Get expected payoff for this action
        return expectimax(tree.children[best_action], info_sets, player, info_set_memo)
    elif (tree.type == 'DecisionNode' and tree.node.player != player) or tree.type == 'ChanceNode':
        # Treat opponent like a chance node -> return expected payoff
        total_expected_payoff = 0
        # Probability for uniform opponent strategy
        num_actions = len(tree.children)
        uniform_strategy = 1/num_actions
        for edge, child_node in tree.children.items():
            expected_payoff = expectimax(child_node, info_sets, player, info_set_memo)
            # Calculate probability to weight this payoff
            if tree.type == 'ChanceNode':
                prob = tree.node.probs[edge]
            else:
                prob = uniform_strategy
            total_expected_payoff += expected_payoff * prob
        return total_expected_payoff
    else:
        # Shouldn't happen
        raise Exception

def find_the_best_response(tree, info_sets):
    # Find the best response for Player 1 against a uniform strategy for Player 2,
    # who plays uniformly over all valid actions at each decision node
    p1 = '1'
    p1_best_response = {}
    p1_expected_utility = expectimax(tree, info_sets, p1, p1_best_response)
    print('Player 1 expected utility: ', p1_expected_utility)
    
    # Calculate p2 best response
    p2 = '2'
    p2_best_response = {}
    p2_expected_utility = expectimax(tree, info_sets, p2, p2_best_response)
    print('Player 2 expected utility: ', p2_expected_utility)

    # Calculate nash gap
    nash_gap = p1_expected_utility + p2_expected_utility
    print('Nash gap: ', nash_gap)

def learning_to_best_respond():
    pass

def learning_the_nash_equilibrium():
    pass

def main():
    games = [
        ('Rock Paper Superscissors', './rock_paper_superscissors.txt'),
        ('Kuhn Poker', './kuhn.txt'),
        ('Leduc Poker', './leduc2.txt')
    ]

    for game_name, filename in games:
        # Construct the game tree
        print(game_name)
        tree, info_sets = load_game_from_txt(filename)

        # 5.1
        print('Problem 5.1')
        find_the_best_response(tree, info_sets)

        # TODO: Plot results
        print()

if __name__ == "__main__":
    main()