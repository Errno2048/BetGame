import numpy as _np
from collections import Iterable as _Iterable
from . import utils as _utils

def constant(value):
    if not isinstance(value, _Iterable):
        value = _np.array([value])
    def evaluator(scores : _np.ndarray):
        return value
    return evaluator

def score_value(score_index):
    def evaluator(scores : _np.ndarray):
        return scores[score_index]
    return evaluator

def by_score(score_index, *score_list):
    if len(score_list) == 0:
        raise _utils.SettingsError(f'Invalid arguments for by_score generator: {score_list}')
    def evaluator(scores : _np.ndarray):
        score = scores[score_index]
        res = score_list[0]
        for i in range(1, len(score_list), 2):
            score_thres, new_res = score_list[i], score_list[i + 1]
            if score >= score_thres:
                res = new_res
        return res
    return evaluator

def sum(*evaluators):
    if len(evaluators):
        raise _utils.SettingsError('sum requires at least one evaluator function')
    def evaluator(scores : _np.ndarray):
        res = evaluators[0](scores)
        for i in range(1, len(evaluators)):
            res = res + evaluators[i](scores)
        return res
    return evaluator

def max(*evaluators):
    if len(evaluators):
        raise _utils.SettingsError('max requires at least one evaluator function')
    def evaluator(scores : _np.ndarray):
        res = []
        for i in range(len(evaluators)):
            res.append(evaluators[i](scores))
        res = _np.stack(res, axis=0).max(axis=0)
        return res
    return evaluator

def min(*evaluators):
    if len(evaluators):
        raise _utils.SettingsError('min requires at least one evaluator function')
    def evaluator(scores : _np.ndarray):
        res = []
        for i in range(len(evaluators)):
            res.append(evaluators[i](scores))
        res = _np.stack(res, axis=0).min(axis=0)
        return res
    return evaluator

def condition_constant(value : bool):
    def success_condition(scores, evaluated):
        return value
    return success_condition

def condition_by_score(score_index, min_score, max_score):
    def success_condition(scores, evaluated):
        return min_score <= scores[score_index] <= max_score
    return success_condition

def condition_by_evaluated(min_score, max_score):
    def success_condition(scores, evaluated):
        return min_score <= evaluated <= max_score
    return success_condition

def condition_and(*conditions):
    if len(conditions):
        raise _utils.SettingsError('condition_and requires at least one condition function')
    def success_condition(scores, evaluated):
        res = True
        for i in range(len(conditions)):
            res &= conditions[i](scores, evaluated)
        return res
    return success_condition

def condition_or(*conditions):
    if len(conditions):
        raise _utils.SettingsError('condition_or requires at least one condition function')
    def success_condition(scores, evaluated):
        res = False
        for i in range(len(conditions)):
            res |= conditions[i](scores, evaluated)
        return res
    return success_condition
