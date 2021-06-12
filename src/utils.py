import json
import os
import pickle
import random
import time
from dataclasses import asdict, dataclass
from pprint import pprint
from typing import Tuple, Union

from abalone.enums import Direction, Player, Space

DATA_DIR = './data'


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


class TransitionTable:
    def __init__(self):
        self.zobrist = [[[0 for y in range(0, 9)]
                         for x in range(0, 9)] for p in range(0, 2)]
        self.table = {}
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

    def get_value(self, key: int,  marbles: dict, depth: int) -> Tuple[Tuple[Union[Space, Tuple[Space, Space]], Direction], str, float]:
        if key in self.table and self.table[key]['depth'] >= depth:
            # if self.table[key]['board'] != marbles:
            # pprint(self.table[key]['board'])
            # pprint(marbles)
            # print("CHICO")
            # print('COLLISION')
            tt_entry = self.table[key]
            return tt_entry['flag'], tt_entry['value']
        return None

    def set_value(self, key: int, value: dict):
        self.table[key] = value
