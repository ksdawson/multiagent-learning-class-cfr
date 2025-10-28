from utils import get_player_from_info_set

def cfr_utility(tree, rprob1, rprob2, regrets, strategy_sum):
    pass

def cfr(tree, info_sets, player, iters=1000):
    # Setup the regret and strategy sum
    regrets = {}
    strategy_sum = {}
    for info_set_name in info_sets.get_info_sets():
        player_name = get_player_from_info_set(info_set_name, info_sets)
        if player_name == player:
            nodes = info_sets.get_info_set(info_set_name)
            actions = {}
            for node in nodes:
                if node.type == 'DecisionNode':
                    actions.update(node.node.actions)
            regrets[info_set_name] = {a: 0 for a in actions}
            strategy_sum[info_set_name] = {a: 0 for a in actions}

    # Repeatedly run CFR up to the # iters
    for i in range(iters):
        cfr_utility(tree, 1.0, 1.0, regrets, strategy_sum)
    
    # Compute the average strategy
    avg_strategy = {}
    for info_set_name in strategy_sum:
        # avg_strategy[info_set_name] = normalize(strategy_sum[info_set_name])
        avg_strategy[info_set_name] = strategy_sum[info_set_name]

    return avg_strategy, regrets

def learning_to_best_respond(tree, info_sets):
    p1 = 'p1'
    cfr(tree, info_sets, p1)