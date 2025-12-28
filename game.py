from typing import List, Dict
from dealer import Dealer
from judger import Judger
from player import Player
from round import Round
from action_generator import ActionGenerator

class Game:
    def __init__(self):
        self.players: List[Player] = []
        self.dealer: Dealer = None
        self.judger: Judger = None
        self.round: Round = None
        self.seen_cards = []
        self.action_generator: ActionGenerator = None
        self.landlord_id = None

    def GetOthersHandAsString(self, exclude_player_id: int) -> str:
        # Combine other two players' hands into a single compact string
        combined = ""
        for p in self.players:
            if p.GetId() == exclude_player_id:
                continue
            combined = combined + p.GetHandAsString()
        # sort combined by rank order for deterministic representation
        # Use judger's rank order if available
        order_map = {"3":0,"4":1,"5":2,"6":3,"7":4,"8":5,"9":6,"T":7,"J":8,"Q":9,"K":10,"A":11,"2":12,"B":13,"R":14}
        chars = list(combined)
        chars.sort(key=lambda ch: order_map.get(ch, -1))
        result = ""
        for ch in chars:
            result = result + ch
        return result

    def BuildState(self, current_player_id: int, landlord_id: int, seen_cards, legal_actions: List[str]) -> Dict:
        current_hand = self.players[current_player_id].GetHandAsString()
        others_hand = self.GetOthersHandAsString(current_player_id)
        trace = self.round.GetActionTrace()
        played_cards = self.round.GetAllPlayedCards()

        # Convert seen_cards hand to compact string
        seen_str = ""
        for c in seen_cards:
            seen_str = seen_str + c.rank

        state = {
            "self": current_player_id,
            "current_hand": current_hand,
            "others_hand": others_hand,
            "actions": legal_actions,
            "trace": trace,
            "landlord": landlord_id,
            "seen_cards": seen_str,
            "played_cards": played_cards
        }
        return state

    def DisplayResults(self, winner_id: int, payoff: Dict[int, int]) -> None:
        if winner_id == -1:
            print("No winner determined.")
        else:
            print("Game winner: Player", winner_id)
        print("Payoff:")
        for id_ in range(0, 3):
            print(" Player", id_, ":", payoff[id_])

        # Optionally print final hands and trace for debugging
        print("Final hands (post-play):")
        for p in self.players:
            print(" Player", p.GetId(), "role=", p.GetRole(), "hand=", p.GetHandAsString())
        print("Action trace:")
        trace = self.round.GetActionTrace()
        for entry in trace:
            print(entry)
        return

    @classmethod
    def NewGame(cls) -> 'Game':
        game = cls()
        # create players
        game.players = [ Player.NewPlayer(0),
                         Player.NewPlayer(1),
                         Player.NewPlayer(2) ]
        game.dealer = Dealer.NewDealer()
        game.judger = Judger.NewJudger()
        game.round = Round.NewRound(game.players, game.judger)
        game.seen_cards = []
        game.action_generator = ActionGenerator.NewActionGenerator()
        game.landlord_id = None
        return game

    def Run(self) -> None:
        # Step 1: Setup deck and deal
        deck = self.dealer.ShuffleDeck()
        (hands, seen_cards) = self.dealer.Deal(deck)
        self.seen_cards = seen_cards

        # Step 2: Assign hands to players
        for i in range(0, 3):
            self.players[i].SetHand(hands[i])

        # Step 3: Determine landlord heuristically and give seen cards
        landlord_id = self.dealer.DetermineLandlord(self.players)
        self.landlord_id = landlord_id

        # Add seen cards to landlord's hand
        for i in range(0, 3):
            if self.players[i].GetId() == landlord_id:
                self.players[i].AddCards(seen_cards)
                self.players[i].SetRole("landlord")
            else:
                self.players[i].SetRole("peasant")

        # Step 4: Game loop begins with landlord
        current_player_id = landlord_id

        # Safety cap to prevent infinite loops in buggy implementations
        turn_count = 0
        max_turns = 163

        while not self.judger.IsGameOver(self.players):
            if turn_count >= max_turns:
                print("Reached max turns, aborting game loop.")
                break
            current_player = self.players[current_player_id]
            legal_actions = self.action_generator.GetLegalActions(current_player, self.round)
            # Build state for the current player
            state = self.BuildState(current_player_id, landlord_id, seen_cards, legal_actions)

            # Get player's chosen action
            action = self.players[current_player_id].SelectAction(state)

            if not action:
                action_as_string = "pass"
            else:
                action_as_string = self.round.ActionToString(action)

            is_legal = False
            for legal_action_str in state["actions"]:
                if action_as_string == legal_action_str:
                    is_legal = True
                    break

            if not is_legal:
                # Fallback for an invalid action returned by the Player module.
                print("Warning: Player", current_player_id, "returned an illegal action. Choosing a valid fallback.")

                fallback_action_str = state["actions"][0]

                # We need to convert the fallback string back to a PlayAction object for processing
                action = self.players[current_player_id].ParseActionStringToCards(fallback_action_str) 

            # Apply the action to the round and the player
            self.round.RecordAction(current_player_id, action)
            self.players[current_player_id].RemoveCards(action)

            # Check for winner immediately
            if self.judger.IsGameOver(self.players):
                break

            # Determine next player
            current_player_id = self.round.GetNextPlayer(current_player_id)
            turn_count = turn_count + 1

        # Step 5: Calculate payoff and display results
        winner_id = self.judger.GetWinner(self.players)
        payoff = self.judger.CalculatePayoff(winner_id, self.landlord_id)
        self.DisplayResults(winner_id, payoff)
        return
