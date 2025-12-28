from typing import List, Tuple, Optional
from card import Card

class Round:
    def __init__(self, players, judger):
        self.players = players
        self.judger = judger
        self.action_trace: List[Tuple[int, str]] = []
        self.played_cards: List[Card] = []
        self.last_non_pass_player: Optional[int] = None
        self.consecutive_passes = 0

    @staticmethod
    def ActionToString(action):
        s = ""
        for c in action:
            s = s + c.rank
        return s

    @classmethod
    def NewRound(cls, players, judger):
        round_instance = cls(players, judger)
        round_instance.players = players
        round_instance.judger = judger
        round_instance.action_trace = []
        round_instance.played_cards = []
        round_instance.last_non_pass_player = None
        round_instance.consecutive_passes = 0
        return round_instance

    def GetLastValidPlay(self):
        # Returns a tuple of (player_id, action_string) for the last non-pass play, or null if none.
        if self.last_non_pass_player is None:
            return None

        # Find the most recent action by the last non-pass player from the trace.
        for i in range(len(self.action_trace) - 1, -1, -1):
            player_id, action_str = self.action_trace[i]
            if player_id == self.last_non_pass_player:
                return (player_id, action_str)

        # Should not be reached if last_non_pass_player is not null, but as a fallback:
        return None

    def RecordAction(self, player_id: int, action):
        # Record the action in trace and update played_cards and pass counters
        if len(action) == 0:
            # pass
            self.action_trace.append((player_id, "pass"))
            self.consecutive_passes = self.consecutive_passes + 1
            # when pass, do not add cards to played_cards
        else:
            # convert played cards to string for trace (compact by ranks)
            action_str = Round.ActionToString(action)
            self.action_trace.append((player_id, action_str))
            for c in action:
                self.played_cards.append(c)
            # reset pass counter since someone played
            self.consecutive_passes = 0
            self.last_non_pass_player = player_id

        # If two consecutive passes after a play, the "pile" clears — but full game logic tracks only for turn order.
        return

    def GetNextPlayer(self, current_player_id: int) -> int:
        # players are in sequence by their id order in round.players
        # find index of current_player_id
        n = len(self.players)
        next_index = -1
        for i in range(0, n):
            if self.players[i].GetId() == current_player_id:
                next_index = (i + 1) % n
                break
        if next_index == -1:
            # fallback to 0
            return self.players[0].GetId()
        return self.players[next_index].GetId()

    def GetActionTrace(self):
        # Return a copy of the trace for safety
        return list(self.action_trace)

    def GetAllPlayedCards(self):
        # Return sorted list of played card ranks as strings (single-char per card)
        ranks_list: List[str] = []
        for c in self.played_cards:
            ranks_list.append(c.rank)
        order_map = {r: i for i, r in enumerate(self.judger.rank_order)}
        ranks_list.sort(key=lambda ch: order_map.get(ch, -1))
        return ranks_list