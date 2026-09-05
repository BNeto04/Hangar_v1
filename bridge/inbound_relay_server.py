#!/usr/bin/env python3
"""
inbound_relay_server.py — Micro-servidor local de sinalização para a extensão do ChatGPT.
Porta 8765 / CORS habilitado / Dedupe e state persistente.
"""

import json
import logging
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [inbound-relay] %(levelname)s: %(message)s")
logger = logging.getLogger("inbound-relay")

STATE_FILE = Path(r"C:\Users\PICHAU\Downloads\circuito\runtime\.inbound_wake_state.json")
STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text("utf-8"))
        except Exception:
            pass
    return {"pending_wake": False, "message_id": None, "call_id": None, "text": "v", "acked_at": None}

def save_state(s):
    STATE_FILE.write_text(json.dumps(s, indent=2), "utf-8")

class InboundHandler(BaseHTTPRequestHandler):
    def _set_cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/status":
            state = load_state()
            if state.get("pending_wake"):
                logger.info(f"GET /status consultado com PENDING_WAKE ativo para {state.get('message_id')}")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors()
            self.end_headers()
            self.wfile.write(json.dumps(state).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        
        if self.path == "/ack":
            try:
                data = json.loads(body)
                state = load_state()
                if data.get("message_id") == state.get("message_id"):
                    state["pending_wake"] = False
                    state["acked_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    save_state(state)
                    logger.info(f"ACK recebido para {data.get('message_id')}. Pending desativado.")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._set_cors()
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
        elif self.path == "/arm_wake":
            try:
                data = json.loads(body)
                state = load_state()
                state["pending_wake"] = True
                state["message_id"] = data.get("message_id")
                state["call_id"] = data.get("call_id")
                state["text"] = data.get("text", "v")
                save_state(state)
                logger.info(f"Wake armado para {state['message_id']} ({state['call_id']}).")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._set_cors()
                self.end_headers()
                self.wfile.write(b'{"status":"armed"}')
            except Exception as e:
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def run_server(port=8765):
    server = ThreadingHTTPServer(("127.0.0.1", port), InboundHandler)
    logger.info(f"Inbound Relay Server ouvindo em http://127.0.0.1:{port}")
    server.serve_forever()

if __name__ == "__main__":
    import time
    run_server()
