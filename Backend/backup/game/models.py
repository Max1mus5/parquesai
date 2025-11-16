from enum import Enum
from typing import List, Optional

class Color(str, Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"

class Ficha:
    def __init__(self, token_id: int):
        self.token_id = token_id
        self.position: int = -1  # -1 = cárcel
        self.completed: bool = False

    def to_dict(self):
        return {
            "token_id": self.token_id,
            "position": self.position,
            "completed": self.completed
        }

class Player:
    def __init__(self, name: str, color: Color):
        self.name = name
        self.color = color
        self.tokens: List[Ficha] = [Ficha(i) for i in range(4)]
        self.connected: bool = True
        self.turn_count_pairs = 0  # contador de pares consecutivos
        self.has_turn: bool = False

    def tokens_finished(self):
        return all(t.completed for t in self.tokens)

    def to_dict(self):
        return {
            "name": self.name,
            "color": self.color.value,
            "tokens": [t.to_dict() for t in self.tokens],
            "connected": self.connected,
            "has_turn": self.has_turn
        }
