from typing import Tuple


def game_is_over(score: Tuple[int, int]) -> bool:
    return 8 in score
