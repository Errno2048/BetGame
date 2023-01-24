import os as _os
import json as _json
import numpy as _np
import re as _re

from .. import utils as _utils, QuestInfo as _QuestInfo, evaluators as _evaluators

def arcaea_score(score, pure, far, lost, combo):
    return _np.array([score, pure, far, lost, combo])

# Considers only score
regular_arcaea_evaluator = _evaluators.score_value(0)

def regular_arcaea_quest(song, weight):
    level = song['level']
    level_name = str(int(level))
    if level - int(level) > 0:
        level_name += '+'

    difficulty = song['difficulty']
    difficulty_name = '?'
    if difficulty == 0:
        difficulty_name = 'Past'
    elif difficulty == 1:
        difficulty_name = 'Present'
    elif difficulty == 2:
        difficulty_name = 'Future'
    elif difficulty == 3:
        difficulty_name = 'Beyond'

    song_name = song['name']
    artist_name = song['artist']
    description = f'{song_name} ({artist_name}) [{difficulty_name} {level_name}]'

    return _QuestInfo(weight, description, regular_arcaea_evaluator)

_song_package_file = _os.path.dirname(_os.path.abspath(__file__)) + _os.path.sep + 'songlist'
with open(_song_package_file, 'r', encoding='utf8') as f:
    _song_package_raw = _json.load(f)
    _song_package = {}
    for _song in _song_package_raw['songs']:
        _package = _song['set']
        _package_list = _song_package.setdefault(_package, {})
        _base_info = {
            'id': _song['id'],
            'name': _song['title_localized']['en'],
            'artist': _song['artist'],
            'package': _package,
        }
        for _dif in _song['difficulties']:
            _difficulty = _dif['ratingClass']
            _level = _dif['rating'] + (0.7 if _dif.get('ratingPlus', False) else 0.0)
            _diff_list = _package_list.setdefault(_level, [])
            _dif_info = {
                **_base_info,
                'level': _level,
                'difficulty': _difficulty,
                'charter': _dif['chartDesigner'],
            }
            if 'title_localized' in _dif:
                _dif_info['name'] = _dif['title_localized']['en']
            _diff_list.append(_dif_info)

def arcaea_level(value : str):
    if _re.match(r'^[0-9]+(?:\.[0-9]+)?$', value):
        level = float(value)
    elif _re.match(r'^[0-9]+\+$', value):
        level = float(value[:-1]) + 0.7
    else:
        level = None
    return level

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
        level_weights = {k : 1.0 for k in levels.keys()}
        difficulty_enabled = [True, True, True, True]
        ban_song_id = set()
        for i in range(0, len(args), 2):
            arg1, arg2 = args[i], args[i + 1]
            mode = 0
            if isinstance(arg1, int) or isinstance(arg1, float):
                mode = 1
                arg1 = float(arg1)
            elif isinstance(arg1, str):
                _level = arcaea_level(arg1)
                if _level:
                    arg1 = _level
                    mode = 1
                else:
                    difficulties = {'pst': 0, 'prs': 1, 'ftr': 2, 'byd': 3}
                    _arg1 = arg1.lower()
                    if _arg1 in difficulties:
                        mode = 2
                        arg1 = _arg1
                    elif _arg1 == 'ban':
                        mode = 3

            if mode == 1:
                level, weight = arg1, arg2
                if not isinstance(weight, int) and not isinstance(weight, float):
                    raise _utils.SettingsError(f'Invalid weight: {weight}')
                weight = max(weight, 0)
                level_weights[level] = weight
            elif mode == 2:
                difficulties = {'pst': 0, 'prs': 1, 'ftr': 2, 'byd': 3}
                difficulty_enabled[difficulties[arg1]] = bool(arg2)
            elif mode == 3:
                ban_song_id.add(arg2)
        quests = []
        for level, songs in levels.items():
            songs = list(filter(lambda x: difficulty_enabled[x['difficulty']] and not x['id'] in ban_song_id, songs))
            for song in songs:
                quest = regular_arcaea_quest(song, weight=level_weights[level] / len(songs))
                quests.append(quest)
        return quests

song_package_manager = SongPackageManager()

try:
    from PIL import Image as _Image
    import ddddocr as _ocr

    def _image_normalize(image : _Image.Image):
        numpy_image = _np.array(image)
        height, width, channels = numpy_image.shape
        ratio = width / height
        normalized_ratio = 16 / 9
        if ratio > normalized_ratio:
            normalized_width = round(height * normalized_ratio)
            x_start = (width - normalized_width) // 2
            return numpy_image[:, x_start : x_start + normalized_width, :]
        elif ratio < normalized_ratio:
            normalized_height = round(width / normalized_ratio)
            y_start = (height - normalized_height) // 2
            return numpy_image[y_start : y_start + normalized_height, :]
        return numpy_image

    def _image_clip(image : _np.ndarray, x1, y1, x2, y2, filter=False):
        height, width, channels = image.shape
        x_start, x_end = round(x1 * width), round(x2 * width)
        y_start, y_end = round(y1 * height), round(y2 * height)
        res = image[y_start : y_end, x_start : x_end, :]
        if filter:
            res_channel_avg = res.mean(axis=-1).reshape(*res.shape[:-1], 1)
            res_filtered = (((res > 96) & (res < 192)).sum(axis=-1) == channels) \
                           & (((res - res_channel_avg) < 8).sum(axis=-1) == channels)
            res_filtered = res_filtered.reshape(*res_filtered.shape, 1)
            res = res * res_filtered + _np.ones_like(res, dtype=res.dtype) * 255 * ~res_filtered
        return _Image.fromarray(res)

    def _image_ocr(image : _Image.Image):
        ocr = _ocr.DdddOcr(show_ad=False)
        res = ocr.classification(image)
        res = ''.join(filter(lambda x: x in '0123456789', res))
        return int(res)

    def ocr_score(image : _Image.Image):
        score_rect = (0.375, 0.4, 0.625, 0.475)
        combo_rect = (0.1375, 0.275, 0.21, 0.325)
        pure_rect = (0.5, 0.71, 0.562, 0.77)
        far_rect = (0.5, 0.77, 0.562, 0.82)
        lost_rect = (0.5, 0.82, 0.562, 0.87)
        normalized = _image_normalize(image)

        score = _image_ocr(_image_clip(normalized, *score_rect))
        pure = _image_ocr(_image_clip(normalized, *pure_rect, True))
        far = _image_ocr(_image_clip(normalized, *far_rect, True))
        lost = _image_ocr(_image_clip(normalized, *lost_rect, True))
        combo = _image_ocr(_image_clip(normalized, *combo_rect))

        return arcaea_score(score, pure, far, lost, combo)
except ImportError as e:
    pass
