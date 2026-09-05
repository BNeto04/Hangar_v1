#!/usr/bin/env python3
"""
bridge_v2/owner_telemetry.py — Telemetria Humana e Registro de Intervenções (V2).
Porta P-EXT-BRIDGE-V2-01 / CG-000148 / CG-000149

Garante que o Proprietário (Manoel) seja informado das tarefas da Sprint
via Telegram e que qualquer intervenção seja registrada no diário diário.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bridge_v2.daily_journal import DailyCircuitJournal
from bridge_v2.schema import format_owner_event

logger = logging.getLogger("owner-telemetry-v2")


class OwnerTelemetryManager:
    """Gerencia notificações humanas e recepção de intervenções."""

    def __init__(self):
        self.journal = DailyCircuitJournal()

    def notify(
        self,
        event_type: str,
        summary: str,
        sprint_id: str = "SPRINT-BRIDGE-V2-CLEANROOM-001",
        task_id: Optional[str] = None,
        channel: str = "TELEGRAM",
        send_telegram: bool = True,
    ):
        """
        Notifica evento material ao Proprietário e registra no diário diário.
        Tipos permitidos: TASK_STARTED, TASK_COMPLETED, TASK_BLOCKED, OWNER_DECISION_REQUIRED, SPRINT_STATE_CHANGED.
        """
        # 1. Registrar no Diário do Dia
        self.journal.record_event(
            event_type=event_type,
            actor_from="ANTIGRAVITY",
            actor_to="OWNER",
            channel=channel,
            summary=summary,
            sprint_id=sprint_id,
            task_id=task_id,
            human_intervention=False,
            status="NOTIFIED",
        )

        # 2. Enviar via Telegram se solicitado
        if send_telegram:
            try:
                from bridge.sentinela_telegram import send_telegram_alert
                icon_map = {
                    "TASK_STARTED": "🚀",
                    "TASK_COMPLETED": "✅",
                    "TASK_BLOCKED": "⚠️",
                    "OWNER_DECISION_REQUIRED": "🛑",
                    "SPRINT_STATE_CHANGED": "🔄",
                }
                icon = icon_map.get(event_type, "ℹ️")
                msg = f"{icon} *[{sprint_id}] {event_type}*\n\n{summary}"
                if task_id:
                    msg += f"\n• *Task:* `{task_id}`"
                send_telegram_alert(msg)
                logger.info(f"Notificação Telegram enviada: {event_type} ({task_id})")
            except Exception as e:
                logger.warning(f"Falha ao enviar alerta Telegram: {e}")

    def register_intervention(
        self,
        actor: str,
        channel: str,
        directive_text: str,
        sprint_id: str = "SPRINT-BRIDGE-V2-CLEANROOM-001",
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Registra uma intervenção humana soberana (via Telegram, Antigravity ou ChatGPT).
        """
        event = self.journal.record_event(
            event_type="OWNER_DIRECTIVE",
            actor_from=actor,
            actor_to="ANTIGRAVITY",
            channel=channel,
            summary=directive_text,
            sprint_id=sprint_id,
            task_id=task_id,
            human_intervention=True,
            status="RECEIVED",
        )
        logger.info(f"Intervenção do Proprietário registrada via {channel}: {directive_text[:100]}")
        return event
