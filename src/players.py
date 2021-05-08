# -*- coding: utf-8 -*-
"""This module is a collection of various AI agents"""
import copy
import random
from collections import defaultdict
from operator import itemgetter
from random import choice
from typing import List, Tuple, Union

from abalone.abstract_player import AbstractPlayer
from abalone.enums import Direction, Marble, Player, Space
from abalone.game import Game

from . import utils
from .hex import Cube


class AlphaBetaBase:
    def __init__(self, game: Game, perspective: Player, depth: int = 2, alpha: float = float('-inf'), beta: float = float('inf'), is_maximizer: bool = False, marbles: Union[Space, Tuple[Space, Space]] = None, direction: Direction = None):
        self.game = game
        self.depth = depth
        self.alpha = alpha
        self.beta = beta
        self.is_maximizer = is_maximizer
        self.marbles = marbles
        self.direction = direction
        self.player = perspective
        self.not_player = Player.BLACK.value if perspective == Player.WHITE.value else Player.BLACK.value

    def _heuristic(self, game: Game) -> float:
        raise NotImplementedError

    def _order_children(self, children: List[Game]) -> List[Game]:
        return children

    def _evaluate_move(self, result: Game, marbles: Union[Space, Tuple[Space, Space]], direction: Direction) -> float:
        return 0.0

    def _end(self, result: Tuple[int, Union[Space, Tuple[Space, Space]], Direction]):
        if self.marbles is None and self.direction is None:
            return result
        return (result[0], self.marbles, self.direction)

    def _create_children(self) -> List[Tuple[Game, Union[Space, Tuple[Space, Space]], Direction, float]]:
        result = []
        for move in self.game.generate_legal_moves():
            child = copy.deepcopy(self.game)
            child.move(*move)
            child.switch_player()
            evaluation = self._evaluate_move(child, move[0], move[1])
            if evaluation > 0:
                result.append((child, move[0], move[1], evaluation))
        return self._order_children(result)

    def run(self) -> Tuple[int, Union[Space, Tuple[Space, Space]], Direction]:
        if self.depth == 0 or utils.game_is_over(self.game.get_score()):
            return self._end((self._heuristic(self.game), None, None))
        if self.is_maximizer:
            value = (float('-inf'), None, None)
            # print(self._create_children())
            for child in self._create_children():
                value = max(value, self.__class__(
                    child[0], self.player, self.depth - 1, self.alpha, self.beta, False, child[1], child[2]).run(), key=itemgetter(0))
                self.alpha = max(self.alpha, value[0])
                if self.alpha >= self.beta:
                    break
        else:
            value = (float('inf'), None, None)
            for child in self._create_children():
                value = min(value, self.__class__(
                    child[0], self.player, self.depth - 1, self.alpha, self.beta, True, child[1], child[2]).run(), key=itemgetter(0))
                self.beta = min(self.beta, value[0])
                if self.beta <= self.alpha:
                    break
        return self._end(value)


class AlphaBetaSimple(AlphaBetaBase):
    def _order_children(self, children):
        children.sort(key=itemgetter(3), reverse=self.is_maximizer)
        return children

    def _evaluate_move(self, result: Game, marbles: Union[Space, Tuple[Space, Space]], direction: Direction) -> float:
        old_score = self.game.get_score()
        new_score = result.get_score()
        enemy_selector = 1 if self.player == Player.BLACK.value else 0
        self_selector = 0 if self.player == Player.BLACK.value else 1
        captured = old_score[enemy_selector] - new_score[enemy_selector]
        # lost = old_score[self_selector] - new_score[self_selector]
        count = 1 if isinstance(marbles, tuple) else 0
        return captured + count

    def _count_heuristics(self, game: Game) -> dict:
        result = {}
        result['sum_adjacency'] = defaultdict(int)
        result['sum_distance'] = defaultdict(int)
        center = Cube.from_board_array(4, 4)

        for y, row in enumerate(game.board):
            for x, current_marble in enumerate(row):
                if current_marble == Marble.BLANK:
                    continue
                c = Cube.from_board_array(x, y)
                # adjacency
                for neighbor in Cube.neighbor_indices():
                    n = Cube(neighbor[0], neighbor[1], neighbor[2]).add(c)
                    xn, yn = n.to_board_array()
                    if yn < 0 or xn < 0:
                        continue
                    try:
                        neighbor_marble = game.board[yn][xn]
                        if neighbor_marble == current_marble:
                            result['sum_adjacency'][current_marble.value] += 1
                    except IndexError:
                        continue
                # distance
                result['sum_distance'][current_marble.value] += c.distance(
                    center)
        return result

    def _heuristic(self, game: Game) -> float:
        '''
        TODO:
            - visualize game metrics
            - save game tree
        '''

        counts = self._count_heuristics(game)

        w_1 = 1
        w_2 = -1
        w_3 = 10000
        adjacency = counts['sum_adjacency'][self.player] - \
            counts['sum_adjacency'][self.not_player]

        distance = counts['sum_distance'][self.player] - \
            counts['sum_distance'][self.not_player]

        score = game.get_score()
        counter = score[0] if self.player == Player.BLACK.value else score[1]
        denominator = score[1] if self.player == Player.BLACK.value else score[0]
        marble_ratio = (counter / denominator)

        return w_1 * adjacency + w_2 * distance + marble_ratio * w_3


class AlphaBetaPlayer(AbstractPlayer):
    '''
    '''

    def __str__(self):
        return f'AlphaBetaPlayer_{self.version}'

    @property
    def version(self) -> str:
        return '1'

    def turn(self, game: Game, moves_history: List[Tuple[Union[Space, Tuple[Space, Space]], Direction]]) -> Tuple[Union[Space, Tuple[Space, Space]], Direction]:
        result = AlphaBetaSimple(game, game.turn).run()
        return [result[1], result[2]]
