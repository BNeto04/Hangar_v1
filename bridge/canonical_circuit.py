#!/usr/bin/env python3
"""
bridge/canonical_circuit.py — Gerenciador Canônico do Circuito de Comunicação e Persistência.
Porta P-EXT-BRIDGE-01 / Hangar_v1/EXTERNAL/BRIDGE

Responsabilidades:
1. Normalização unificada de envelopes (Full format YAML-like e Compact format CG-xxxxx).
2. Journal append-only por data (YYYY-MM-DD.jsonl) com SHA-256, metadados e provenance.
3. Deduplicação global atômica compartilhada entre Webhook (primário) e Polling (fallback).
4. Gerenciamento canônico de caminhos em runtime/bridge/ (inbox, outbox, journal, state, logs).
5. Compatibilidade retroativa durante cutover com Downloads/circuito.
"""

import datetime
import hashlib
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("canonical-circuit")

# Caminhos Canônicos no Hangar V1
REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_BRIDGE = REPO_ROOT / "runtime" / "bridge"
INBOX_DIR = RUNTIME_BRIDGE / "inbox"
OUTBOX_DIR = RUNTIME_BRIDGE / "outbox"
JOURNAL_DIR = RUNTIME_BRIDGE / "journal"
STATE_DIR = RUNTIME_BRIDGE / "state"
LOGS_DIR = RUNTIME_BRIDGE / "logs"

CURRENT_CALL_FILE = INBOX_DIR / "current_call.txt"
CURRENT_RESULT_FILE = OUTBOX_DIR / "current_result.txt"
JOURNAL_INDEX_FILE = JOURNAL_DIR / "INDEX.json"
STATE_FILE = STATE_DIR / "github_bridge_state.json"
WEBHOOK_DEDUPE_FILE = STATE_DIR / "webhook_dedupe.json"
REJECTIONS_LOG = JOURNAL_DIR / "rejections.jsonl"

# Caminho Legado (circuito antigo)
LEGACY_CIRCUITO_DIR = Path(r"C:\Users\PICHAU\Downloads\circuito")
LEGACY_CONVERSA_FILE = LEGACY_CIRCUITO_DIR / "conversa de ia.txt"
LEGACY_RESPOSTA_FILE = LEGACY_CIRCUITO_DIR / "resposta do executor.txt"


def ensure_directories():
    """Garante existência de todos os diretórios do runtime/bridge."""
    for d in [INBOX_DIR, OUTBOX_DIR, JOURNAL_DIR, STATE_DIR, LOGS_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_envelope(raw_text: str, comment_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Normaliza envelopes de mensagens recebidas do GitHub PR #1.
    Aceita dois formatos canônicos:
      1. Envelope Completo (MESSAGE_ID:, FROM:, TO:, TYPE:, REPLY_TO:, BODY:)
      2. Envelope Compacto do ChatGPT (Linha 1 com 'CG-xxxxx', 'TYPE: CALL', 'TO: ANTIGRAVITY')
    Retorna dicionário normalizado ou None se for inválido/malformado.
    Em caso de rejeição, grava no journal de rejeições para auditoria.
    """
    if not raw_text or not raw_text.strip():
        return None

    raw_clean = raw_text.strip()
    lines = [ln.strip() for ln in raw_clean.splitlines()]

    data: Dict[str, Any] = {
        "MESSAGE_ID": None,
        "TIMESTAMP": None,
        "FROM": None,
        "TO": None,
        "TYPE": None,
        "REPLY_TO": None,
        "CALL_ID": None,
        "BODY": "",
        "BODY_SHA256": None,
        "raw_format": None,
        "schema_version": "CANONICAL_ENVELOPE_V1",
    }

    # FORMATO 1: Envelope Completo YAML-like
    if "MESSAGE_ID:" in raw_clean:
        body_lines = []
        in_body = False
        header_keys = ("MESSAGE_ID:", "TIMESTAMP:", "FROM:", "TO:", "TYPE:", "REPLY_TO:")

        for line in lines:
            if in_body:
                if line.startswith("BODY_SHA256:"):
                    in_body = False
                    data["BODY_SHA256"] = line.split(":", 1)[1].strip()
                else:
                    body_lines.append(line)
            elif line.startswith("MESSAGE_ID:"):
                data["MESSAGE_ID"] = line.split(":", 1)[1].strip()
            elif line.startswith("TIMESTAMP:"):
                data["TIMESTAMP"] = line.split(":", 1)[1].strip()
            elif line.startswith("FROM:"):
                data["FROM"] = line.split(":", 1)[1].strip()
            elif line.startswith("TO:"):
                data["TO"] = line.split(":", 1)[1].strip()
            elif line.startswith("TYPE:"):
                data["TYPE"] = line.split(":", 1)[1].strip()
            elif line.startswith("REPLY_TO:"):
                data["REPLY_TO"] = line.split(":", 1)[1].strip()
            elif line.startswith("BODY:"):
                in_body = True
            elif not any(line.startswith(hk) for hk in header_keys):
                if data["MESSAGE_ID"] and data["FROM"] and data["TO"]:
                    body_lines.append(line)

        data["BODY"] = "\n".join(body_lines).strip()
        data["raw_format"] = "FULL_ENVELOPE"

        call_id_match = re.search(r"CALL_ID:\s*([^\s\n]+)", data["BODY"])
        if call_id_match:
            data["CALL_ID"] = call_id_match.group(1).strip()

        if not data["BODY_SHA256"]:
            data["BODY_SHA256"] = compute_sha256(data["BODY"])

        if data["MESSAGE_ID"] and data["FROM"] and data["TO"]:
            return data

    # FORMATO 2: Envelope Compacto ChatGPT (ex: CG-000144 / CG-000145)
    first_line = lines[0] if lines else ""
    cg_match = re.match(r"^(CG-\d{5,7})\b", first_line)

    if cg_match:
        msg_id = cg_match.group(1)
        data["MESSAGE_ID"] = msg_id
        data["FROM"] = "CHATGPT"
        data["raw_format"] = "COMPACT_CHATGPT"

        body_start_idx = 1
        for idx in range(1, min(15, len(lines))):
            ln = lines[idx]
            if ln.startswith("TYPE:"):
                data["TYPE"] = ln.split(":", 1)[1].strip()
            elif ln.startswith("TO:"):
                data["TO"] = ln.split(":", 1)[1].strip()
            elif ln.startswith("CALL_ID:"):
                data["CALL_ID"] = ln.split(":", 1)[1].strip()
            elif ln.startswith("REPLY_TO:"):
                data["REPLY_TO"] = ln.split(":", 1)[1].strip()
            elif ln.startswith("TIMESTAMP:"):
                data["TIMESTAMP"] = ln.split(":", 1)[1].strip()
            elif ln == "" or ln.startswith("CONTEXT:") or ln.startswith("ACTION:"):
                body_start_idx = idx
                break

        body_text = "\n".join(lines[body_start_idx:]).strip()
        data["BODY"] = body_text if body_text else raw_clean
        data["BODY_SHA256"] = compute_sha256(data["BODY"])

        if not data["TO"]:
            data["TO"] = "ANTIGRAVITY"
        if not data["TYPE"]:
            data["TYPE"] = "CALL"

        return data

    if "TO: ANTIGRAVITY" in raw_clean or "TYPE: CALL" in raw_clean:
        record_rejection(raw_clean, comment_id, "Ambiguous envelope: missing MESSAGE_ID and compact CG prefix")
        return None

    return None


def record_rejection(raw_snippet: str, comment_id: Optional[int], reason: str):
    """Registra rejeição de envelope de forma auditável e fail-closed."""
    ensure_directories()
    entry = {
        "timestamp": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(),
        "comment_id": comment_id,
        "reason": reason,
        "raw_snippet": raw_snippet[:300],
    }
    with open(REJECTIONS_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    logger.warning(f"Envelope rejeitado e auditado (comment_id={comment_id}): {reason}")


class CanonicalCircuitManager:
    """Gerenciador de estado, journal diário e deduplicação global."""

    def __init__(self):
        ensure_directories()
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text("utf-8"))
            except Exception as e:
                logger.error(f"Erro ao ler state file: {e}")
        legacy_state = LEGACY_CIRCUITO_DIR / "runtime" / ".github_bridge_state.json"
        if legacy_state.exists():
            try:
                data = json.loads(legacy_state.read_text("utf-8"))
                logger.info("Migrando estado inicial de Downloads/circuito para runtime/bridge/state")
                return data
            except Exception:
                pass
        return {"processed_comment_ids": [], "processed_message_ids": [], "processed_keys": []}

    def _save_state(self):
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=2, ensure_ascii=False), "utf-8")
        tmp.replace(STATE_FILE)

    def is_processed(
        self,
        comment_id: Optional[int] = None,
        delivery_id: Optional[str] = None,
        message_id: Optional[str] = None,
        call_id: Optional[str] = None,
    ) -> bool:
        """Verificação de deduplicação composta atômica."""
        if comment_id and comment_id in self.state.get("processed_comment_ids", []):
            return True
        if message_id and message_id in self.state.get("processed_message_ids", []):
            return True

        composite_key = f"{comment_id or 'none'}:{delivery_id or 'none'}:{message_id or 'none'}:{call_id or 'none'}"
        if composite_key in self.state.get("processed_keys", []):
            return True

        return False

    def mark_processed(
        self,
        comment_id: Optional[int] = None,
        delivery_id: Optional[str] = None,
        message_id: Optional[str] = None,
        call_id: Optional[str] = None,
    ):
        """Marca identificadores como processados e persiste atomicamente."""
        if comment_id and comment_id not in self.state.setdefault("processed_comment_ids", []):
            self.state["processed_comment_ids"].append(comment_id)
        if message_id and message_id not in self.state.setdefault("processed_message_ids", []):
            self.state["processed_message_ids"].append(message_id)

        composite_key = f"{comment_id or 'none'}:{delivery_id or 'none'}:{message_id or 'none'}:{call_id or 'none'}"
        keys = self.state.setdefault("processed_keys", [])
        if composite_key not in keys:
            keys.append(composite_key)

        self.state["processed_comment_ids"] = self.state["processed_comment_ids"][-1000:]
        self.state["processed_message_ids"] = self.state["processed_message_ids"][-1000:]
        self.state["processed_keys"] = self.state["processed_keys"][-1000:]
        self._save_state()

    def append_journal(
        self,
        envelope: Dict[str, Any],
        source: str = "GITHUB_PR_1",
        comment_id: Optional[int] = None,
        delivery_id: Optional[str] = None,
        provenance: str = "PRIMARY_WEBHOOK",
        date_str: Optional[str] = None,
    ) -> Path:
        """
        Adiciona registro ao Journal diário append-only (journal/YYYY-MM-DD.jsonl).
        Atualiza o índice mestre journal/INDEX.json.
        """
        ensure_directories()
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
        if not date_str:
            date_str = now.strftime("%Y-%m-%d")

        journal_file = JOURNAL_DIR / f"{date_str}.jsonl"

        entry = {
            "timestamp": envelope.get("TIMESTAMP") or now.isoformat(),
            "source": source,
            "provenance": provenance,
            "comment_id": comment_id,
            "delivery_id": delivery_id,
            "MESSAGE_ID": envelope.get("MESSAGE_ID"),
            "CALL_ID": envelope.get("CALL_ID"),
            "REPLY_TO": envelope.get("REPLY_TO"),
            "FROM": envelope.get("FROM"),
            "TO": envelope.get("TO"),
            "TYPE": envelope.get("TYPE"),
            "body_sha256": envelope.get("BODY_SHA256"),
            "schema_version": envelope.get("schema_version", "CANONICAL_ENVELOPE_V1"),
        }

        line = json.dumps(entry, ensure_ascii=False)
        with open(journal_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")

        self._update_journal_index(date_str, journal_file)
        return journal_file

    def _update_journal_index(self, date_str: str, journal_file: Path):
        """Atualiza o journal/INDEX.json com contagens e hashes SHA-256."""
        index_data = {}
        if JOURNAL_INDEX_FILE.exists():
            try:
                index_data = json.loads(JOURNAL_INDEX_FILE.read_text("utf-8"))
            except Exception:
                index_data = {}

        data_bytes = journal_file.read_bytes()
        sha = hashlib.sha256(data_bytes).hexdigest()
        records_count = len([ln for ln in data_bytes.decode("utf-8", errors="replace").splitlines() if ln.strip()])

        files_entry = index_data.setdefault("files", {})
        files_entry[f"{date_str}.jsonl"] = {
            "date": date_str,
            "records": records_count,
            "bytes": len(data_bytes),
            "sha256": sha,
            "last_updated": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(),
        }

        total_records = sum(f.get("records", 0) for f in files_entry.values())
        index_data["total_records"] = total_records
        index_data["total_files"] = len(files_entry)
        index_data["last_updated"] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat()

        tmp = JOURNAL_INDEX_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(index_data, indent=2, ensure_ascii=False), "utf-8")
        tmp.replace(JOURNAL_INDEX_FILE)

    def deliver_to_inbox(self, envelope: Dict[str, Any]) -> Tuple[Path, str]:
        """
        Entrega a CALL ao inbox corrente (runtime/bridge/inbox/current_call.txt).
        Também mantém dual-write temporário em Downloads/circuito/conversa de ia.txt para cutover seguro.
        """
        ensure_directories()
        body = envelope.get("BODY", "")
        CURRENT_CALL_FILE.write_text(body, encoding="utf-8")

        try:
            if LEGACY_CIRCUITO_DIR.exists():
                LEGACY_CONVERSA_FILE.write_text(body, encoding="utf-8")
        except Exception as e:
            logger.warning(f"Dual-write legado falhou: {e}")

        body_sha = compute_sha256(body)
        return CURRENT_CALL_FILE, body_sha
