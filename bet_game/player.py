class Player:
    def __init__(self, id):
        self.id = id
        self.score = 0
        self.bet = None
        self.current_value = None
        self.stake = None
        self.score_decreased = False

    def reset_turn(self):
        self.bet = None
        self.current_value = None
        self.stake = None
        self.score_decreased = False

    def __lt__(self, other):
        if self.current_value is not None and other.current_value is not None and self.current_value != other.current_value:
            return self.current_value < other.current_value
        return self.score > other.score

    def __str__(self):
        return f'{self.id} ({self.score})'
