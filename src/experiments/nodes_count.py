import time
from dataclasses import dataclass
from enum import Enum
from typing import List

from abalone.enums import InitialPosition
from abalone.game import Game, Marble

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


class Position(Enum):
    MID_GAME = [
        [Marble.WHITE] * 5,
        [Marble.WHITE] * 5 + [Marble.BLANK],
        [Marble.BLANK] * 3 + [Marble.WHITE] +
        [Marble.BLANK] + [Marble.WHITE] * 2,
        [Marble.BLANK] * 4 + [Marble.BLACK] +
        [Marble.WHITE] + [Marble.BLANK] * 2,
        [Marble.BLANK] * 4 + [Marble.BLACK] * 2 + [Marble.BLANK] * 3,
        [Marble.BLANK] * 3 + [Marble.BLACK] * 4 + [Marble.BLANK],
        [Marble.BLANK] * 1 + [Marble.BLACK] * 4 + [Marble.BLANK] * 2,
        [Marble.BLANK] * 1 + [Marble.BLACK] +
        [Marble.BLANK] + [Marble.BLACK] * 2 + [Marble.BLANK],
        [Marble.BLANK] * 5
    ]


POSITIONS = [
    InitialPosition.DEFAULT,
    # Position.MID_GAME,
]


def main():
    global nodes
    results = []
    for position in POSITIONS:
        game = Game(initial_position=position)
        algorithms = [
            # {
            #     'class': players.AlphaBetaSimple,
            #     'args': (game, game.turn),
            #     'kwargs': {
            #         'depth': 1,
            #         'func': count_nodes,
            #     },
            # },
            # {
            #     'class': players.AlphaBetaSimple,
            #     'args': (game, game.turn),
            #     'kwargs': {
            #         'depth': 2,
            #         'func': count_nodes,
            #     },
            # },
            # {
            #     'class': players.AlphaBetaSimple,
            #     'args': (game, game.turn),
            #     'kwargs': {
            #         'depth': 3,
            #         'func': count_nodes,
            #     },
            # },
            # {
            #     'class': players.AlphaBetaSimple,
            #     'args': (game, game.turn),
            #     'kwargs': {
            #         'depth': 4,
            #         'func': count_nodes,
            #     },
            # },
            {
                'class': players.AlphaBetaAdvanced,
                'args': (game, game.turn),
                'kwargs': {
                    'depth': 4,
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
