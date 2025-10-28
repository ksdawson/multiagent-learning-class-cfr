from utils import get_player_from_info_set, graph_output
from problem_5p2 import regret_matching, normalize

def expectimax(tree, info_sets, player, info_set_memo, opponent_strategy=None):
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
            return expectimax(tree.children[best_action], info_sets, player, info_set_memo, opponent_strategy)
        info_set = info_sets.get_info_set(info_set_name)

        # Get best action utility over all nodes in the info set
        actions = tree.children.keys()
        best_action = None
        best_expected_payoff = float('-inf')
        for action in actions:
            action_expected_payoff = 0
            for decision_node in info_set:
                child_node = decision_node.children[action]
                expected_payoff = expectimax(child_node, info_sets, player, info_set_memo, opponent_strategy)
                action_expected_payoff += expected_payoff / len(info_set)
            if action_expected_payoff > best_expected_payoff:
                best_action = action
                best_expected_payoff = action_expected_payoff

        # Update memo
        info_set_memo[info_set_name] = best_action
        
        # Get expected payoff for this action
        return expectimax(tree.children[best_action], info_sets, player, info_set_memo, opponent_strategy)
    elif (tree.type == 'DecisionNode' and tree.node.player != player) or tree.type == 'ChanceNode':
        # Treat opponent like a chance node -> return expected payoff
        total_expected_payoff = 0
        # Probability for uniform opponent strategy
        num_actions = len(tree.children)
        uniform_strategy = 1/num_actions
        for edge, child_node in tree.children.items():
            expected_payoff = expectimax(child_node, info_sets, player, info_set_memo, opponent_strategy)
            # Calculate probability to weight this payoff
            if tree.type == 'ChanceNode':
                prob = tree.node.probs[edge]
            else:
                if opponent_strategy and tree.info_set in opponent_strategy:
                    prob = opponent_strategy[tree.info_set][edge]
                else:
                    # Default to uniform
                    prob = uniform_strategy
            total_expected_payoff += expected_payoff * prob
        return total_expected_payoff
    else:
        # Shouldn't happen
        raise Exception

def compute_nash_gap(tree, info_sets, avg_strategy):
    br_p1 = expectimax(tree, info_sets, player='1', info_set_memo={}, opponent_strategy=avg_strategy)
    br_p2 = expectimax(tree, info_sets, player='2', info_set_memo={}, opponent_strategy=avg_strategy)
    nash_gap = br_p1 + br_p2
    return nash_gap

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
    nash_gaps = []
    for _ in range(iters):
        # Run cfr and compute utilities
        util = cfr_utility_dual(tree, info_sets, regrets, strategy_sum)
        utilities.append((util['1'], util['2']))

        # Compute average strategies for both players
        avg_strategy = {info_set_name: normalize(strategy_sum[info_set_name])
                        for info_set_name in strategy_sum}
        
        # Compute nash gap
        nash_gap = compute_nash_gap(tree, info_sets, avg_strategy)
        nash_gaps.append(nash_gap)

    return avg_strategy, regrets, utilities, nash_gaps

def learning_the_nash_equilibrium(tree, info_sets, game_name):
    # Run CFR with the players playing against each other
    avg_strategy, regrets, utilities, nash_gaps = cfr_dual(tree, info_sets)
    ne_utility = utilities[-1]
    print('Player 1, 2 NE utilities: ', ne_utility)

    # Get player 1's expected utility
    p1_utilities = []
    for p1, p2 in utilities:
        p1_utilities.append(p1)

    # Graph
    graph_output(nash_gaps, 'Nash Gap', game_name)
    graph_output(p1_utilities, 'NE Expected Utility', game_name)