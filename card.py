from dataclasses import dataclass
from typing import Optional

@dataclass
class Card:
    rank: str
    suit: Optional[str]  # None for jokers
