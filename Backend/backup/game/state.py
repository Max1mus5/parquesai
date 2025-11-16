from threading import Lock
from typing import List, Optional
from .models import Player, Color

class GameState:
    def __init__(self):
        self.players: List[Player] = []
        self.started: bool = False
        self.current_player_index: Optional[int] = None
        self.lock = Lock()
        self.block_new_join = False
        self.winner: Optional[Player] = None

    def add_player(self, player: Player):
        with self.lock:
            if self.block_new_join or self.started or len(self.players) >= 4:
                raise Exception("No se puede unir ahora")
            # evitar colores duplicados
            for p in self.players:
                if p.color == player.color:
                    raise Exception("Color ya seleccionado")
            self.players.append(player)

    def to_dict(self):
        return {
            "players": [p.to_dict() for p in self.players],
            "started": self.started,
            "current_player_index": self.current_player_index,
            "winner": self.winner.name if self.winner else None
        }

game_state = GameState()
