#!/usr/bin/env python3
"""
bridge_v2/autowake_agent.py — Receptor Exit-on-Detect para Despertar do Antigravity (V2).
Porta P-EXT-BRIDGE-V2-01 / Hangar_v1/EXTERNAL/BRIDGE_V2

Estratégia: EXIT-ON-DETECT.
Monitora runtime/bridge_v2/inbox/current_call.txt.
Quando uma nova CALL é entregue pelo Webhook ou Polling:
1. Detecta alteração de SHA-256 do arquivo de inbox.
2. Emite evidências estruturadas no stdout.
3. Termina com código 0.
4. O runtime do Antigravity detecta o encerramento da tarefa em segundo plano
   e inicia um novo turno de inferência para o modelo processar a CALL.
"""

import argparse
import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bridge_v2.daily_journal import DailyCircuitJournal
from bridge_v2.state_manager import CURRENT_CALL_FILE, RUNTIME_DIR

LOG = logging.getLogger("autowake-v2")


def compute_signature(filepath: Path) -> Optional[dict]:
    if not filepath.exists():
        return None
    try:
        data = filepath.read_bytes()
    except OSError:
        return None
    if not data.strip():
        return None
    sha = hashlib.sha256(data).hexdigest()
    text = data.decode("utf-8", errors="replace")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    header = lines[0] if lines else ""
    return {"sha": sha, "header": header, "size": len(data)}


def main():
    parser = argparse.ArgumentParser(description="Autowake Agent V2")
    parser.add_argument("--watch-file", default=str(CURRENT_CALL_FILE), help="Arquivo de inbox a monitorar")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Intervalo de polling em segundos")
    parser.add_argument("--timeout", type=float, default=0, help="Timeout em segundos (0 = infinito)")
    args = parser.parse_args()

    watch_path = Path(args.watch_file)
    watch_path.parent.mkdir(parents=True, exist_ok=True)

    state_file = RUNTIME_DIR / "state" / "autowake_seen_sha.json"
    state_file.parent.mkdir(parents=True, exist_ok=True)

    seen_sha = None
    if state_file.exists():
        try:
            seen_sha = json.loads(state_file.read_text("utf-8")).get("last_sha")
        except Exception:
            pass

    # Inicializar com estado atual se ainda não visto
    current_sig = compute_signature(watch_path)
    if current_sig and seen_sha is None:
        seen_sha = current_sig["sha"]
        state_file.write_text(json.dumps({"last_sha": seen_sha, "bootstrapped": True}, indent=2), "utf-8")

    print(f"AUTOWAKE_V2_ONLINE: Watching {watch_path} (interval={args.poll_interval}s)", flush=True)

    start_time = time.time()
    journal = DailyCircuitJournal()

    while True:
        if args.timeout > 0 and (time.time() - start_time) > args.timeout:
            print("AUTOWAKE_TIMEOUT", flush=True)
            sys.exit(2)

        sig = compute_signature(watch_path)
        if sig and sig["sha"] != seen_sha:
            # Nova CALL detectada!
            state_file.write_text(json.dumps({"last_sha": sig["sha"], "detected_at": time.time()}, indent=2), "utf-8")

            print("WAKE_CALL_DETECTED", flush=True)
            print(f"CALL_HEADER={sig['header']}", flush=True)
            print(f"CALL_SHA256={sig['sha']}", flush=True)
            print(f"CALL_SIZE={sig['size']}", flush=True)

            journal.record_event(
                event_type="ANTIGRAVITY_WAKE_TRIGGERED",
                actor_from="AUTOWAKE_V2",
                actor_to="ANTIGRAVITY",
                channel="BRIDGE_V2",
                summary=f"Despertar do Antigravity disparado por nova CALL: {sig['header'][:80]}",
                status="TRIGGERED",
            )
            # Termina para acordar o Antigravity
            sys.exit(0)

        time.sleep(args.poll_interval)


if __name__ == "__main__":
    main()
