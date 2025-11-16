import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from typing import List
from game.models import Player, Color
from game.state import game_state
from game.engine import start_game, roll_dice, move_token
from game.sync import BerkeleySync
import threading

app = FastAPI()
# WebSocket manager simple
class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)
    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)
    async def broadcast(self, message: dict):
        for conn in list(self.active):
            try:
                await conn.send_json(message)
            except Exception:
                self.disconnect(conn)

manager = ConnectionManager()

# lanzar hilo de Berkeley al inicio
berkeley = BerkeleySync(interval=20)
berkeley.start()

@app.post("/join")
def join(name: str, color: Color):
    try:
        player = Player(name=name, color=color)
        game_state.add_player(player)
        return {"msg": "Jugador registrado", "state": game_state.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/start")
def api_start():
    try:
        msg = start_game()
        return {"msg": msg, "state": game_state.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/roll/{player_name}")
def api_roll(player_name: str):
    # devolvemos dados; mover lo hace cliente pidiendo /move
    d1, d2 = roll_dice()
    return {"dice": [d1, d2]}

@app.post("/move/{player_name}")
def api_move(player_name: str, token_id: int, d1: int, d2: int):
    try:
        result = move_token(player_name, token_id, d1, d2)
        # broadcast simple a websockets
        import asyncio
        asyncio.create_task(manager.broadcast({"type":"update", "state": game_state.to_dict(), "event": result}))
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await manager.connect(ws)
    try:
        # enviar estado inicial
        await ws.send_json({"type":"state", "state": game_state.to_dict()})
        while True:
            data = await ws.receive_json()  # cliente puede enviar pings o acciones
            # ejemplo de manejo rápido: {"cmd":"ping"}
            if data.get("cmd") == "ping":
                await ws.send_json({"cmd":"pong"})
    except WebSocketDisconnect:
        manager.disconnect(ws)

if __name__ == "__main__":
    # lanzar server TCP opcional en hilo
    import sockets.tcp_server as tcp_mod
    t = threading.Thread(target=tcp_mod.run_tcp_server, daemon=True)
    t.start()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
