import time
from dataclasses import dataclass
from typing import List

from abalone.game import Game

from .. import players, utils


@dataclass
class NodeCount:
    _dir = 'counts'

    algorithm: str
    time: float
    nodes_visited: int

    def __str__(self):
        return f'Time: {self.time} | Nodes visited: {self.nodes_visited}'


@dataclass
class Counts(utils.Stats):
    _dir = 'node_counts'

    node_counts: List[NodeCount]


nodes = 0


def count_nodes():
    global nodes
    nodes += 1


def reset_count():
    global nodes
    nodes = 0


def main():
    global nodes
    game = Game()
    algorithms = [
        {
            'class': players.AlphaBetaSimple,
            'args': (game, game.turn),
            'kwargs': {
                'depth': 1,
                'func': count_nodes,
            },
        },
        # {
        #     'class': players.AlphaBetaSimple,
        #     'args': (game, game.turn),
        #     'kwargs': {
        #         'depth': 4,
        #         'func': count_nodes,
        #     },
        # },
        # {
        #     'class': players.AlphaBetaSimpleUnordered,
        #     'args': (game, game.turn),
        #     'kwargs': {
        #         'depth': 3,
        #         'func': count_nodes,
        #     },
        # },
        # {
        #     'class': players.AlphaBetaSimpleUnordered,
        #     'args': (game, game.turn),
        #     'kwargs': {
        #         'depth': 4,
        #         'func': count_nodes,
        #     },
        # },
    ]
    results = []
    for algo in algorithms:
        algo = algo['class'](*algo['args'], **algo['kwargs'])
        name = str(algo)
        print(f'[ ] Running {name}...')
        start = time.time()
        move = algo.run()
        end = time.time()
        total_time = end-start
        result = NodeCount(
            algorithm=name,
            time=total_time,
            nodes_visited=nodes,
        )
        results.append(result)
        reset_count()
        print(f'[x] Result: {result}')

    print('[ ] Saving...')
    Counts(node_counts=results).save()
    print('[x] Saved')


if __name__ == '__main__':
    main()
