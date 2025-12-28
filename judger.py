class Judger:
    def __init__(self):
        self.rank_order = ["3","4","5","6","7","8","9","T","J","Q","K","A","2","B","R"]

    @classmethod
    def NewJudger(cls):
        judger_instance = cls()
        # Judger can hold rule tables, rank orders, combination validators
        judger_instance.rank_order = ["3","4","5","6","7","8","9","T","J","Q","K","A","2","B","R"]
        return judger_instance

    def IsGameOver(self, players):
        # Game over if any player has zero cards in hand
        for p in players:
            if len(p.GetHand()) == 0:
                return True
        return False

    def GetWinner(self, players):
        # Return the id of the first player with empty hand; if none, return -1
        for p in players:
            if len(p.GetHand()) == 0:
                return p.GetId()
        return -1

    def CalculatePayoff(self, winner_id: int, landlord_id: int):
        payoff = {}
        # initialize all to 0
        for id_ in range(0, 3):
            payoff[id_] = 0

        if winner_id == landlord_id:
            payoff[landlord_id] = 1
            # peasants remain 0
        else:
            # Both peasants win
            for id_ in range(0, 3):
                if id_ != landlord_id:
                    payoff[id_] = 1

        return payoff
