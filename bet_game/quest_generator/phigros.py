import os as _os
import json as _json
import numpy as _np
import re as _re

from .. import utils as _utils, QuestInfo as _QuestInfo, evaluators as _evaluators

def phigros_score(
    score, 
    perfect = 0, 
    good = 0, 
    bad = 0, 
    miss = 0,
    combo = 0):
    return _np.array([score, perfect, good, bad, miss, combo])

# Considers only score
regular_phigros_evaluator = _evaluators.score_value(0)

def regular_phigros_quest(song, weight):
    level = song['level']
    level_name = str(int(level))
    if level - int(level) > 0:
        level_name += '+'

    difficulty = song['difficulty']
    difficulty_name = '?'
    if difficulty == 0:
        difficulty_name = 'EZ'
    elif difficulty == 1:
        difficulty_name = 'HD'
    elif difficulty == 2:
        difficulty_name = 'IN'
    elif difficulty == 3:
        difficulty_name = 'AT'

    song_name = song['name']
    artist_name = song['artist']
    description = f'{song_name} ({artist_name}) [{difficulty_name} {level_name}]'

    return _QuestInfo(weight, description, regular_phigros_evaluator)

def phigros_diff_split(diff_str):
    if _re.search(r'[0-9]+\s*\([0-9]+\.[0-9]+\)', diff_str):
        rough, detailed = _re.findall(r'(?P<rough>[0-9]+)\s*\((?P<detailed>[0-9]+\.[0-9]+)\)', diff_str)[0]
        return int(rough), float(detailed)
    else:
        return 0, 0

_song_package_file = _os.path.dirname(_os.path.abspath(__file__)) + _os.path.sep + 'phigros_songlist'
with open(_song_package_file, 'r', encoding='utf8') as f:
    _song_package_raw = _json.load(f)
    _song_package = {}
    diffname_list = ['EZ', 'HD', 'IN', 'AT']
    for _song in _song_package_raw:
        _package = _song['Pack']
        _package_list = _song_package.setdefault(_package, {})
        _base_info = {
            'id': "",
            'name': _song['Title'],
            'artist': _song['Artist'],
            'package': _package,
        }
        for diff_num in range(4):
            _level, _level_detailed = phigros_diff_split(_song[diffname_list[diff_num]])
            _diff_list = _package_list.setdefault(_level, [])
            if _level:
                _dif_info = {
                    **_base_info,
                    'level': _level,
                    'level_detailed': _level_detailed,
                    'difficulty': diff_num,
                }
                _diff_list.append(_dif_info)

def phigros_level(value : str):
    if _re.match(r'^[0-9]+(?:\.[0-9]+)?$', value):
        level = float(value)
        detailed = 1
    elif _re.match(r'^[0-9]+$', value):
        level = float(value)
        detailed = 0
    else:
        level = None
        detailed = None
    return level, detailed

class SongPackageManager:
    def __init__(self, info=None):
        if info is None:
            self.__info = _song_package
        else:
            self.__info = info
        self.__enabled = {'base'}
        self.__quest_list_cache = None

    def available_packages(self):
        return list(self.__info.keys())

    def enable_all(self):
        self.__enabled.update(self.__info.keys())
        self.__quest_list_cache = None

    def disable_all(self):
        self.__enabled.clear()
        self.__quest_list_cache = None

    def enabled_packages(self):
        return list(self.__enabled)

    def disabled_packages(self):
        return list(set(self.available_packages()).difference(self.enabled_packages()))

    def enable(self, package):
        if not package in self.__info:
            raise _utils.SettingsError(f'Invalid package name {package}')
        self.__enabled.add(package)
        self.__quest_list_cache = None

    def disable(self, package):
        self.__enabled.discard(package)
        self.__quest_list_cache = None

    def quest_list(self, *args):
        if self.__quest_list_cache:
            levels = self.__quest_list_cache
        else:
            levels = {}
            for package in self.__enabled:
                package_songs = self.__info.get(package, {})
                for level, songs in package_songs.items():
                    _level_songs = levels.setdefault(level, [])
                    _level_songs.extend(songs)
            self.__quest_list_cache = levels
        level_weights = {k : 0.0 for k in levels.keys()}
        difficulty_enabled = [True, True, True, True]
        ban_song_id = set()
        for i in range(0, len(args), 2):
            arg1, arg2 = args[i], args[i + 1]
            mode = 0
            if isinstance(arg1, int) or isinstance(arg1, float):
                mode = 1
                arg1 = float(arg1)
            elif isinstance(arg1, str):
                _level, _detailed = phigros_level(arg1)
                if _level:
                    arg1 = _level
                    mode = 1
                else:
                    difficulties = {'EZ': 0, 'HD': 1, 'IN': 2, 'AT': 3}
                    _arg1 = arg1.upper()
                    if _arg1 in difficulties:
                        mode = 2
                        arg1 = _arg1
                    elif _arg1 == 'BAN':
                        mode = 3

            if mode == 1:
                level, weight = arg1, arg2
                if not isinstance(weight, int) and not isinstance(weight, float):
                    raise _utils.SettingsError(f'Invalid weight: {weight}')
                weight = max(weight, 0)
                level_weights[level] = weight
            elif mode == 2:
                difficulties = {'EZ': 0, 'HD': 1, 'IN': 2, 'AT': 3}
                difficulty_enabled[difficulties[arg1]] = bool(arg2)
            elif mode == 3:
                ban_song_id.add(arg2)
        quests = []
        for level, songs in levels.items():
            songs = list(filter(lambda x: difficulty_enabled[x['difficulty']] and not x['id'] in ban_song_id, songs))
            for song in songs:
                quest = regular_phigros_quest(song, weight=level_weights[level] / len(songs))
                quests.append(quest)
        return quests

song_package_manager = SongPackageManager()
