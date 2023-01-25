import numpy as _np
from collections.abc import Iterable as _Iterable

class GameError(Exception):
    pass

class SettingsError(GameError):
    pass

class GameplayError(GameError):
    pass

def check_ndarray(value):
    if not isinstance(value, _np.ndarray):
        if isinstance(value, _Iterable):
            value = _np.array(value)
        else:
            raise SettingsError(f'{value.__class__} object is not iterable : {value}')
    return value

def check_type(value, type, info='Invalid type'):
    if not isinstance(value, type):
        raise SettingsError(f'{info} {value.__class__} : {value}')

def multiplier_transform(value : _np.ndarray, multiplier : _np.ndarray) -> _np.ndarray:
    if not isinstance(value, _np.ndarray):
        if not isinstance(value, _Iterable):
            value = _np.array([value])
        else:
            value = _np.array(value)
    base_value = _np.ones_like(value)
    res = _np.zeros_like(value)
    for index in range(multiplier.shape[0]):
        res = res + base_value * multiplier[index]
        base_value = base_value * value
    return res
