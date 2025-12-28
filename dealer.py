import random
from card import Card

class Dealer:
    def __init__(self):
        self.deck = []

    @staticmethod
    def CreateFullDeck():
        deck = []
        suits = ["Spade", "Heart", "Club", "Diamond"]
        ranks = ["3","4","5","6","7","8","9","T","J","Q","K","A","2"]

        for suit in suits:
            for rank in ranks:
                card = Card(rank=rank, suit=suit)
                deck.append(card)

        # Add two jokers
        deck.append(Card(rank="B", suit=None))    # Black Joker
        deck.append(Card(rank="R", suit=None))    # Red Joker

        return deck

    @staticmethod
    def EvaluateHandHeuristic(hand_str: str) -> int:
        # Count high ranks and jokers and pairs/triples
        score = 0
        frequency = {}
        for ch in hand_str:
            if ch in frequency:
                frequency[ch] = frequency[ch] + 1
            else:
                frequency[ch] = 1

        # Award points for powerful ranks
        for rank_char, count in frequency.items():
            # Jokers are strongest
            if rank_char == "R":
                score = score + 50 * count
            elif rank_char == "B":
                score = score + 45 * count
            elif rank_char == "2":
                score = score + 20 * count
            elif rank_char == "A":
                score = score + 12 * count
            elif rank_char == "K":
                score = score + 8 * count
            elif rank_char == "Q":
                score = score + 6 * count
            elif rank_char == "J":
                score = score + 5 * count
            elif rank_char == "T":
                score = score + 4 * count
            else:
                score = score + 1 * count

            # Award combos
            if count == 2:
                score = score + 10   # pair
            elif count == 3:
                score = score + 25   # triple
            elif count == 4:
                score = score + 40   # bomb

        return score

    @classmethod
    def NewDealer(cls):
        dealer_instance = cls()
        dealer_instance.deck = Dealer.CreateFullDeck()
        return dealer_instance

    def ShuffleDeck(self):
        # Fisher-Yates shuffle on a copy of dealer's deck
        deck_to_shuffle = list(self.deck)
        n = len(deck_to_shuffle)
        for i in range(n - 1, 0, -1):
            j = random.randint(0, i)
            temp = deck_to_shuffle[i]
            deck_to_shuffle[i] = deck_to_shuffle[j]
            deck_to_shuffle[j] = temp
        return deck_to_shuffle

    def Deal(self, deck):
        # Expect deck length == 54
        hands = [[], [], []]
        # Deal first 51 cards round-robin (17 each) and keep last 3 as seen_cards
        for i in range(0, 51):
            player_index = i % 3
            hands[player_index].append(deck[i])

        seen_cards = []
        for i in range(51, 54):
            seen_cards.append(deck[i])

        return (hands, seen_cards)

    def DetermineLandlord(self, players):
        # Heuristic: compute a simple hand-strength score for each player's current hand string
        # Use GetHandAsString accessor to avoid reaching into Player internals.
        best_score = float("-inf")
        landlord_id = 0

        for player in players:
            hand_str = player.GetHandAsString()
            score = Dealer.EvaluateHandHeuristic(hand_str)
            if score > best_score:
                best_score = score
                landlord_id = player.GetId()

        # In tie cases the first max remains; ensure landlord_id is valid
        return landlord_id
