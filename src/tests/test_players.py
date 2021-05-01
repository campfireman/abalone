from typing import List

from abalone.enums import InitialPosition, Player
from abalone.game import Game

from .. import players

BOARD_DIMENSIONS = [
    5, 6, 7, 8, 9, 8, 7, 6, 5
]


def _validate_board(self, board: List[List]):
    assert len(board) == len(BOARD_DIMENSIONS)
    for i, row in enumerate(board):
        assert len(row) == BOARD_DIMENSIONS[i]


def test_heuristic():
    boards = [{
        'value': InitialPosition.DEFAULT.value,
        'expected_heuristic': 0.0,
        'in_turn': Player.BLACK,
    }]
    game = Game()
    for board in boards:
        game.board = board['value']
        game.turn = board['in_turn']
        algorithm = players.AlphaBetaSimple(game)
        assert algorithm._heuristic(game) == board['expected_heuristic']
