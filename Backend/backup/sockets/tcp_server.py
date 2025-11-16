import socket
import threading
import json
from typing import Tuple

HOST = "0.0.0.0"
PORT = 9009

def handle_client(conn: socket.socket, addr: Tuple[str,int]):
    with conn:
        print(f"Conexión desde {addr}")
        try:
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                # protocolo simple: JSON per line
                try:
                    msg = json.loads(data.decode())
                except Exception:
                    conn.send(b'{"error":"invalid json"}')
                    continue
                # ejemplo: {"cmd":"ping"}
                if msg.get("cmd") == "ping":
                    conn.send(b'{"pong": true}')
                else:
                    conn.send(b'{"error":"unknown command"}')
        except Exception as e:
            print("Client handler error:", e)

def run_tcp_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    print(f"TCP server listening on {HOST}:{PORT}")
    try:
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn,addr), daemon=True)
            t.start()
    except KeyboardInterrupt:
        s.close()
