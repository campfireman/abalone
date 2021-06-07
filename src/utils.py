import json
import os
import pickle
import time
from dataclasses import asdict, dataclass
from typing import Tuple, Union

from abalone.enums import Player

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
