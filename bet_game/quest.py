import numpy as _np
import typing as _typing

from . import evaluators as _evaluators

class QuestInfo:
    def __init__(
        self,
        weight : float = 1.0,
        description : str = '',
        evaluator : _typing.Callable[[_np.ndarray, _typing.Any], _np.ndarray] = _evaluators.constant(0),
        #success_condition : _typing.Callable[[_np.ndarray, _typing.Any, _typing.Any], _np.ndarray] = _evaluators.condition_constant(True),
    ):
        self.weight = weight
        self.description = description
        self.evaluator = evaluator
        #self.success_condition = success_condition

    def __str__(self):
        return self.description
