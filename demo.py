from bet_game.quest_generator.arcaea import song_package_manager, arcaea_score
from bet_game import Game, Player

song_package_manager.enable('core')
song_package_manager.enable('rei')
song_package_manager.enable('yugamu')
song_package_manager.enable('prelude')
song_package_manager.enable('vs')

regular_quests = song_package_manager.quest_list(
    'pst', False, # 禁用past，默认为启用
    'prs', False, # 禁用present
    'ftr', True, # 启用future
    'byd', False, # 禁用beyond
    '7', 1.0, # 7级歌曲的总权重为1.0，默认为1.0
    '8', 2.0,
    '9', 3.0,
    '9+', 3.0,
    '10', 2.0,
    '10+', 1.0,
    '11', 0.0,
    '12', 0.0,
    'ban', 'dropdead', # 禁止出现id为dropdead的歌曲
    'ban', 'fallensquare',
    'ban', 'altale',
    'ban', 'ifi',
)

game = Game()
game.add_quest(regular_quests)
game.enroll(Player(id='player1'))
game.enroll(Player(id='player2'))
game.enroll(Player(id='player3'))
game.enroll(Player(id='player4'))

# 总回合数为2
game.start(turns=2)

# turn 1
# 抽取本轮的任务
game.draw_quest()
print(game, '\n')

# player1选择下注，目标为player2，押2分
# 歌曲结算后，若在除了player1以外的所有玩家中，player2的总积分最高，则player1得2分，player2失去固定的1分
# 否则player1失去2分
# 下注的最大值为game.max_stake
game.bet('player1', 'player2', 2)

game.bet('player2', 'player1', 1)
game.bet('player3', 'player1', 1)

# player4选择不下注，当所有玩家下注完毕后进入打歌阶段
game.bet('player4', None)

# player1的得分为9950000，pure、far、lost和combo分别为1、2、3、4
game.play('player1', arcaea_score(9950000, 1, 2, 3, 4))

game.play('player2', arcaea_score(9900000, 0, 0, 0, 0))
game.play('player3', arcaea_score(9850000, 0, 0, 0, 0))
game.play('player4', arcaea_score(9800000, 0, 0, 0, 0))

# 结算歌曲得分，倒数第k名得到k-game.score_baseline分，4人时按排名得分分别为2、1、0、-1
game.evaluate_score()

print(game, '\n')

# 结算本轮下注
game.evaluate_bet()

print(game, '\n')

# turn 2
game.draw_quest()
print(game, '\n')

# 在下注阶段，player1可以自愿让自己减少game.decrease_score_value分，该操作属于保护机制，每个玩家一回合只能用一次
game.decrease_score('player1')

game.bet('player1', 'player2', 1)
game.bet('player2', 'player1', 3)
game.bet('player3', 'player1', 3)
game.bet('player4', 'player1', 3)

print(game, '\n')

game.play('player1', arcaea_score(9950000, 0, 0, 0, 0))
game.play('player2', arcaea_score(9900000, 0, 0, 0, 0))
game.play('player3', arcaea_score(9850000, 0, 0, 0, 0))
game.play('player4', arcaea_score(9800000, 0, 0, 0, 0))

game.evaluate_score()

print(game, '\n')

game.evaluate_bet()

print(game, '\n')

# game.finished为True时表示游戏已结束
print(game.finished)