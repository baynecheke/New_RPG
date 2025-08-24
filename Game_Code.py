class Game_code:
    def __init__(self):
        self.score = 0
        self.level = 1

    def start_game(self):
        print("Game started!")
        self.score = 0
        self.level = 1

    def play(self):
        print("Playing the game...")
        self.score += 10

    def end_game(self):
        print("Game over!")
        print(f"Final score: {self.score}")