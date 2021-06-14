import json
import os
import pickle
import random
import time
from collections import defaultdict
from dataclasses import asdict, dataclass
from pprint import pprint
from traceback import format_exc
from typing import Generator, List, Tuple, Union

from abalone.abstract_player import AbstractPlayer
from abalone.enums import Direction, Player, Space
from abalone.game import Game, IllegalMoveException
from abalone.utils import line_from_to

DATA_DIR = './data'


def format_move(turn: Player, move: Tuple[Union[Space, Tuple[Space, Space]], Direction], moves: int) -> str:
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


def game_is_over(score: Tuple[int, int]) -> bool:
    return 8 in score


def get_winner(score: Tuple[int, int]) -> Union[Player, None]:
    """Returns the winner of the game based on the current score.

    Args:
        score: The score tuple returned by `abalone.game.Game.get_score`

    Returns:
        Either the `abalone.enums.Player` who won the game or `None` if no one has won yet.
    """
    if 8 in score:
        return Player.WHITE if score[0] == 8 else Player.BLACK
    return None


def write_to_file(obj, filename):
    with open(os.path.join(DATA_DIR, filename), 'wb') as file:
        pickle.dump(obj, file)


def open_from_file(filename) -> dict:
    with open(os.path.join(DATA_DIR, filename), 'rb') as file:
        return pickle.load(file)


def write_to_file_json(obj, filename):
    with open(os.path.join(DATA_DIR, filename), 'w') as file:
        file.write(json.dumps(obj, indent=4, sort_keys=True))


@dataclass
class Stats:
    def save(self):
        path = os.path.join(DATA_DIR, self._dir)
        os.makedirs(path, exist_ok=True)
        write_to_file_json(asdict(self), os.path.join(
            self._dir, f'{time.time()}.json'))


@dataclass
class MoveStats:
    no: int
    space: str
    direction: Direction
    time: float


@dataclass
class GameStats(Stats):
    name_black: str
    name_white: str
    score_black: int
    score_white: int
    total_time: float
    moves: List[MoveStats]

    _dir = 'games'

    def save_pickle(self) -> str:
        print(f'[ ] Saving {self.name_black} vs {self.name_white}')
        filename = time.time()
        path = os.path.join(
            self._dir, f'{filename}.pickle')
        write_to_file(asdict(self), path)
        print(f'[x] Save {path}')
        return filename

    @classmethod
    def print(cls, filename):
        pprint(open_from_file(os.path.join(cls._dir, filename)))


class Storage:
    def __init__(self):
        self.zobrist = [[[0 for y in range(0, 9)]
                         for x in range(0, 9)] for p in range(0, 2)]
        self.table = {}
        self.heuristic_cache = {}
        self.children_cache = {}
        self.initialize_keys()

    def initialize_keys(self):
        '''
        Generate Zobrist hash keys
        '''
        for p in range(0, 2):
            for x in range(0, 9):
                for y in range(0, 9):
                    self.zobrist[p][x][y] = random.getrandbits(64) - 2**63

    def get_key(self, marbles: dict):
        '''
        Get the state at the key
        '''
        key = 0
        for player in marbles.keys():
            p = 0 if player == Player.BLACK.value else 1
            for x in marbles[player].keys():
                for y in marbles[player][x].keys():
                    key ^= self.zobrist[p][x][y]
        return key

    def get_tt_value(self, key: int,  marbles: dict, depth: int) -> Tuple[Tuple[Union[Space, Tuple[Space, Space]], Direction], str, float]:
        if key in self.table and self.table[key]['depth'] >= depth:
            tt_entry = self.table[key]
            return tt_entry['flag'], tt_entry['value']
        return None

    def set_tt_value(self, key: int, value: dict):
        self.table[key] = value

    def get_cache_value(self, key: int):
        return self.heuristic_cache.get(key, None)

    def set_cache_value(self, key: int, value: float):
        self.heuristic_cache[key] = value

    def get_cached_children(self, key: int):
        return self.children_cache.get(key, None)

    def set_cached_children(self, key: int, value: list):
        self.children_cache[key] = value


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

        winner = get_winner(score)
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
                print(format_move(game.turn, move,
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
