class ChosenPrompt:
    def __init__(self, prompt, players):
        self.prompt = prompt
        self.players = players
        # maps player ids to their answers
        self.answers = {}

    def answer(self, player_id: int, answer):
        self.answers[player_id] = answer
