import threading
import time
from typing import Dict
from .state import game_state

# Implementación simplificada: el servidor actúa como maestro y periódicamente
# "sincroniza" relojes de jugadores (aquí simulados). En una implementación
# real, cada cliente respondería con su timestamp y el maestro ajusta.
class BerkeleySync(threading.Thread):
    def __init__(self, interval=30):
        super().__init__(daemon=True)
        self.interval = interval
        self.running = True

    def run(self):
        while self.running:
            time.sleep(self.interval)
            # En este ejemplo, sólo registramos que se produjo una sincronización.
            # En la práctica: mandar mensaje a clientes pidiendo timestamp, calcular offset, enviar ajuste.
            with game_state.lock:
                if game_state.started:
                    print("[Berkeley] sincronización de relojes: partida en curso.")
                else:
                    print("[Berkeley] sincronización: no hay partida activa.")

    def stop(self):
        self.running = False
