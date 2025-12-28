from typing import List, Dict
from card import Card

class Player:
    def __init__(self, id_: int):
        self.id = id_
        self.hand: List[Card] = []
        self.role = "peasant"

    @staticmethod
    def CardsEqual(a: Card, b: Card) -> bool:
        return (a.rank == b.rank) and ((a.suit == b.suit) or (a.suit is None) or (b.suit is None))

    @staticmethod
    def SortHand(player: 'Player') -> None:
        # Simple stable sort by rank ordering then suit; maps rank to order index
        order_map = {"3":0,"4":1,"5":2,"6":3,"7":4,"8":5,"9":6,"T":7,"J":8,"Q":9,"K":10,"A":11,"2":12,"B":13,"R":14}
        player.hand.sort(key=lambda card: (order_map.get(card.rank, -1), card.suit if card.suit is not None else ""))

    def ParseActionStringToCards(self, action_str: str):
        # Convert a compact string action into actual Card objects picked from player's hand.
        # e.g., "K" -> choose one K from player's hand, "8222" -> choose one '8' and three '2's
        result: List[Card] = []
        if action_str == "pass":
            return result

        # Build a map from rank -> list of indices in hand
        rank_to_indices: Dict[str, List[int]] = {}
        for i in range(0, len(self.hand)):
            r = self.hand[i].rank
            if r not in rank_to_indices:
                rank_to_indices[r] = []
            rank_to_indices[r].append(i)

        # For each char in action_str, pop one available card of that rank
        for ch in action_str:
            if (ch in rank_to_indices) and (len(rank_to_indices[ch]) > 0):
                idx = rank_to_indices[ch].pop()   # take one matching card
                # Add copy(self.hand[idx]) to result
                c = self.hand[idx]
                result.append(Card(rank=c.rank, suit=c.suit))
            else:
                # Fallback: if not available on hand, attempt to construct synthetic Card (shouldn't happen)
                result.append(Card(rank=ch, suit=None))

        return result

    def GetHand(self):
        return [Card(rank=c.rank, suit=c.suit) for c in self.hand]

    def GetId(self) -> int:
        return self.id

    def GetRole(self) -> str:
        return self.role

    def GetHandAsString(self) -> str:
        # Convert hand into compact string ordered by rank mapping used elsewhere.
        # Use rank characters only (suit omitted) for compactness like '345...R'
        rank_order = ["3","4","5","6","7","8","9","T","J","Q","K","A","2","B","R"]
        bucket = {ch: 0 for ch in rank_order}
        for card in self.hand:
            ch = card.rank
            bucket[ch] = bucket.get(ch, 0) + 1

        result = ""
        for r in rank_order:
            count = bucket.get(r, 0)
            for _ in range(1, count + 1):
                result = result + r
        return result

    @classmethod
    def NewPlayer(cls, id_: int) -> 'Player':
        player_instance = cls(id_)
        player_instance.id = id_
        player_instance.hand = []
        player_instance.role = "peasant"   # default
        return player_instance

    def SetHand(self, hand):
        self.hand = [Card(rank=c.rank, suit=c.suit) for c in hand]

    def SetRole(self, role: str):
        self.role = role

    def AddCards(self, cards):
        # Append cards to player's hand
        for card in cards:
            self.hand.append(card)
        # Keep deterministic ordering: sort hand by Rank ordering then suit (optional)
        Player.SortHand(self)

    def RemoveCards(self, cards):
        # For each card in action, find and remove one matching card from hand
        for played_card in cards:
            removed = False
            for i in range(0, len(self.hand)):
                if Player.CardsEqual(self.hand[i], played_card):
                    del self.hand[i]
                    removed = True
                    break
            if not removed:
                # Defensive: if card not found, raise/print error and ignore (shouldn't happen)
                print("Warning: attempted to remove card not in hand for player", self.id)
        # Maintain order
        Player.SortHand(self)

    def SelectAction(self, state):
        # 职责：只从给定的合法动作列表中选择一个。
        legal_action_strings = state["actions"]

        # 策略: 选择一个最长的非"pass"动作 (贪心策略)
        chosen_str = "pass"
        max_len = 0
        if legal_action_strings:
            # 如果列表为空(不应发生但做防御)，则默认pass
            chosen_str = legal_action_strings[0]  # 至少有一个动作
            for act_str in legal_action_strings:
                if act_str != "pass" and len(act_str) > max_len:
                    max_len = len(act_str)
                    chosen_str = act_str

        # 如果没有找到可出的牌（除了pass），并且pass是合法选项，则选择pass
        if max_len == 0 and ("pass" in legal_action_strings):
            chosen_str = "pass"

        if chosen_str == "pass":
            return []
        else:
            return self.ParseActionStringToCards(chosen_str)
