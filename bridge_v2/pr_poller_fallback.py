#!/usr/bin/env python3
"""
bridge_v2/pr_poller_fallback.py — Polling Fallback e Publicador de RESULT (V2).
Porta P-EXT-BRIDGE-V2-01 / Hangar_v1/EXTERNAL/BRIDGE_V2

Funções:
1. Fallback estrito de recuperação (polling compartilhado com dedupe global do webhook).
2. Publicador de RESULT no GitHub PR #1.
3. Montagem e armamento automático de CONTEXT_PACKET para a extensão do ChatGPT.
4. Notificação ao Proprietário via Telegram.
"""

import argparse
import datetime
import json
import logging
import os
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bridge.github_pr_relay import get_github_token
from bridge_v2.daily_journal import DailyCircuitJournal
from bridge_v2.owner_telemetry import OwnerTelemetryManager
from bridge_v2.schema import (
    format_context_packet,
    format_result_envelope,
    normalize_call_envelope,
)
from bridge_v2.state_manager import CleanroomStateManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [fallback-poller-v2] %(levelname)s: %(message)s")
logger = logging.getLogger("fallback-poller-v2")


class GitHubPRPollerV2:
    def __init__(self, repo: str = "BNeto04/Hangar_v1", pr_number: int = 1):
        self.repo = repo
        self.pr_number = pr_number
        self.state_mgr = CleanroomStateManager()
        self.journal = DailyCircuitJournal()
        self.telemetry = OwnerTelemetryManager()
        self.token = get_github_token()

    def fetch_comments(self) -> List[Dict[str, Any]]:
        if not self.token:
            self.token = get_github_token()
        if not self.token:
            logger.error("Token do GitHub indisponível para fetch.")
            return []

        all_comments = []
        page = 1
        while True:
            url = f"https://api.github.com/repos/{self.repo}/issues/{self.pr_number}/comments?per_page=100&page={page}"
            headers = {
                "Authorization": f"token {self.token}",
                "User-Agent": "Hangar-V2-Poller/2.0",
                "Accept": "application/vnd.github.v3+json",
            }
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if not data or not isinstance(data, list):
                        break
                    all_comments.extend(data)
                    if len(data) < 100:
                        break
                    page += 1
            except Exception as e:
                logger.error(f"Erro ao buscar comentários do PR #{self.pr_number}: {e}")
                break
        return all_comments

    def poll_cycle(self) -> int:
        """Executa um ciclo de polling estrito de recuperação."""
        comments = self.fetch_comments()
        delivered_count = 0

        for c in comments:
            cid = c.get("id")
            raw_body = c.get("body", "")

            envelope = normalize_call_envelope(raw_body, comment_id=cid)
            if not envelope:
                continue

            mid = envelope["message_id"]
            call_id = envelope["call_id"]

            if self.state_mgr.is_duplicate(comment_id=cid, message_id=mid, call_id=call_id):
                continue

            # Nova CALL recuperada pelo fallback!
            logger.warning(f"FALLBACK_POLLING: Recuperando CALL {mid} não processada pelo Webhook!")
            self.state_mgr.deliver_to_inbox(envelope["body"], message_id=mid, call_id=call_id)
            self.state_mgr.mark_processed(comment_id=cid, message_id=mid, call_id=call_id)

            self.journal.record_event(
                event_type="CALL_RECEIVED",
                actor_from="CHATGPT",
                actor_to="ANTIGRAVITY",
                channel="GITHUB_PR1",
                summary=f"CALL recuperada via Polling Fallback: {mid} ({call_id})",
                message_id=mid,
                call_id=call_id,
                reply_to=envelope.get("reply_to"),
                github_comment_id=cid,
                status="DELIVERED_VIA_FALLBACK",
            )
            delivered_count += 1
            break

        return delivered_count

    def post_result(
        self,
        message_id: str,
        reply_to: str,
        status: str,
        body: str,
        sprint_id: str = "SPRINT-BRIDGE-V2-CLEANROOM-001",
        call_id: Optional[str] = None,
        summary_short: Optional[str] = None,
    ) -> Optional[int]:
        """Publica RESULT no GitHub PR #1 e arma o CONTEXT_PACKET para o ChatGPT."""
        if not self.token:
            self.token = get_github_token()

        envelope_text = format_result_envelope(
            message_id=message_id,
            reply_to=reply_to,
            status=status,
            body=body,
            sprint_id=sprint_id,
            call_id=call_id,
        )

        url = f"https://api.github.com/repos/{self.repo}/issues/{self.pr_number}/comments"
        headers = {
            "Authorization": f"token {self.token}",
            "User-Agent": "Hangar-V2-Poller/2.0",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }
        payload = json.dumps({"body": envelope_text}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                comment_id = data.get("id")
                logger.info(f"RESULT postado no PR #{self.pr_number}! ID={comment_id}")

                # 1. Gravar outbox
                short_sum = summary_short or body[:200]
                self.state_mgr.deliver_to_outbox(envelope_text, status=status, summary=short_sum)

                # 2. Registrar no diário diário
                self.journal.record_event(
                    event_type="RESULT_PUBLISHED",
                    actor_from="ANTIGRAVITY",
                    actor_to="CHATGPT",
                    channel="GITHUB_PR1",
                    summary=f"RESULT publicado: {message_id} ({status})",
                    message_id=message_id,
                    call_id=call_id,
                    reply_to=reply_to,
                    github_comment_id=comment_id,
                    status=status,
                )

                # 3. Construir CONTEXT_PACKET e armar na extensão do ChatGPT
                sprint_data = self.state_mgr.sprint_state
                context_packet = format_context_packet(
                    sprint_id=sprint_id,
                    owner_objective=sprint_data.get("owner_objective", ""),
                    done_criteria=sprint_data.get("done_criteria", ""),
                    out_of_scope=sprint_data.get("out_of_scope", ""),
                    last_call_id=call_id or "NONE",
                    last_message_id=reply_to or "NONE",
                    github_comment_id=comment_id,
                    result_status=status,
                    result_summary=short_sum,
                    current_state="RESULT_DELIVERED_AWAITING_NEXT_STEP",
                )

                self._arm_inbound_relay(message_id, call_id, context_packet)

                # 4. Notificar Proprietário via Telegram
                self.telemetry.notify(
                    event_type="TASK_COMPLETED",
                    summary=f"Resultado entregue: `{message_id}` ({status})\n\n_{short_sum[:180]}..._",
                    sprint_id=sprint_id,
                    task_id=call_id,
                )

                return comment_id
        except Exception as exc:
            logger.error(f"Falha ao postar RESULT: {exc}")
            return None

    def _arm_inbound_relay(self, message_id: str, call_id: Optional[str], context_packet: str):
        try:
            payload = json.dumps({
                "message_id": message_id,
                "call_id": call_id,
                "context_packet": context_packet
            }).encode("utf-8")
            req = urllib.request.Request(
                "http://127.0.0.1:8765/arm_wake",
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                logger.info(f"Relay inbound armado com CONTEXT_PACKET para {message_id}")
        except Exception as e:
            logger.warning(f"Inbound relay offline ou não respondeu: {e}")


def main():
    parser = argparse.ArgumentParser(description="PR Poller Fallback V2")
    parser.add_argument("--poll-loop", action="store_true", help="Executa loop de polling fallback contínuo")
    parser.add_argument("--poll-interval", type=int, default=10, help="Intervalo de polling em segundos")
    args = parser.parse_args()

    poller = GitHubPRPollerV2()
    if args.poll_loop:
        logger.info(f"Iniciando Poller Fallback V2 (intervalo={args.poll_interval}s)...")
        while True:
            try:
                poller.poll_cycle()
            except Exception as e:
                logger.error(f"Erro no ciclo de fallback: {e}")
            time.sleep(args.poll_interval)
    else:
        delivered = poller.poll_cycle()
        print(f"POLL_CYCLE_DONE: Delivered {delivered}")


if __name__ == "__main__":
    main()
