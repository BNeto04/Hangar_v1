#!/usr/bin/env python3
"""
github_webhook_server.py — Micro-servidor local receptor de Webhooks do GitHub.
Porta 8766 / Validação estrita HMAC SHA-256 / Dedupe por delivery_id + comment_id / Resposta rápida (<500ms).
"""

import hashlib
import hmac
import json
import logging
import os
import subprocess
import sys
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [github-webhook] %(levelname)s: %(message)s")
logger = logging.getLogger("github-webhook")

DEDUPE_FILE = Path(r"C:\Users\PICHAU\Hangar_v1\runtime\.webhook_dedupe.json")
CIRCUITO_CONVERSA = Path(r"C:\Users\PICHAU\Downloads\circuito\conversa de ia.txt")
NOTIFY_CODEX_SCRIPT = Path(r"C:\Users\PICHAU\Downloads\circuito\runtime\notify_codex.py")

DEFAULT_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "hangar_v1_webhook_secret_soberano")

def load_dedupe_set() -> set:
    if DEDUPE_FILE.exists():
        try:
            data = json.loads(DEDUPE_FILE.read_text("utf-8"))
            return set(data.get("seen_ids", []))
        except Exception:
            pass
    return set()

def save_dedupe_id(entry_id: str):
    seen = load_dedupe_set()
    seen.add(entry_id)
    DEDUPE_FILE.parent.mkdir(parents=True, exist_ok=True)
    DEDUPE_FILE.write_text(json.dumps({"seen_ids": list(seen)[-500:]}, indent=2), "utf-8")

def verify_signature(payload_bytes: bytes, signature_header: Optional[str], secret: str) -> bool:
    """Verifica assinatura HMAC SHA-256 (X-Hub-Signature-256)."""
    if not signature_header or not signature_header.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header)

def trigger_antigravity_wake(comment_body: str, comment_id: int, delivery_id: str):
    """Aciona a esteira local para processar a nova CALL recebida."""
    logger.info(f"Disparando auto-wake para CALL id={comment_id} (delivery={delivery_id})")
    
    # 1. Registrar em conversa de ia.txt se ainda não estiver presente
    try:
        CIRCUITO_CONVERSA.parent.mkdir(parents=True, exist_ok=True)
        current = CIRCUITO_CONVERSA.read_text("utf-8") if CIRCUITO_CONVERSA.exists() else ""
        if str(comment_id) not in current:
            with open(CIRCUITO_CONVERSA, "a", encoding="utf-8") as f:
                f.write("\n\n" + comment_body.strip() + "\n")
    except Exception as exc:
        logger.error(f"Erro ao persistir CALL no circuito: {exc}")

    # 2. Notificar Codex
    if NOTIFY_CODEX_SCRIPT.exists():
        try:
            subprocess.Popen([sys.executable, str(NOTIFY_CODEX_SCRIPT), "v"], cwd=str(CIRCUITO_CONVERSA.parent))
        except Exception as exc:
            logger.error(f"Erro ao invocar notify_codex: {exc}")

class WebhookHandler(BaseHTTPRequestHandler):
    webhook_secret = DEFAULT_SECRET

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "service": "github-webhook-receiver",
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

        # 1. Validação Fail-Closed de Assinatura HMAC SHA-256
        if not verify_signature(payload_bytes, sig_header, self.webhook_secret):
            logger.warning(f"Rejeitada requisicao sem assinatura valida HMAC SHA-256 (delivery={delivery_id})")
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Invalid HMAC signature"}).encode("utf-8"))
            return

        # 2. Aceitar ping event com 200
        if event_type == "ping":
            logger.info("GitHub Ping Event recebido e autenticado com sucesso.")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"msg": "pong"}).encode("utf-8"))
            return

        # 3. Filtrar somente eventos issue_comment da PR #1
        if event_type != "issue_comment":
            logger.info(f"Evento {event_type} ignorado (apenas issue_comment e processado).")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"msg": f"Ignored event: {event_type}"}).encode("utf-8"))
            return

        try:
            data = json.loads(payload_bytes.decode("utf-8"))
        except Exception as exc:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Invalid JSON: {exc}"}).encode("utf-8"))
            return

        action = data.get("action")
        issue_number = data.get("issue", {}).get("number")
        comment = data.get("comment", {})
        comment_id = comment.get("id")
        comment_body = comment.get("body", "")

        # Apenas comentários criados na PR #1
        if action != "created" or issue_number != 1:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"msg": "Ignored (not PR #1 comment created)"}).encode("utf-8"))
            return

        # Filtrar TYPE: CALL
        if "TYPE: CALL" not in comment_body and "CG-" not in comment_body:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"msg": "Ignored (no CALL payload in body)"}).encode("utf-8"))
            return

        # 4. Deduplicação estrita por delivery_id + comment_id
        dedupe_key = f"{delivery_id}_{comment_id}"
        seen = load_dedupe_set()
        if dedupe_key in seen:
            logger.info(f"Deduplicado: evento {dedupe_key} ja foi processado previamente.")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"msg": "Duplicate event ignored", "dedupe_key": dedupe_key}).encode("utf-8"))
            return

        # Registrar no dedupe
        save_dedupe_id(dedupe_key)

        # 5. Ingestão e Selagem Criptográfica Soberana AZ000
        az000_info = {}
        try:
            from az000_governance.owner_intent.ingestor import ingest_and_seal_call
            seal_res = ingest_and_seal_call(comment_body)
            az000_info = {
                "status": seal_res.get("status"),
                "stage": seal_res.get("stage"),
                "verdict": seal_res.get("validation", {}).get("verdict"),
                "contract_id": seal_res.get("sealed_contract", {}).get("contract_id") if seal_res.get("sealed_contract") else None,
                "contract_file": seal_res.get("contract_file")
            }
            logger.info(f"[AZ000] Ingestão e selagem concluídas: status={az000_info['status']} contract_id={az000_info['contract_id']}")
        except Exception as exc:
            logger.error(f"[AZ000] Erro na ingestão e selagem AZ000: {exc}")
            az000_info = {"status": "ERROR", "error": str(exc)}

        # 6. Resposta HTTP rápida antes/durante o disparo
        self.send_response(202)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "accepted",
            "comment_id": comment_id,
            "delivery_id": delivery_id,
            "dispatched": True,
            "az000_seal": az000_info
        }).encode("utf-8"))

        # 7. Disparo assíncrono do Antigravity
        trigger_antigravity_wake(comment_body, comment_id, delivery_id)

def create_server(host="127.0.0.1", port=8766, secret=None):
    WebhookHandler.webhook_secret = secret or DEFAULT_SECRET
    return ThreadingHTTPServer((host, port), WebhookHandler)

if __name__ == "__main__":
    port = 8766
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    server = create_server("127.0.0.1", port)
    logger.info(f"GitHub Webhook Server rodando em http://127.0.0.1:{port}/github-webhook")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Servidor encerrado.")
