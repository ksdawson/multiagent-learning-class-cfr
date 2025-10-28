from utils import get_player_from_info_set, graph_output
from problem_5p2 import regret_matching, normalize

def cfr_utility_dual(tree, info_sets, regrets, strategy_sum, rprob1=1.0, rprob2=1.0):
    if tree.type == 'TerminalNode':
        return tree.node.payoffs  # return payoff dict for all players
    elif tree.type == 'DecisionNode':
        player = tree.node.player
        info_set = tree.info_set

        # Compute strategy for this player
        strategy = regret_matching(regrets[info_set])
        for a in tree.children:
            strategy_sum[info_set][a] += (rprob1 if player == '1' else rprob2) * strategy[a]

        # Compute expected utility for each action
        action_utils = {}
        node_value = {'1': 0.0, '2': 0.0}
        for a, child_node in tree.children.items():
            next_rprob1 = rprob1 * strategy[a] if player == '1' else rprob1
            next_rprob2 = rprob2 * strategy[a] if player == '2' else rprob2
            child_util = cfr_utility_dual(child_node, info_sets, regrets, strategy_sum,
                                          next_rprob1, next_rprob2)
            action_utils[a] = child_util
            node_value['1'] += strategy[a] * child_util['1']
            node_value['2'] += strategy[a] * child_util['2']

        # Update regrets for this player
        for a in tree.children:
            regret = action_utils[a][player] - node_value[player]
            if player == '1':
                regrets[info_set][a] += rprob2 * regret
            else:
                regrets[info_set][a] += rprob1 * regret

        return node_value
    elif tree.type == 'ChanceNode':
        total_expected = {'1': 0.0, '2': 0.0}
        for a, child_node in tree.children.items():
            prob = tree.node.probs[a]
            child_util = cfr_utility_dual(child_node, info_sets, regrets, strategy_sum,
                                          rprob1 * prob, rprob2 * prob)
            total_expected['1'] += prob * child_util['1']
            total_expected['2'] += prob * child_util['2']
        return total_expected
    else:
        raise Exception("Unknown node type")

def cfr_dual(tree, info_sets, iters=1000):
    # Initialize regrets and strategy sums for both players
    regrets = {}
    strategy_sum = {}
    for info_set_name in info_sets.get_info_sets():
        nodes = info_sets.get_info_set(info_set_name)
        actions = set()
        for node in nodes:
            if node.type == 'DecisionNode':
                actions.update(node.node.actions)
        regrets[info_set_name] = {a: 0 for a in actions}
        strategy_sum[info_set_name] = {a: 0 for a in actions}

    utilities = []
    for _ in range(iters):
        util = cfr_utility_dual(tree, info_sets, regrets, strategy_sum)
        utilities.append((util['1'], util['2']))

    # Compute average strategies for both players
    avg_strategy = {info_set_name: normalize(strategy_sum[info_set_name])
                    for info_set_name in strategy_sum}

    return avg_strategy, regrets, utilities

def learning_the_nash_equilibrium(tree, info_sets, game_name):
    # Run CFR with the players playing against each other
    avg_strategy, regrets, utilities = cfr_dual(tree, info_sets)
    ne_utility = utilities[-1]
    print('Player 1, 2 NE utilities: ', ne_utility)

    # Compute the Nash gap over the iterations
    nash_gaps = []
    p1_utilities = []
    for p1, p2 in utilities:
        p1_utilities.append(p1)
        gap = p1 + p2
        nash_gaps.append(gap)
    graph_output(nash_gaps, 'Nash Gap', game_name)
    graph_output(p1_utilities, 'NE Expected Utility', game_name)