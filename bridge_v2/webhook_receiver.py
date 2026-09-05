#!/usr/bin/env python3
"""
bridge_v2/webhook_receiver.py — Receptor Primário de Webhooks do GitHub (V2).
Porta 8766 / Validação HMAC SHA-256 / Filtro PR #1 / Dedupe Global / Resposta < 200ms.
Porta P-EXT-BRIDGE-V2-01 / Hangar_v1/EXTERNAL/BRIDGE_V2
"""

import hashlib
import hmac
import json
import logging
import os
import sys
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bridge_v2.daily_journal import DailyCircuitJournal
from bridge_v2.schema import normalize_call_envelope
from bridge_v2.state_manager import CleanroomStateManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [webhook-v2] %(levelname)s: %(message)s")
logger = logging.getLogger("webhook-v2")

DEFAULT_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "hangar_v1_webhook_secret_soberano")


def verify_signature(payload_bytes: bytes, signature_header: Optional[str], secret: str) -> bool:
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)


class WebhookV2Handler(BaseHTTPRequestHandler):
    state_mgr = CleanroomStateManager()
    journal = DailyCircuitJournal()
    webhook_secret = DEFAULT_SECRET

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "service": "webhook-receiver-v2",
                "timestamp": time.time()
            }).encode("utf-8"))
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/github-webhook":
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get("Content-Length", 0))
        payload_bytes = self.rfile.read(content_length)
        sig_header = self.headers.get("X-Hub-Signature-256")
        event_type = self.headers.get("X-GitHub-Event", "")
        delivery_id = self.headers.get("X-GitHub-Delivery", "no-delivery-id")

        # 1. Validação Fail-Closed HMAC
        if not verify_signature(payload_bytes, sig_header, self.webhook_secret):
            logger.warning(f"Rejeitada requisição sem HMAC válido (delivery={delivery_id})")
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":"Invalid signature"}')
            return

        # 2. Ping
        if event_type == "ping":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"msg":"pong"}')
            return

        if event_type != "issue_comment":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"msg":"ignored non-issue-comment"}')
            return

        try:
            data = json.loads(payload_bytes.decode("utf-8"))
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        action = data.get("action")
        issue_number = data.get("issue", {}).get("number")
        comment = data.get("comment", {})
        comment_id = comment.get("id")
        raw_body = comment.get("body", "")

        if action != "created" or issue_number != 1:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"msg":"ignored non-PR1 created"}')
            return

        # 3. Normalização e Deduplicação
        envelope = normalize_call_envelope(raw_body, comment_id=comment_id)
        if not envelope:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"msg":"ignored non-CALL"}')
            return

        mid = envelope["message_id"]
        cid = envelope["call_id"]

        if self.state_mgr.is_duplicate(comment_id=comment_id, delivery_id=delivery_id, message_id=mid, call_id=cid):
            logger.info(f"Comentário {comment_id} ({mid}) já processado. Ignorando duplicata.")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"msg":"already processed"}')
            return

        # 4. Entrega e Registro
        self.state_mgr.deliver_to_inbox(envelope["body"], message_id=mid, call_id=cid)
        self.state_mgr.mark_processed(comment_id=comment_id, delivery_id=delivery_id, message_id=mid, call_id=cid)

        self.journal.record_event(
            event_type="CALL_RECEIVED",
            actor_from="CHATGPT",
            actor_to="ANTIGRAVITY",
            channel="GITHUB_PR1",
            summary=f"CALL recebida via Webhook primário: {mid} ({cid})",
            message_id=mid,
            call_id=cid,
            reply_to=envelope.get("reply_to"),
            github_comment_id=comment_id,
            status="DELIVERED_TO_INBOX",
        )

        logger.info(f"CALL {mid} processada e entregue com sucesso via Webhook primário!")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "delivered", "message_id": mid}).encode("utf-8"))

    def log_message(self, format, *args):
        pass


def run_webhook_server(port=8766):
    server = ThreadingHTTPServer(("127.0.0.1", port), WebhookV2Handler)
    logger.info(f"Webhook Receiver V2 rodando em http://127.0.0.1:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run_webhook_server()
