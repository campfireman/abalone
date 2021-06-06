# -*- coding: utf-8 -*-
"""This module is a collection of various AI agents"""
from __future__ import annotations

import copy
import random
from collections import defaultdict
from math import floor
from operator import itemgetter
from random import choice
from typing import List, Tuple, Union

from abalone.abstract_player import AbstractPlayer
from abalone.enums import Direction, Marble, Player, Space
from abalone.game import Game
from abalone.hex import Cube
from abalone.utils import line_to_edge, space_to_board_indices

from . import utils


class AlphaBetaBase:
    def __init__(self, game: Game, perspective: Player, depth: int = 3, alpha: float = float('-inf'), beta: float = float('inf'), is_maximizer: bool = True, marbles: Union[Space, Tuple[Space, Space]] = None, direction: Direction = None):
        self.game = game
        self.depth = depth
        self.alpha = alpha
        self.beta = beta
        self.is_maximizer = is_maximizer
        self.marbles = marbles
        self.direction = direction
        self.player = perspective
        self.not_player = Player.BLACK.value if perspective == Player.WHITE.value else Player.WHITE.value

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
            result.append((child, move[0], move[1], evaluation))
        result = self._order_children(result)[:30]
        return result

    def run(self) -> Tuple[int, Union[Space, Tuple[Space, Space]], Direction]:
        if self.depth == 0 or utils.game_is_over(self.game.get_score()):
            return self._end((self._heuristic(self.game), None, None))
        if self.is_maximizer:
            value = (float('-inf'), None, None)
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
        if utils.game_is_over(new_score):
            w_0 = 10000
            winner = utils.get_winner(new_score)
            # return as winning or losing move
            return w_0 * 1 if winner.value == self.player else w_0 * -1
        enemy_selector = 1 if self.player == Player.BLACK.value else 0
        self_selector = 0 if self.player == Player.BLACK.value else 1

        captured = old_score[enemy_selector] - new_score[enemy_selector]
        lost = new_score[self_selector] - old_score[self_selector]

        multiple = 0
        if isinstance(marbles, tuple):
            c1 = Cube.from_board_array(*space_to_board_indices(marbles[0]))
            c2 = Cube.from_board_array(*space_to_board_indices(marbles[1]))
            multiple = c1.distance(c2)
        else:
            line = line_to_edge(marbles, direction)
            own_marbles_num, opp_marbles_num = self.game._inline_marbles_nums(
                line)
            multiple = own_marbles_num - 1

        # weights for the linear combination
        w_0 = 1
        w_1 = 3
        return w_0 * multiple + w_1 * captured + w_1 * lost

    def _count_heuristics(self, game: Game) -> dict:
        result = {}
        result['sum_adjacency'] = defaultdict(int)
        result['sum_distance'] = defaultdict(int)
        center = Cube.from_board_array(4, 4)

        for y, row in enumerate(game.board):
            for x, current_marble in enumerate(row):
                if current_marble == Marble.BLANK:
                    continue
                c = Cube.from_board_array(y, x)
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
        '''
        score = game.get_score()
        if utils.game_is_over(score):
            w_0 = 100000
            winner = utils.get_winner(score)
            return w_0 * 1 if winner.value == self.player else w_0 * -1
        counts = self._count_heuristics(game)

        adjacency = counts['sum_adjacency'][self.player] - \
            counts['sum_adjacency'][self.not_player]

        distance = counts['sum_distance'][self.player] - \
            counts['sum_distance'][self.not_player]

        counter = score[0] if self.player == Player.BLACK.value else score[1]
        denominator = score[1] if self.player == Player.BLACK.value else score[0]
        marble_ratio = (counter / denominator)

        w_0 = 1
        w_1 = -1
        w_2 = 10000
        heuristic = w_0 * adjacency + w_1 * distance + w_2 * marble_ratio
        return heuristic


class AlphaBetaSimpleUnordered(AlphaBetaSimple):
    def _order_children(self, children):
        return children


class AlphaBetaPlayer(AbstractPlayer):
    '''
    '''

    def __str__(self):
        return f'AlphaBetaPlayer_{self.version}'

    @property
    def version(self) -> str:
        return '1'

    def turn(self, game: Game, moves_history: List[Tuple[Union[Space, Tuple[Space, Space]], Direction]]) -> Tuple[Union[Space, Tuple[Space, Space]], Direction]:
        result = AlphaBetaSimple(
            game, game.turn.value).run()
        print(result[0])
        return [result[1], result[2]]


class MctsNode:
    def __init__(self, game: Game, parent: MctsNode, marbles: Union[Space, Tuple[Space, Space]] = None, direction: Direction = None):
        self.game = game
        self.parent = parent
        self.marbles = marbles
        self.direction = direction
        self.black_stats = 0
        self.white_stats = 0
        self.children = []

    @property
    def stats(self) -> (int, int):
        return (self.black_stats, self.white_stats)

    def append_child(self, child: MctsNode):
        self.children.append(child)

    def update_stats(self, new: Tuple[int, int]):
        self.black_stats += new[0]
        self.white_stats += new[1]


class MonteCarloSearch:
    def __init__(self, game: Game, playouts=5, max_plies=200):
        self.game = game
        self.playouts = playouts
        self.max_plies = max_plies
        self.player = self.game.turn.value
        self.not_player = self.game.not_in_turn_player().value

    def run(self) -> Tuple[Union[Space, Tuple[Space, Space]], Direction]:
        root = MctsNode(self.game, None)
        child_count = 0
        for move in self.game.generate_legal_moves():
            next_state = copy.deepcopy(self.game)
            next_state.move(*move)
            next_state.switch_player()
            child = MctsNode(next_state, root, *move)
            sim_count = 0
            child_count += 1
            root.append_child(child)
            for _ in range(self.playouts):
                result = self.playout(child)
                child.update_stats(result)
                self.backpropagate(child, result)
                sim_count += 1
                # print(f'child_count: {child_count} sim_count: {sim_count}')
        return self.choose_best(root)

    def choose_best(self, root: MctsNode) -> Tuple[Union[Space, Tuple[Space, Space]], Direction]:
        best = None
        for child in root.children:
            if best is None:
                best = child
            else:
                if best.stats[self.player] < child.stats[self.player]:
                    best = child
        return (best.marbles, best.direction)

    def backpropagate(self, node: MctsNode, result: Tuple[int, int]):
        while (node.parent != None):
            node.parent.update_stats(result)
            node = node.parent

    def playout_policy(self, state: game):
        # legal_moves = list(state.generate_legal_moves())
        # return choice(legal_moves)
        return state.generate_random_move()

    def playout(self, node: MctsNode):
        plies = 0
        state = copy.deepcopy(node.game)
        score = state.get_score()
        while (plies < self.max_plies and not utils.game_is_over(score)):
            move = self.playout_policy(state)
            state.move(*move)
            state.switch_player()
            score = state.get_score()
            plies += 1
        if score[0] > score[1]:
            return (1, 0)
        elif score[0] < score[1]:
            return (0, 1)
        else:
            return (0, 0)


class MonteCarloPlayer(AbstractPlayer):
    def turn(self, game: Game, moves_history: List[Tuple[Union[Space, Tuple[Space, Space]], Direction]]) -> Tuple[Union[Space, Tuple[Space, Space]], Direction]:
        result = MonteCarloSearch(game).run()
        return result
