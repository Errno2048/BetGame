from bet_game.quest_generator.phigros import song_package_manager, phigros_score
from bet_game import Game, Player

song_package_manager.enable('Single-单曲精选集')
song_package_manager.enable('Chapter Legacy 过去的章节')
song_package_manager.enable('Chapter 4 管道迷宫')
song_package_manager.enable('Chapter 5 霓虹灯牌')
song_package_manager.enable('Chapter 6 方舟蜃景')
song_package_manager.enable('Chapter 7 时钟链接')

regular_quests = song_package_manager.quest_list(
    'EZ', False,
    'HD', False,
    'IN', True,
    'AT', True,
    '13', 1.0,
    '14', 2.0,
    '15', 3.0, # 15级歌曲的总权重为3.0，默认为1.0
    '16', 1.0,
    # 'ban', 'Sigma (Haocore Mix) ~ Regrets of The Yellow Tulip ~',
    # 'ban', 'Sigma (Haocore Mix) ~ 105秒の伝説 ~',
    # 'ban', 'Spasmodic(Haocore Mix)',
    # 'ban', 'Introduction',
    # 以上四首在特殊曲包内，选定曲包的话不用ban
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

game.bet('player2', 'player3', 1)
game.bet('player3', 'player1', 1)

# player4选择不下注，当所有玩家下注完毕后进入打歌阶段
game.bet('player4', None)

# player1的得分为995000，perfect、good、bad、miss和combo分别为1、2、3、4
game.play('player1', phigros_score(995000, 1, 2, 3, 4, 5))

game.play('player2', phigros_score(990000, 0, 0, 0, 0, 0))
game.play('player3', phigros_score(985000, 0, 0, 0, 0, 0))
game.play('player4', phigros_score(980000, 0, 0, 0, 0, 0))

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

game.play('player1', phigros_score(995000, 0, 0, 0, 0, 0))
game.play('player2', phigros_score(990000, 0, 0, 0, 0, 0))
game.play('player3', phigros_score(985000, 0, 0, 0, 0, 0))
game.play('player4', phigros_score(980000, 0, 0, 0, 0, 0))

game.evaluate_score()

print(game, '\n')

game.evaluate_bet()

print(game, '\n')

# game.finished为True时表示游戏已结束
print(game.finished)