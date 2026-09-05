#!/usr/bin/env python3
"""
github_webhook_daemon.py — Daemon orquestrador do Webhook do GitHub para o Hangar V1.
Inicia o servidor local, estabelece o túnel seguro, registra o webhook na API do GitHub
e gerencia o ciclo de vida completo com rollback automático ao encerrar.
"""

import atexit
import logging
import signal
import sys
import threading
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import bridge.github_webhook_server as gws
import bridge.tunnel_manager as tm

logging.basicConfig(level=logging.INFO, format="%(asctime)s [webhook-daemon] %(levelname)s: %(message)s")
logger = logging.getLogger("webhook-daemon")

LOCAL_PORT = 8766
SHARED_SECRET = "hangar_v1_webhook_secret_soberano"

server = None
tunnel_mgr = None

def cleanup():
    global tunnel_mgr, server
    logger.info("Executando teardown seguro do daemon...")
    if tunnel_mgr:
        try:
            tunnel_mgr.teardown()
        except Exception as exc:
            logger.error(f"Erro no teardown do tunnel: {exc}")
    if server:
        try:
            server.shutdown()
            server.server_close()
        except Exception as exc:
            logger.error(f"Erro ao fechar servidor: {exc}")
    logger.info("Daemon encerrado de forma limpa e reversivel.")

def signal_handler(signum, frame):
    logger.info(f"Sinal recebido ({signum}). Encerrando...")
    cleanup()
    sys.exit(0)

def main():
    global server, tunnel_mgr

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup)

    # 1. Iniciar servidor local na porta 8766
    logger.info(f"Iniciando GitHub Webhook Server local na porta {LOCAL_PORT}...")
    server = gws.create_server("127.0.0.1", LOCAL_PORT, secret=SHARED_SECRET)
    srv_thread = threading.Thread(target=server.serve_forever, daemon=True)
    srv_thread.start()
    time.sleep(0.5)

    # 2. Iniciar túnel seguro Cloudflare
    logger.info("Estabelecendo tunel seguro Cloudflare...")
    tunnel_mgr = tm.TunnelManager(local_port=LOCAL_PORT, secret=SHARED_SECRET)
    public_url = tunnel_mgr.start_tunnel(timeout=35)
    logger.info(f"Tunel ativo: {public_url}")

    # 3. Registrar Webhook no GitHub
    logger.info("Registrando webhook no repositorio BNeto04/Hangar_v1...")
    hook_id = tunnel_mgr.register_github_webhook()
    logger.info(f"Webhook registrado com sucesso! ID={hook_id}")

    logger.info("=" * 60)
    logger.info("GITHUB WEBHOOK DAEMON PRONTO E AGUARDANDO EVENTOS DA PR #1")
    logger.info(f"Endpoint: {public_url}/github-webhook")
    logger.info(f"Webhook ID no GitHub: {hook_id}")
    logger.info("=" * 60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
