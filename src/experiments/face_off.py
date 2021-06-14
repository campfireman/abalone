import time
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import List

from abalone.enums import InitialPosition
from abalone.game import Game, Marble
from abalone.random_player import RandomPlayer

from .. import players, utils

MATCHES = [
    # {
    #     'players': (players.AlphaBetaPlayerFast, RandomPlayer),
    #     'iterations': 5,
    #     'args': ((), ()),
    #     'kwargs': ({'depth': 2, 'verbose': False}, {}),
    # },
    # {
    #     'players': (players.AlphaBetaPlayerFast, RandomPlayer),
    #     'iterations': 5,
    #     'args': ((), ()),
    #     'kwargs': ({'depth': 3, 'verbose': False}, {}),
    # },
    # {
    #     'players': (players.AlphaBetaPlayerFast, RandomPlayer),
    #     'iterations': 5,
    #     'args': ((), ()),
    #     'kwargs': ({'depth': 4, 'verbose': False}, {}),
    # },
    # {
    #     'players': (players.AlphaBetaPlayer, RandomPlayer),
    #     'iterations': 5,
    #     'args': ((), ()),
    #     'kwargs': ({'depth': 2, 'verbose': False}, {}),
    # },
    # {
    #     'players': (players.AlphaBetaPlayer, RandomPlayer),
    #     'iterations': 5,
    #     'args': ((), ()),
    #     'kwargs': ({'depth': 3, 'verbose': False}, {}),
    # },
    # {
    #     'players': (players.AlphaBetaPlayer, RandomPlayer),
    #     'iterations': 5,
    #     'args': ((), ()),
    #     'kwargs': ({'depth': 4, 'verbose': False}, {}),
    # },
    # {
    #     'players': (players.AlphaBetaPlayer, players.AlphaBetaPlayer),
    #     'iterations': 5,
    #     'args': ((), ()),
    #     'kwargs': ({'depth': 3, 'verbose': False}, {'depth': 3, 'verbose': False}),
    # },
    # {
    #     'players': (players.AlphaBetaPlayer, players.AlphaBetaPlayerFast),
    #     'iterations': 1,
    #     'args': ((), ()),
    #     'kwargs': ({'depth': 3, 'verbose': False}, {'depth': 3}),
    # },
    {
        'players': (players.MonteCarloPlayerImproved, players.AlphaBetaPlayerFast),
        'iterations': 1,
        'args': ((), ()),
        'kwargs': ({'max_time': 20}, {'depth': 3, 'verbose': False}),
    },
    # {
    #     'players': (players.MonteCarloPlayerImproved, RandomPlayer),
    #     'iterations': 1,
    #     'args': ((), ()),
    #     'kwargs': ({'max_time': 20}, {}),
    # },
]


@dataclass
class FaceOff(utils.Stats):
    _dir = 'faceoffs'

    total_games: int
    black_str: str
    white_str: str
    average_time_black: float
    average_time_white: float
    average_moves_per_game: float
    average_lost_marbles_black: float
    average_lost_marbles_white: float
    games: List[str]


def main():
    for match in MATCHES:
        black = match['players'][0](*match['args'][0], **match['kwargs'][0])
        white = match['players'][1](*match['args'][1], **match['kwargs'][1])
        all_stats = []
        games = []

        total = defaultdict(int)
        for i in range(0, match['iterations']):
            print(f'[ ] Starting game {i}: {black} vs {white}')
            start = time.time()
            game, moves_history, move_stats = utils.run_game(
                black, white, is_verbose=False)
            end = time.time()
            score = game.get_score()
            total_time = end-start
            print(
                f'[x] Time to simulate: {total_time} | Total moves: {len(moves_history)}')

            game_stats = utils.GameStats(
                name_black=str(black),
                name_white=str(white),
                score_black=score[0],
                score_white=score[1],
                total_time=total_time,
                moves=move_stats,
            )
            all_stats.append(game_stats)
            games.append(game_stats.save_pickle())
        #
        total_time_black = 0
        total_time_white = 0
        total_moves_black = 0
        total_moves_white = 0
        total_games = match['iterations']
        total_marbles_lost_black = 0
        total_marbles_lost_white = 0
        for stat in all_stats:
            total_marbles_lost_black += 14 - stat.score_black
            total_marbles_lost_white += 14 - stat.score_white
            is_black = True
            for move in stat.moves:
                if is_black:
                    total_time_black += move.time
                    total_moves_black += 1
                else:
                    total_time_white += move.time
                    total_moves_white += 1

                is_black = not is_black
        FaceOff(
            total_games=total_games,
            black_str=str(black),
            white_str=str(white),
            average_time_black=total_time_black/total_moves_black,
            average_time_white=total_time_white/total_moves_white,
            average_moves_per_game=(
                total_moves_black + total_moves_white) / total_games,
            average_lost_marbles_black=total_marbles_lost_black / total_games,
            average_lost_marbles_white=total_marbles_lost_white / total_games,
            games=games,
        ).save()


if __name__ == '__main__':
    main()
