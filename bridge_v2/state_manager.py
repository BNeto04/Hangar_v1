#!/usr/bin/env python3
"""
bridge_v2/state_manager.py — Gerenciador de Estado e Deduplicação Atômica da Ponte V2.
Porta P-EXT-BRIDGE-V2-01 / Hangar_v1/EXTERNAL/BRIDGE_V2

Isolamento absoluto Clean-Room:
- runtime/bridge_v2/inbox/current_call.txt
- runtime/bridge_v2/outbox/current_result.txt
- runtime/bridge_v2/state/dedupe_state.json
- runtime/bridge_v2/state/current_sprint.json
- runtime/bridge_v2/state/wake_state.json
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger("state-manager-v2")

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = REPO_ROOT / "runtime" / "bridge_v2"
INBOX_DIR = RUNTIME_DIR / "inbox"
OUTBOX_DIR = RUNTIME_DIR / "outbox"
STATE_DIR = RUNTIME_DIR / "state"

CURRENT_CALL_FILE = INBOX_DIR / "current_call.txt"
CURRENT_RESULT_FILE = OUTBOX_DIR / "current_result.txt"
DEDUPE_STATE_FILE = STATE_DIR / "dedupe_state.json"
CURRENT_SPRINT_FILE = STATE_DIR / "current_sprint.json"
WAKE_STATE_FILE = STATE_DIR / "wake_state.json"


def ensure_state_dirs():
    for d in [INBOX_DIR, OUTBOX_DIR, STATE_DIR]:
        d.mkdir(parents=True, exist_ok=True)


class CleanroomStateManager:
    """Gerencia estado de execução, deduplicação e contexto da Sprint."""

    def __init__(self, runtime_dir: Optional[Path] = None):
        self.runtime_dir = runtime_dir or RUNTIME_DIR
        self.inbox_dir = self.runtime_dir / "inbox"
        self.outbox_dir = self.runtime_dir / "outbox"
        self.state_dir = self.runtime_dir / "state"

        for d in [self.inbox_dir, self.outbox_dir, self.state_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.current_call_file = self.inbox_dir / "current_call.txt"
        self.current_result_file = self.outbox_dir / "current_result.txt"
        self.dedupe_state_file = self.state_dir / "dedupe_state.json"
        self.current_sprint_file = self.state_dir / "current_sprint.json"
        self.wake_state_file = self.state_dir / "wake_state.json"

        self.dedupe_state = self._load_dedupe_state()
        self.sprint_state = self._load_sprint_state()

    def _load_dedupe_state(self) -> Dict[str, Any]:
        if self.dedupe_state_file.exists():
            try:
                return json.loads(self.dedupe_state_file.read_text("utf-8"))
            except Exception:
                pass
        return {"processed_comments": [], "processed_deliveries": [], "processed_messages": [], "processed_keys": []}

    def _save_dedupe_state(self):
        tmp = self.dedupe_state_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.dedupe_state, indent=2), "utf-8")
        tmp.replace(self.dedupe_state_file)

    def _load_sprint_state(self) -> Dict[str, Any]:
        if self.current_sprint_file.exists():
            try:
                return json.loads(self.current_sprint_file.read_text("utf-8"))
            except Exception:
                pass
        return {
            "sprint_id": "SPRINT-BRIDGE-V2-CLEANROOM-001",
            "owner_objective": "Construir uma NOVA ponte Hangar V1 em clean-room sem poluição de legado anterior.",
            "done_criteria": "Nova ponte isolada, webhook primário, fallback sem duplicar, auto-rearm, extensão com CONTEXT_PACKET, telemetria multi-canal, diário do circuito ativo.",
            "out_of_scope": "Obsidian/Canvas/cartografia, migração de histórico legado, homologação soberana final.",
            "current_status": "BUILDING",
            "last_call_id": None,
            "last_message_id": None,
            "last_comment_id": None,
            "latest_result_status": "INITIALIZED",
            "latest_result_summary": "Sprint iniciada em clean-room.",
        }

    def save_sprint_state(self, updates: Dict[str, Any]):
        self.sprint_state.update(updates)
        tmp = self.current_sprint_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.sprint_state, indent=2, ensure_ascii=False), "utf-8")
        tmp.replace(self.current_sprint_file)

    def is_duplicate(
        self,
        comment_id: Optional[int] = None,
        delivery_id: Optional[str] = None,
        message_id: Optional[str] = None,
        call_id: Optional[str] = None,
    ) -> bool:
        """Verifica se a mensagem já foi consumida."""
        if comment_id and comment_id in self.dedupe_state["processed_comments"]:
            return True
        if delivery_id and delivery_id in self.dedupe_state["processed_deliveries"]:
            return True
        if message_id and message_id in self.dedupe_state["processed_messages"]:
            return True

        key = f"{comment_id or 'none'}_{delivery_id or 'none'}_{message_id or 'none'}_{call_id or 'none'}"
        if key in self.dedupe_state["processed_keys"]:
            return True

        return False

    def mark_processed(
        self,
        comment_id: Optional[int] = None,
        delivery_id: Optional[str] = None,
        message_id: Optional[str] = None,
        call_id: Optional[str] = None,
    ):
        """Marca o item como processado e persiste."""
        if comment_id and comment_id not in self.dedupe_state["processed_comments"]:
            self.dedupe_state["processed_comments"].append(comment_id)
        if delivery_id and delivery_id not in self.dedupe_state["processed_deliveries"]:
            self.dedupe_state["processed_deliveries"].append(delivery_id)
        if message_id and message_id not in self.dedupe_state["processed_messages"]:
            self.dedupe_state["processed_messages"].append(message_id)

        key = f"{comment_id or 'none'}_{delivery_id or 'none'}_{message_id or 'none'}_{call_id or 'none'}"
        if key not in self.dedupe_state["processed_keys"]:
            self.dedupe_state["processed_keys"].append(key)

        # Truncar para manter últimos 500 registros
        self.dedupe_state["processed_comments"] = self.dedupe_state["processed_comments"][-500:]
        self.dedupe_state["processed_deliveries"] = self.dedupe_state["processed_deliveries"][-500:]
        self.dedupe_state["processed_messages"] = self.dedupe_state["processed_messages"][-500:]
        self.dedupe_state["processed_keys"] = self.dedupe_state["processed_keys"][-500:]

        self._save_dedupe_state()

    def deliver_to_inbox(self, body_text: str, message_id: str, call_id: Optional[str] = None) -> Path:
        """Entrega o corpo da CALL no inbox corrente da ponte V2."""
        tmp = self.current_call_file.with_suffix(".tmp")
        tmp.write_text(body_text, encoding="utf-8")
        tmp.replace(self.current_call_file)

        self.save_sprint_state({
            "last_message_id": message_id,
            "last_call_id": call_id,
            "current_status": "IN_PROGRESS",
        })
        logger.info(f"CALL entregue com sucesso em {self.current_call_file} ({message_id})")
        return self.current_call_file

    def deliver_to_outbox(self, result_text: str, status: str, summary: str) -> Path:
        """Grava o RESULT no outbox corrente."""
        tmp = self.current_result_file.with_suffix(".tmp")
        tmp.write_text(result_text, encoding="utf-8")
        tmp.replace(self.current_result_file)

        self.save_sprint_state({
            "latest_result_status": status,
            "latest_result_summary": summary,
            "current_status": "RESULT_READY",
        })
        logger.info(f"RESULT gravado com sucesso em {self.current_result_file} ({status})")
        return self.current_result_file
