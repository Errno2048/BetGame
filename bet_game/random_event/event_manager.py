import numpy as _np

from .. import utils as _utils

class EventManager:
    def __init__(self):
        self.bought = 0
        self.applied = 0
        self.last_ranking = []

    def status_check(self, func):
        if not self.bought :
            return -1
        elif not self.applied :
            return -1
    
    def card_print(self):
        """ 1.所有对他人下注的目标按上轮总分位次将目标后移一个人
        2.若目标为你的下注都失败了，在最后结算环节将这些下注总分将平均分给你和所有这次打歌得零分的人
        3.所有未进行下注的玩家加n/4（向上取整）分
        4.取消本轮的所有下注失败惩罚
        5.本轮打歌得分从低到高计算
        6.所有人亮成绩后，你在[本轮最低成绩，满分]范围内roll一个分数出来作为你的本轮打歌成绩
        7.你本轮打歌成绩强制视为理论值
        8.你花的分数打水漂了！哈哈哈哈哈哈哈 """
        pass

    def target_twist(self):
        pass
    
    def score_modifier_ahead(self):
        pass

    def score_modifier_delayed(self):
        pass
    
    def playscore_modifier(self):
        pass
    
        

