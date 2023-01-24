from collections import Iterable as _Iterable
import numpy as _np
import math as _math

from .player import Player
from . import utils as _utils

class Game:
    STATUS_000_UNAVAILABLE = 0
    STATUS_100_DRAW_QUEST = 100
    STATUS_101_BET = 101
    STATUS_102_PLAY = 102
    STATUS_103_EVALUATE_SCORE = 103
    STATUS_104_EVALUATE_BET = 104
    STATUS_200_FINISHED = 200

    def __init__(self):
        self.members = {}
        self.quest_pool = []
        self.clear()

    def clear(self):
        self.turns = 0
        self.current_quest = None
        self.playing_player_num = None
        self.status = self.STATUS_000_UNAVAILABLE
        self.__log = []

    def log(self, info : str):
        self.__log.append(info)

    @property
    def history(self):
        return '\n'.join(self.__log)

    def enroll(self, player : Player):
        if self.current_quest is not None:
            raise _utils.GameplayError('Cannot enroll when a quest is active')
        self.members[player.id] = player

    def add_quest(self, quest):
        if isinstance(quest, _Iterable):
            self.quest_pool.extend(quest)
        else:
            self.quest_pool.append(quest)

    def start(self, turns):
        self.turns = turns
        self.status = self.STATUS_100_DRAW_QUEST
        self.log(f'Starting game with {turns} turns.')

    def check_status(self, status):
        if self.status != status:
            raise _utils.GameplayError(f'Invalid operation. The current status is {self.status}')

    @property
    def finished(self):
        return self.status == self.STATUS_200_FINISHED

    def draw_quest(self):
        self.check_status(self.STATUS_100_DRAW_QUEST)

        weights = _np.array([q.weight for q in self.quest_pool])
        total_pool_size = len(self.quest_pool)
        total_weights = weights.sum()
        p = weights / total_weights
        indexes = _np.arange(0, total_pool_size, dtype=_np.int_)
        rolled = _np.random.choice(indexes, 1, replace=False, p=p).item()
        self.current_quest = self.quest_pool[rolled]
        self.playing_player_num = len(self.members)

        self.status = self.STATUS_101_BET

        self.log(f'{self.turns} turn{"s" if self.turns > 1 else ""} left. Drawing quest: {self.current_quest.description}.')
        return self.current_quest

    @property
    def decrease_score_value(self):
        return len(self.members) // 2

    def decrease_score(self, player_id):
        self.check_status(self.STATUS_101_BET)
        if not player_id in self.members:
            raise _utils.GameplayError(f'Invalid player ID: {player_id}')
        player = self.members[player_id]
        if player.score_decreased:
            raise _utils.GameplayError(f'The score is already decreased')
        player.score_decreased = True
        self.log(f'Player {player.id} voluntarily decreases the score by {self.decrease_score_value} points.')

    def bet(self, player_id, bet_id, stake=1):
        self.check_status(self.STATUS_101_BET)

        if not player_id in self.members:
            raise _utils.GameplayError(f'Invalid player ID: {player_id}')
        player = self.members[player_id]
        if player.bet is not None:
            raise _utils.GameplayError(f'Already bet')
        if bet_id is None:
            # No betting
            player.bet = player_id
            player.stake = 0
            self.playing_player_num -= 1
            if self.playing_player_num <= 0:
                self.playing_player_num = len(self.members)
                self.status = self.STATUS_102_PLAY
            self.log(f'Player {player.id} bets nothing.')
            return
        if not bet_id in self.members:
            raise _utils.GameplayError(f'Invalid player ID: {bet_id}')
        if player_id == bet_id:
            raise _utils.GameplayError(f'Cannot bet self')
        stake = max(min(int(stake), self.max_stake), 1)
        player.bet = bet_id
        player.stake = stake
        self.playing_player_num -= 1
        if self.playing_player_num <= 0:
            self.playing_player_num = len(self.members)
            self.status = self.STATUS_102_PLAY
        self.log(f'Player {player.id} bets {stake} point{"s" if stake > 1 else ""} on {bet_id}.')

    def play(self, player_id, scores : _np.ndarray):
        self.check_status(self.STATUS_102_PLAY)

        if not isinstance(scores, _Iterable):
            scores = [scores]
        scores = _utils.check_ndarray(scores)

        if not player_id in self.members:
            raise _utils.GameplayError(f'Invalid player ID: {player_id}')
        player = self.members[player_id]
        if player.current_value is not None:
            raise _utils.GameplayError(f'The player (ID {player_id}) has already completed the quest')
        value = self.current_quest.evaluator(scores)
        player.current_value = value
        self.playing_player_num -= 1
        if self.playing_player_num <= 0:
            self.playing_player_num = 0
            self.status = self.STATUS_103_EVALUATE_SCORE
        self.log(f'Player {player.id} plays the quest with score "{scores}".')

    def consume(self, player_id, score=None):
        self.check_status(self.STATUS_102_PLAY)

        if not player_id in self.members:
            raise _utils.GameplayError(f'Invalid player ID: {player_id}')
        if score is None:
            score = self.decrease_score_value
        player = self.members[player_id]
        if player.score < score:
            raise _utils.GameplayError(f'Player {player_id} does not have enough score')
        player.score -= score

        self.log(f'Player {player.id} consumes {score} point{"s" if score > 1 else ""}.')

    @property
    def score_baseline(self):
        n = len(self.members)
        return _math.ceil((n + 1) / 3)

    @property
    def max_stake(self):
        return len(self.members)

    def evaluate_score(self):
        self.check_status(self.STATUS_103_EVALUATE_SCORE)

        members = sorted(self.members.values(), reverse=False)

        baseline = self.score_baseline

        for ranking, player in enumerate(members):
            score = ranking + 1 - baseline
            player.score += score
            if player.score_decreased:
                player.score -= self.decrease_score_value

        self.status = self.STATUS_104_EVALUATE_BET

        self.log(str(self))

    def evaluate_bet(self):
        self.check_status(self.STATUS_104_EVALUATE_BET)

        members = sorted(self.members.values(), key=lambda x: x.score, reverse=True)
        top_score = members[0].score
        top_id = members[0].id
        second_top_score = members[1].score

        delta_score = [0 for i in range(len(members))]
        player_index = {x.id : i for i, x in enumerate(members)}
        for index, player in enumerate(members):
            bet = player.bet
            if bet is None:
                delta_score[index] += 0
            else:
                if top_id == player.id:
                    _top_score = second_top_score
                else:
                    _top_score = top_score
                bet_player = self.members[bet]
                if bet_player.score == _top_score:
                    delta_score[index] += player.stake
                    delta_score[player_index[bet]] -= 1
                else:
                    delta_score[index] -= player.stake
        for index, player in enumerate(members):
            player.score += delta_score[index]
            player.reset_turn()
        self.turns -= 1
        self.current_quest = None
        self.playing_player_num = None
        if self.turns <= 0:
            self.status = self.STATUS_200_FINISHED
        else:
            self.status = self.STATUS_100_DRAW_QUEST

        self.log(str(self))

    def __str__(self):
        turn = f'{self.turns} turn{"s" if self.turns > 1 else ""} left.\n'

        head = ''
        if self.status == self.STATUS_100_DRAW_QUEST:
            head = f'Drawing the next quest.\n'
        elif self.status == self.STATUS_102_PLAY:
            head = f'Playing {self.current_quest.description}.\n'
        elif self.status == self.STATUS_103_EVALUATE_SCORE:
            head = f'Evaluating scores of {self.current_quest.description}.\n'
        elif self.status == self.STATUS_104_EVALUATE_BET:
            head = f'Evaluating bet results.\n'
        if self.status == self.STATUS_104_EVALUATE_BET:
            player_infos = [
                f'{player} (result: {player.current_value}){" (decreased)" if player.score_decreased else ""} {"betting " + str(player.stake) + " point" + ("s" if player.stake > 1 else "") + " on " + player.bet if player.bet != player.id else "not betting"}'
                for player in self.members.values()
            ]
        else:
            player_infos = [f'{player}' for player in self.members.values()]
        player_infos_str = '\n'.join(player_infos)
        return f'{turn}{head}{player_infos_str}'
