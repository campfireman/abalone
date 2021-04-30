# -*- coding: utf-8 -*-
"""This module is a collection of various AI agents"""
import copy
import random
from operator import itemgetter
from random import choice
from typing import List, Tuple, Union

from abalone.abstract_player import AbstractPlayer
from abalone.enums import Direction, Space
from abalone.game import Game

import utils


class AlphaBetaBase:
    def __init__(self, game: Game, depth: int, alpha: float = float('-inf'), beta: float = float('inf'), is_maximizer: bool = True, marbles: Union[Space, Tuple[Space, Space]] = None, direction: Direction = None):
        self.game = game
        self.depth = depth
        self.alpha = alpha
        self.beta = beta
        self.is_maximizer = is_maximizer
        self.marbles = marbles
        self.direction = direction

    def _heuristic(self):
        raise NotImplementedError

    def _order_children(self, children: List[Game]) -> List[Game]:
        return children

    def _end(self, result: Tuple[int, Union[Space, Tuple[Space, Space]], Direction]):
        if self.marbles is None and self.direction is None:
            return result
        return (result[0], self.marbles, self.direction)

    def _create_children(self) -> List[Tuple[Game]]:
        result = []
        for move in self.game.generate_legal_moves():
            child = copy.deepcopy(self.game)
            child.move(*move)
            result.append((child, move[0], move[1]))
        return self._order_children(result)

    def run(self) -> Tuple[int, Union[Space, Tuple[Space, Space]], Direction]:
        if self.depth == 0 or utils.game_is_over(self.game.get_score()):
            return self._end((self._heuristic(), None, None))
        if self.is_maximizer:
            value = (float('-inf'), None, None)
            for child in self._create_children():
                value = max(value, self.__class__(
                    child[0], self.depth - 1, self.alpha, self.beta, False, child[1], child[2]).run(), key=itemgetter(0))
                self.alpha = max(self.alpha, value[0])
                if self.alpha >= self.beta:
                    break
        else:
            value = (float('inf'), None, None)
            for child in self._create_children():
                value = min(value, self.__class__(
                    child[0], self.depth - 1, self.alpha, self.beta, True, child[1], child[2]).run(), key=itemgetter(0))
                self.beta = min(self.beta, value[0])
                if self.beta <= self.alpha:
                    break
        return self._end(value)


class AlphaBetaSimple(AlphaBetaBase):
    def _heuristic(self):
        return random.randrange(-100, 100)


class AlphaBetaPlayer(AbstractPlayer):
    '''
    TODO:
        - basic heuristic
        - ordering of nodes
    '''

    def turn(self, game: Game, moves_history: List[Tuple[Union[Space, Tuple[Space, Space]], Direction]]) -> Tuple[Union[Space, Tuple[Space, Space]], Direction]:
        result = AlphaBetaSimple(game, 3).run()
        return [result[1], result[2]]
