#!/usr/bin/env python3
"""
bridge_v2/inbound_relay.py — Micro-servidor local de sinalização para a extensão do ChatGPT (V2).
Porta 8765 / CORS total / Injeção de CONTEXT_PACKET ao invés de V puro.
Porta P-EXT-BRIDGE-V2-01 / Hangar_v1/EXTERNAL/BRIDGE_V2
"""

import json
import logging
import os
import sys
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bridge_v2.daily_journal import DailyCircuitJournal
from bridge_v2.state_manager import WAKE_STATE_FILE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [inbound-relay-v2] %(levelname)s: %(message)s")
logger = logging.getLogger("inbound-relay-v2")


def load_wake_state():
    if WAKE_STATE_FILE.exists():
        try:
            return json.loads(WAKE_STATE_FILE.read_text("utf-8"))
        except Exception:
            pass
    return {"pending_wake": False, "message_id": None, "call_id": None, "text": "", "acked_at": None}


def save_wake_state(state_dict):
    WAKE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = WAKE_STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state_dict, indent=2, ensure_ascii=False), "utf-8")
    tmp.replace(WAKE_STATE_FILE)


class InboundV2Handler(BaseHTTPRequestHandler):
    journal = DailyCircuitJournal()

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
            state = load_wake_state()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors()
            self.end_headers()
            self.wfile.write(json.dumps(state).encode("utf-8"))
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._set_cors()
            self.end_headers()
            self.wfile.write(b'{"status":"healthy","service":"inbound-relay-v2"}')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")

        if self.path == "/ack":
            try:
                data = json.loads(body) if body else {}
                state = load_wake_state()
                mid = data.get("message_id")
                if not mid or mid == state.get("message_id"):
                    state["pending_wake"] = False
                    state["acked_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    save_wake_state(state)
                    logger.info(f"ACK recebido da extensão para {mid}. pending_wake desativado.")
                    self.journal.record_event(
                        event_type="CONTEXT_PACKET_DELIVERED",
                        actor_from="EXTENSION",
                        actor_to="CHATGPT",
                        channel="CHATGPT",
                        summary=f"Extensão injetou CONTEXT_PACKET no ChatGPT para {mid}.",
                        message_id=mid,
                        call_id=state.get("call_id"),
                        status="DELIVERED",
                    )
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
                state = load_wake_state()
                mid = data.get("message_id") or f"RESULT-{int(time.time()*1000)}"
                call_id = data.get("call_id") or "TASK"
                packet_text = data.get("text") or data.get("context_packet") or ""

                state["pending_wake"] = True
                state["message_id"] = mid
                state["call_id"] = call_id
                state["text"] = packet_text
                save_wake_state(state)

                logger.info(f"Wake armado com sucesso com CONTEXT_PACKET para {mid} ({call_id}).")
                self.journal.record_event(
                    event_type="WAKE_ARMED",
                    actor_from="BRIDGE_V2",
                    actor_to="EXTENSION",
                    channel="BRIDGE_V2",
                    summary=f"Armado CONTEXT_PACKET para injeção no ChatGPT ({mid}).",
                    message_id=mid,
                    call_id=call_id,
                    status="ARMED",
                )
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._set_cors()
                self.end_headers()
                self.wfile.write(b'{"status":"armed"}')
            except Exception as e:
                logger.error(f"Erro ao armar wake: {e}")
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def run_server(port=8765):
    server = ThreadingHTTPServer(("127.0.0.1", port), InboundV2Handler)
    logger.info(f"Inbound Relay V2 ouvindo em http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
