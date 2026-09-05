#!/usr/bin/env python3
"""
gpt_watchdog.py — Sentinela Ativa de Ciclo Contínuo (Watchdog do ChatGPT).
Monitora o fluxo de respostas na PR #1 e na ponte de sinalização local.
Se o ChatGPT ficar ocioso por mais de 75s após um envio do Antigravity,
provoca o despertar automaticamente armando o pulso 'v'.
"""

import json
import logging
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bridge.sentinela_telegram import send_telegram_alert

logging.basicConfig(level=logging.INFO, format="%(asctime)s [watchdog-gpt] %(levelname)s: %(message)s")
logger = logging.getLogger("watchdog-gpt")

RELAY_URL = "http://127.0.0.1:8765"
PR_API_URL = "https://api.github.com/repos/BNeto04/Hangar_v1/issues/1/comments?per_page=5&page=100"
IDLE_THRESHOLD_SECONDS = 75
PROBE_COOLDOWN_SECONDS = 60

def get_latest_pr_comment_author() -> str:
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/BNeto04/Hangar_v1/issues/1",
            headers={"User-Agent": "Watchdog-Bot"}
        )
        issue = json.loads(urllib.request.urlopen(req, timeout=10).read())
        total = issue["comments"]
        page = (total // 30) + 1
        req2 = urllib.request.Request(
            f"https://api.github.com/repos/BNeto04/Hangar_v1/issues/1/comments?page={page}&per_page=30",
            headers={"User-Agent": "Watchdog-Bot"}
        )
        comments = json.loads(urllib.request.urlopen(req2, timeout=10).read())
        if comments:
            last = comments[-1]
            body = last.get("body", "")
            if "FROM: ANTIGRAVITY" in body or "MESSAGE_ID: AG-" in body:
                return "ANTIGRAVITY"
            elif "CG-" in body or "TYPE: CALL" in body:
                return "CHATGPT"
    except Exception as exc:
        logger.warning(f"Erro ao verificar ultimo autor na PR #1: {exc}")
    return "UNKNOWN"

def check_relay_status() -> dict:
    try:
        req = urllib.request.Request(f"{RELAY_URL}/status")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return {}

def arm_wake(probe_id: str):
    try:
        data = json.dumps({"message_id": probe_id, "call_id": "WATCHDOG_KEEP_ALIVE", "text": "v"}).encode("utf-8")
        req = urllib.request.Request(f"{RELAY_URL}/arm_wake", data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            logger.info(f"Pulso 'v' armado com sucesso pelo Watchdog (probe={probe_id})")
            return True
    except Exception as exc:
        logger.error(f"Erro ao armar wake via Watchdog: {exc}")
        return False

def run_watchdog_loop(poll_interval: int = 15):
    logger.info("Watchdog do ChatGPT iniciado. Mantendo ciclo de trabalho perene...")
    last_probe_time = 0
    waiting_since = None

    while True:
        try:
            status = check_relay_status()
            last_author = get_latest_pr_comment_author()
            now = time.time()

            if last_author == "ANTIGRAVITY":
                if waiting_since is None:
                    waiting_since = now
                idle_duration = now - waiting_since

                if idle_duration > IDLE_THRESHOLD_SECONDS and (now - last_probe_time) > PROBE_COOLDOWN_SECONDS:
                    if not status.get("pending_wake"):
                        probe_id = f"PROBE-WATCHDOG-{int(now)}"
                        logger.warning(f"ChatGPT ocioso ha {int(idle_duration)}s apos entrega do Antigravity. Provocando com 'v'...")
                        if arm_wake(probe_id):
                            last_probe_time = now
                            try:
                                send_telegram_alert(f"⚡ *Watchdog Ativo:* ChatGPT ocioso há {int(idle_duration)}s. Pulso 'v' re-armado automaticamente para manter o ciclo de trabalho contínuo!")
                            except Exception:
                                pass
            else:
                waiting_since = None

        except Exception as exc:
            logger.error(f"Excecao no loop do Watchdog: {exc}")

        time.sleep(poll_interval)

if __name__ == "__main__":
    run_watchdog_loop()
