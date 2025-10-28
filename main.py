from utils import load_game_from_txt
from problem_5p1 import find_the_best_response
from problem_5p2 import learning_to_best_respond
from problem_5p3 import learning_the_nash_equilibrium

def main():
    games = [
        # ('Rock Paper Superscissors', './rock_paper_superscissors.txt'),
        ('Kuhn Poker', './kuhn.txt'),
        # ('Leduc Poker', './leduc2.txt')
    ]

    for game_name, filename in games:
        # Construct the game tree
        print(game_name)
        tree, info_sets = load_game_from_txt(filename)

        # 5.1
        print('Problem 5.1')
        find_the_best_response(tree, info_sets)

        # 5.2
        print('Problem 5.2')
        learning_to_best_respond(tree, info_sets)

        # 5.3
        print('Problem 5.2')
        learning_the_nash_equilibrium()

        # TODO: Plot results
        print()

if __name__ == "__main__":
    main()