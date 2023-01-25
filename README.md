# 别押我 (Bet On Me)

一个为音游玩家线下面基开发的策略性小游戏。

## 游戏规则

游戏开始之前需要完成游戏准备阶段。之后的每回合中将会进行课题抽取阶段、下注阶段、游玩阶段、排名结算阶段和下注结算阶段共5个环节。在完成指定的回合数后，游戏进入游戏结束阶段。

### 游戏准备阶段

玩家需要集体决定游戏的回合数。

还有什么？给设备充好电，擦擦手，撒点痱子粉。准备好在打不到EX的时候断网。

每个玩家将会获得初始值为0的积分。

### 课题抽取阶段

游戏管理员随机抽取一个课题。

比如抽到了dropdead [Present 9]，接下来的阶段里所有玩家就要打开Arcaea，选好自己心仪的角色，开始~~摔死~~游玩指定曲目。

如果有玩家尚未解锁该曲目，游戏管理员可以重新抽取一个课题。游戏管理员可以让所有玩家确认自己能够游玩课题。

### 下注阶段（Bet on me!）

所有玩家在此阶段选择两种行为中的一种，并仅告诉游戏管理员，不让其他玩家知道：

1. 预测本轮结算时除自己外总积分最高的玩家，并对该玩家进行下注。下注需要指定自己下注的积分，最低下注1分，最高能下注与玩家总数等同的分数~~（all in）~~。下注在本阶段不会扣除下注的积分。
2. 不下注。（注意需要明确向游戏管理员表示不下注哦）

### 游玩阶段

所有玩家游玩指定的课题并将成绩仅告诉管理员。（线下面基怎么办？link play？~~那就考验人性了~~）

### 排名结算阶段

游戏管理员对课题游玩的成绩进行结算。本阶段的排名遵循以下规则：

1. 当玩家A的课题成绩高于玩家B时，A的排名高于B；
2. 当玩家A的课题成绩等于玩家B时，若A的积分低于B，则A的排名高于B；否则A与B具有相同的排名（取高排名）。

记玩家总数为$n$，对于倒数第$k$名的玩家，其得分为$\max\left\{0, k-\left\lfloor n/2\right\rfloor \right\}$。例如当有8名玩家时，最高4名玩家分别得到4、3、2、1分，其余玩家得0分。

此外，每个玩家在下注阶段每被下注一次，在本阶段扣1分。例如玩家A被玩家B下注了2分，被玩家C下注了1分，则玩家A被扣除2分。

### 下注结算阶段（别押我！）

游戏管理员对下注的结果进行结算。

若玩家A在下注阶段对玩家B下注$x$分，当玩家B在该阶段拥有最高的总分（可并列）时，玩家A获得$x$分；否则玩家A失去$x$分。

若玩家A未进行下注，则玩家A的积分在本阶段不变。

### 游戏结束阶段

在经过指定的回合数后，按照所有玩家的总积分数量对玩家进行排名。

## 脚本使用方法

游戏通过`bet_game.game.Game`对象管理。在游戏的任意阶段，均可以调用`str(game)`得到对游戏状态的描述。

### 游戏准备阶段

以Arcaea为例，可通过以下代码准备课题池。其中`arcaea_quests`是一个数组，其中每个元素是一个`bet_game.quest.QuestInfo`对象。

```python
from bet_game.quest_generator.arcaea import song_package_manager

song_package_manager.enable('core') # 启用id为core的曲包
arcaea_quests = song_package_manager.quest_list(
    'pst', False, # 禁用past难度，默认为启用
    'prs', False, # 禁用present难度
    'ftr', True, # 启用future难度
    'byd', False, # 禁用beyond难度
    '7', 1.0, # 7级歌曲的总权重为1.0，默认为1.0
    '8', 2.0,
    '9', 3.0,
    '9+', 3.0,
    '10', 2.0,
    '10+', 1.0,
    '11', 0.0, # 当权重为0时不会被抽取
    '12', 0.0,
    'ban', 'dropdead', # 禁止出现id为dropdead的歌曲
    'ban', 'fallensquare',
    'ban', 'altale',
)
```

此外，可通过以下方式自定义课题。

```python
from bet_game import QuestInfo, evaluators

# 将分数的第3个值（far）和第4个值（lost）加起来作为总分
custom_evaluator = evaluators.sum(
    evaluators.score_value(2), 
    evaluators.score_value(3),
)

custom_quest = QuestInfo(
    weight=1.0, # 课题被抽中的权重
    description='游玩dropdead并按照far和lost的总数结算分数',
    evaluator=custom_evaluator,
)
```

在自定义课题后，通过以下方式设置游戏的轮数和玩家的名称。

```python
from bet_game import Game, Player

game = Game()
game.add_quest([*arcaea_quests, custom_quest]) # 加入指定的课题
game.enroll(Player(id='player1')) # 加入ID为player1的玩家
game.enroll(Player(id='player2'))

game.start(5) # 开始游戏，设定为5个回合
```

### 课题抽取阶段

通过以下方式抽取本轮的课题。

```python
quest = game.draw_quest()

quest = game.draw_quest() # 在没有选手下注时，可重新抽取课题
game.current_quest.description # 可通过该字段查看任务的描述
```

### 下注阶段

通过以下方式选择下注或不下注。

```python
game.bet('player1', None) # player1选择不下注
game.bet('player2', 'player1', 1) # player2对player1下注1分
```

在所有选手完成下注（或不下注）后，自动进入下一个阶段。

### 游玩阶段

通过以下方式录入选手的游玩成绩。

```python
from bet_game.quest_generator.arcaea import arcaea_score

game.play('player1', 9950000) # player1的分数为9950000
game.play('player2', arcaea_score(9900000, pure=1000, far=10, lost=10, combo=500))
# 或game.play('player2', [9900000, 1000, 10, 10, 500])
# player2的分数为9900000，pure数为1000，far数为10，lost数为10，最大连击为500
```

在录入所有选手的成绩后，自动进入下一个阶段。

### 排名结算阶段

通过以下方式结算课题成绩排名。

```python
game.evaluate_score()
```

### 下注结算阶段

通过以下方式结算下注。

```py
game.evaluate_bet()
```

在完成下注结算后，若当前回合不是最后一个回合，则自动进入下一个回合；否则结束游戏。

## API Reference

### 关于evaluator

`QuestInfo`对象的构造方法需要传递一个evaluator参数。该参数是满足以下定义的函数。

```python
import numpy as np
from typing import Union

def evaluator(scores : np.ndarray) -> Union[int, float, np.ndarray]:
    ...
    return value
```

其中`np.ndarray`对象需要满足仅有一个元素（即可以调用`item()`方法）。

`bet_game.evaluators`提供了一系列evaluator函数的生成器。

- `constant(value)`: 产生仅返回固定值`value`的evaluator。
- `score_value(score_index)`: 提取指定位的成绩并作为evaluator的返回值。
- `by_score(score_index, *score_list)`: 提取指定位的成绩并按照指定的分段计算返回值。例如`by_score(0, 0, 9500000, 1, 9800000, 2)`表示提取第1位的成绩（此处表示得分），当成绩小于9500000时返回0，大于等于9500000但小于9800000时返回1，否则返回2。
- `multiply(multiplier, evaluator)`: 对evaluator的输出进行多项式变换。其中若`multiplier`为数值，则结果乘以`multiplier`；若`multiplier`是数组，则进行多项式变换，例如对于`multiplier=[1.0, 2.0, 3.0]`，当输入值为$x$时返回值为$3.0x^2+2.0x+1.0$。
- `sum(*evaluators)`: 将所有输入evaluator的结果相加。
- `max(*evaluators)`: 在所有输入evaluator的结果中取最大值。
- `min(*evaluators)`: 在所有输入evaluator的结果中取最小值。

## 安装至Bot？

🕊🕊🕊🕊🕊🕊🕊🕊🕊🕊🕊🕊🕊🕊🕊🕊