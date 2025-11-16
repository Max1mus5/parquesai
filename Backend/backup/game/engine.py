import random
from typing import Tuple
from threading import Lock
from .state import game_state
from .models import Player, Color

# Configuraciones del tablero (simplificadas)
BOARD_SIZE = 96

# posiciones de salida para cada color (ejemplo)
START_POS = {
    Color.RED: 0,
    Color.BLUE: 24,
    Color.GREEN: 48,
    Color.YELLOW: 72
}

# casillas "seguro" (ejemplo: cada 8 casillas hay una casilla de seguro)
SAFE_SQUARES = set([i for i in range(0, BOARD_SIZE, 8)])  # simplificado

_engine_lock = Lock()

def roll_dice() -> Tuple[int,int]:
    return (random.randint(1,6), random.randint(1,6))

def start_game() -> str:
    with _engine_lock:
        if len(game_state.players) < 2:
            raise Exception("Se requieren mínimo 2 jugadores")
        game_state.started = True
        game_state.block_new_join = True

        # Determinar primer turno por mayor lanzamiento (si hay empate, re-lanzar para los empatados)
        best = -1
        best_index = None
        for i, p in enumerate(game_state.players):
            d1, d2 = roll_dice()
            total = d1 + d2
            if total > best:
                best = total
                best_index = i
        game_state.current_player_index = best_index
        game_state.players[best_index].has_turn = True
        return f"Inicia {game_state.players[best_index].name}"

def _advance_turn():
    # avanza al siguiente jugador activo
    n = len(game_state.players)
    if n == 0:
        game_state.current_player_index = None
        return
    # apaga turno actual
    if game_state.current_player_index is not None:
        game_state.players[game_state.current_player_index].has_turn = False
    next_idx = (game_state.current_player_index + 1) % n
    # buscar siguiente jugador conectado
    start = next_idx
    while not game_state.players[next_idx].connected:
        next_idx = (next_idx + 1) % n
        if next_idx == start:
            # ninguno conectado
            game_state.current_player_index = None
            return
    game_state.current_player_index = next_idx
    game_state.players[next_idx].has_turn = True

def player_by_name(name: str) -> Player:
    for p in game_state.players:
        if p.name == name:
            return p
    raise Exception("Jugador no encontrado")

def player_start_position(color: Color) -> int:
    return START_POS[color]

def move_token(player_name: str, token_id: int, d1: int, d2: int) -> dict:
    with _engine_lock:
        if not game_state.started:
            raise Exception("La partida no ha iniciado")
        player = player_by_name(player_name)
        # validar que es su turno
        idx = game_state.players.index(player)
        if game_state.current_player_index != idx:
            raise Exception("No es tu turno")

        token = player.tokens[token_id]
        # regla: para sacar de cárcel necesita pares
        dice_pair = (d1 == d2)
        dice_sum = d1 + d2

        # si está en cárcel
        if token.position == -1:
            if not dice_pair:
                # no puede salir
                # si no saca pares, pasa el turno
                _advance_turn()
                return {"moved": False, "msg": "Necesitas pares para salir; turno pasado"}
            # sacar ficha a la casilla de salida
            token.position = player_start_position(player.color)
            # si sacó pares, puede lanzar de nuevo (regla: si saca pares, lanza de nuevo)
            player.turn_count_pairs += 1
            # si saca 3 pares seguidos -> puede sacar un token extra del juego (regla del enunciado)
            if player.turn_count_pairs >= 3:
                # concesión: desbloqueamos para elegir token extra (simplificado: marcar contador)
                player.turn_count_pairs = 0
                # no pasamos turno automáticamente; en la API el cliente puede pedir "usar bonus"
            return {"moved": True, "new_pos": token.position, "extra_turn": True}

        # si ya está en juego
        new_pos = (token.position + dice_sum) % BOARD_SIZE
        # proteger en casilla seguro o salida:
        if token.position in SAFE_SQUARES:
            # desde seguro no se puede comer a otro
            pass

        # verificar captura: si alguna ficha rival está en esa posición y no es seguro y no es propia
        captured = None
        for other in game_state.players:
            if other == player:
                continue
            for t in other.tokens:
                if t.position == new_pos and new_pos not in SAFE_SQUARES:
                    # enviar a cárcel
                    t.position = -1
                    captured = {"player": other.name, "token_id": t.token_id}

        token.position = new_pos

        # marcar completado si entra en su camino final (simplificamos: ningún camino final especial)
        # aquí podrías implementar la lógica de ingreso a "meta" por color

        # manejar pares: si sacó pares, mantiene turno; sino pasar
        if dice_pair:
            player.turn_count_pairs += 1
        else:
            player.turn_count_pairs = 0
            _advance_turn()

        # verificar ganador
        if player.tokens_finished():
            game_state.winner = player
            game_state.started = False
            game_state.block_new_join = False

        return {
            "moved": True,
            "new_pos": token.position,
            "captured": captured,
            "next_player": game_state.players[game_state.current_player_index].name if game_state.current_player_index is not None else None,
            "winner": game_state.winner.name if game_state.winner else None
        }
