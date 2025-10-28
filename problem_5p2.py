from utils import get_player_from_info_set, graph_output

def normalize(strategy_counts):
    total = sum(strategy_counts.values())
    if total == 0:
        # If all counts are zero, just return uniform
        n = len(strategy_counts)
        return {a: 1.0 / n for a in strategy_counts}
    return {a: count / total for a, count in strategy_counts.items()}

def regret_matching(regret_map):
    positive_regrets = {a: max(r, 0) for a, r in regret_map.items()}
    normalizer = sum(positive_regrets.values())
    if normalizer > 0:
        return {a: r / normalizer for a, r in positive_regrets.items()}
    # If all regrets <= 0, play uniform
    n = len(regret_map)
    return {a: 1.0 / n for a in regret_map}

def cfr_utility(tree, info_sets, player, rprob1, rprob2, regrets, strategy_sum):
    # Base case
    if tree.type == 'TerminalNode':
        # Return payoff of player
        return tree.node.payoffs[player]
    # Recursive steps
    elif tree.type == 'DecisionNode' and tree.node.player == player:
        # Player -> ?
        info_set = tree.info_set

        # Compute current strategy from regrets
        strategy = regret_matching(regrets[info_set])
        for a, _ in tree.children.items():
            strategy_sum[info_set][a] += rprob1 * strategy[a] # accumulate reach-weighted strategy

        # Compute utilities for each action
        action_utils = {}
        node_value = 0
        for a, child_node in tree.children.items():
            action_utils[a] = cfr_utility(child_node, info_sets, player, rprob1 * strategy[a], rprob2, regrets, strategy_sum)
            node_value += strategy[a] * action_utils[a]

        # Update regrets
        for a, _ in tree.children.items():
            regret = action_utils[a] - node_value
            regrets[info_set][a] += rprob2 * regret # weighted by opponent reach prob

        return node_value
    elif (tree.type == 'DecisionNode' and tree.node.player != player) or tree.type == 'ChanceNode':
        # Treat opponent like a chance node -> return expected payoff
        total_expected_payoff = 0
        # Probability for uniform opponent strategy
        num_actions = len(tree.children)
        uniform_strategy = 1/num_actions
        for edge, child_node in tree.children.items():
            # Calculate probability to weight this payoff
            if tree.type == 'ChanceNode':
                prob = tree.node.probs[edge]
                adj = 1.0
            else:
                prob = uniform_strategy
                adj = prob
            expected_payoff = cfr_utility(child_node, info_sets, player, rprob1, adj * rprob2, regrets, strategy_sum)
            total_expected_payoff += expected_payoff * prob
        return total_expected_payoff
    else:
        # Shouldn't happen
        raise Exception

def cfr(tree, info_sets, player, iters=1000):
    # Setup the regret and strategy sum
    regrets = {}
    strategy_sum = {}
    for info_set_name in info_sets.get_info_sets():
        player_name = get_player_from_info_set(info_set_name, info_sets)
        if player_name == player:
            nodes = info_sets.get_info_set(info_set_name)
            actions = set()
            for node in nodes:
                if node.type == 'DecisionNode':
                    actions.update(node.node.actions)
            regrets[info_set_name] = {a: 0 for a in actions}
            strategy_sum[info_set_name] = {a: 0 for a in actions}

    # Repeatedly run CFR up to the # iters
    utilities = []
    for i in range(iters):
        player_expected_utility = cfr_utility(tree, info_sets, player, 1.0, 1.0, regrets, strategy_sum)
        utilities.append(player_expected_utility)
    
    # Compute the average strategy
    avg_strategy = {}
    for info_set_name in strategy_sum:
        avg_strategy[info_set_name] = normalize(strategy_sum[info_set_name])

    return avg_strategy, regrets, utilities

def learning_to_best_respond(tree, info_sets):
    p1 = '1'
    avg_strategy, regrets, utilities = cfr(tree, info_sets, p1)
    # print(avg_strategy, '\n')
    # print(regrets)
    graph_output(utilities)