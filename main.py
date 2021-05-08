#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2020 Scriptim (https://github.com/Scriptim)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""This module runs a `abalone.game.Game`."""

import os
import pickle
import sys
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from traceback import format_exc
from typing import Generator, List, Tuple, Union

import matplotlib.pyplot as plt

from abalone.abstract_player import AbstractPlayer
from abalone.enums import Direction, Player, Space
from abalone.game import Game, IllegalMoveException
from abalone.utils import line_from_to

DATA_DIR = './data'


def _get_winner(score: Tuple[int, int]) -> Union[Player, None]:
    """Returns the winner of the game based on the current score.

    Args:
        score: The score tuple returned by `abalone.game.Game.get_score`

    Returns:
        Either the `abalone.enums.Player` who won the game or `None` if no one has won yet.
    """
    if 8 in score:
        return Player.WHITE if score[0] == 8 else Player.BLACK
    return None


def _format_move(turn: Player, move: Tuple[Union[Space, Tuple[Space, Space]], Direction], moves: int) -> str:
    """Formats a player's move as a string with a single line.

    Args:
        turn: The `Player` who performs the move
        move: The move as returned by `abalone.abstract_player.AbstractPlayer.turn`
        moves: The number of total moves made so far (not including this move)
    """
    marbles = [move[0]] if isinstance(
        move[0], Space) else line_from_to(*move[0])[0]
    marbles = map(lambda space: space.name, marbles)
    return f'{moves + 1}: {turn.name} moves {", ".join(marbles)} in direction {move[1].name}'


def _merge_dict(dict1, dict2):
    for key in dict2.keys():
        dict1[key] += dict2[key]


def _write_to_file(obj, filename):
    with open(os.path.join(DATA_DIR, filename), 'wb') as file:
        pickle.dump(obj, file)


def _open_from_file(filename) -> dict:
    with open(os.path.join(DATA_DIR, filename), 'rb') as file:
        return pickle.load(file)


@dataclass
class MoveStats:
    no: int
    space: str
    direction: Direction
    time: float


@dataclass
class GameStats:
    name_black: str
    name_white: str
    score_black: int
    score_white: int
    total_time: float
    moves: List[MoveStats]

    _dir = 'games'

    def save(self):
        _write_to_file(asdict(self), os.path.join(
            self._dir, f'{time.time()}.pickle'))


def run_game(black: AbstractPlayer, white: AbstractPlayer, is_verbose: bool = True) \
        -> Generator[Tuple[Game, List[Tuple[Union[Space, Tuple[Space, Space]], Direction]]], None, None]:
    """Runs a game instance and prints the progress / current state at every turn.

    Args:
        black: An `abalone.abstract_player.AbstractPlayer`
        white: An `abalone.abstract_player.AbstractPlayer`
        **kwargs: These arguments are passed to `abalone.game.Game.__init__`

    """
    game = Game()
    moves_history = []
    count = defaultdict(int)
    move_stats = []

    while True:
        score = game.get_score()
        if is_verbose:
            score_str = f'BLACK {score[0]} - WHITE {score[1]}'
            print(score_str, game, '', sep='\n')

        winner = _get_winner(score)
        if winner is not None and is_verbose:
            print(f'{winner.name} won!')
            break

        try:
            start = time.time()
            move = black.turn(game, moves_history) if game.turn is Player.BLACK else white.turn(
                game, moves_history)
            end = time.time()
            if is_verbose:
                print(f'Time to deliberate: {end-start}')
                print(_format_move(game.turn, move,
                                   len(moves_history)), end='\n\n')
            game.move(*move)
            game.switch_player()
            move_stats.append(MoveStats(
                no=len(moves_history),
                space=move[0],
                direction=move[1],
                time=end-start,
            ))
            moves_history.append(move)

        except IllegalMoveException as ex:
            if is_verbose:
                print(
                    f'{game.turn.name}\'s tried to perform an illegal move ({ex})\n')
            break
        except:
            if is_verbose:
                print(f'{game.turn.name}\'s move caused an exception\n')
                print(format_exc())
            break
    return game, moves_history, move_stats


if __name__ == '__main__':  # pragma: no cover
    # Run a game from the command line with default configuration.
    import argparse
    import importlib
    import sys

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('player_black', metavar='blk', type=str,
                        help='Python path to the Player module for black')
    parser.add_argument('player_white', metavar='wht', type=str,
                        help='Python path to the Player module for black')
    parser.add_argument('-g', '--games', type=int,
                        default=1,
                        help='Number of games to play')
    parser.add_argument('-v', '--verbose', type=bool,
                        default=False, const=True, nargs='?',
                        help='Print the game output')

    args = parser.parse_args()

    black_str = args.player_black.rsplit('.', 1)
    black = getattr(importlib.import_module(black_str[0]), black_str[1])()
    white_str = args.player_white.rsplit('.', 1)
    white = getattr(importlib.import_module(white_str[0]), white_str[1])()

    total = defaultdict(int)
    for i in range(0, args.games):
        print(f'Starting game {i}')
        start = time.time()
        game, moves_history, move_stats = run_game(black, white, args.verbose)
        end = time.time()
        score = game.get_score()
        total_time = end-start
        GameStats(
            name_black=str(black),
            name_white=str(white),
            score_black=score[0],
            score_white=score[1],
            total_time=total_time,
            moves=move_stats,
        ).save()
        print(f'Time to simulate: {total_time}')
        print(f'Total moves: {len(moves_history)}')

    # write_to_file(total, f'{time.time()}_data.json')
    # plt.bar(total.keys(), total.values())
    # plt.show()
