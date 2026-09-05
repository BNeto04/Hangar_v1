#!/usr/bin/env python3
"""
bridge_v2/schema.py — Schemas Canônicos e Normalização da Ponte Clean-Room V2.
Porta P-EXT-BRIDGE-V2-01 / Hangar_v1/EXTERNAL/BRIDGE_V2

Define os 4 envelopes canônicos obrigatórios:
1. CALL: Diretiva de tarefa do ChatGPT para o Antigravity.
2. RESULT: Laudo de execução/resultado do Antigravity para o ChatGPT.
3. OWNER_EVENT: Intervenções e telemetria humana (Telegram, Antigravity, ChatGPT).
4. CONTEXT_PACKET: Pacote contextual estruturado (<= 4 KiB) submetido pela extensão ao ChatGPT.
"""

import datetime
import hashlib
import json
import re
from typing import Any, Dict, Optional

SCHEMA_VERSION = "BRIDGE_V2_CANONICAL_SCHEMA_1"


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def get_current_iso_timestamp() -> str:
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat()


def get_current_local_date() -> str:
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%Y-%m-%d")


def normalize_call_envelope(raw_text: str, comment_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Normaliza chamadas (CALL) recebidas do GitHub PR #1.
    Suporta formato completo YAML-like e formato compacto do ChatGPT (CG-xxxxx).
    Retorna dicionário estruturado e canônico.
    """
    if not raw_text or not raw_text.strip():
        return None

    raw_clean = raw_text.strip()
    lines = [ln.strip() for ln in raw_clean.splitlines()]

    envelope: Dict[str, Any] = {
        "schema": SCHEMA_VERSION,
        "type": "CALL",
        "message_id": None,
        "timestamp": None,
        "from": "CHATGPT",
        "to": "ANTIGRAVITY",
        "call_id": None,
        "reply_to": None,
        "sprint_id": None,
        "priority": "P0",
        "body": "",
        "body_sha256": None,
        "github_comment_id": comment_id,
        "raw_format": None,
    }

    # Caso 1: Formato Completo
    if "MESSAGE_ID:" in raw_clean:
        envelope["raw_format"] = "FULL_ENVELOPE"
        body_lines = []
        in_body = False
        header_keys = ("MESSAGE_ID:", "TIMESTAMP:", "FROM:", "TO:", "TYPE:", "REPLY_TO:")

        for line in lines:
            if in_body:
                if line.startswith("BODY_SHA256:"):
                    in_body = False
                else:
                    body_lines.append(line)
            elif line.startswith("MESSAGE_ID:"):
                envelope["message_id"] = line.split(":", 1)[1].strip()
            elif line.startswith("TIMESTAMP:"):
                envelope["timestamp"] = line.split(":", 1)[1].strip()
            elif line.startswith("FROM:"):
                envelope["from"] = line.split(":", 1)[1].strip()
            elif line.startswith("TO:"):
                envelope["to"] = line.split(":", 1)[1].strip()
            elif line.startswith("REPLY_TO:"):
                envelope["reply_to"] = line.split(":", 1)[1].strip()
            elif line.startswith("BODY:"):
                in_body = True
            elif not any(line.startswith(hk) for hk in header_keys):
                if envelope["message_id"]:
                    body_lines.append(line)

        envelope["body"] = "\n".join(body_lines).strip()

    # Caso 2: Formato Compacto (ex: CG-000148)
    else:
        first_line = lines[0] if lines else ""
        cg_match = re.match(r"^(CG-\d{5,7})\b", first_line)
        if cg_match:
            envelope["raw_format"] = "COMPACT_CHATGPT"
            envelope["message_id"] = cg_match.group(1)

            body_start_idx = 1
            for idx in range(1, min(15, len(lines))):
                ln = lines[idx]
                if ln.startswith("TYPE:"):
                    envelope["type"] = ln.split(":", 1)[1].strip()
                elif ln.startswith("TO:"):
                    envelope["to"] = ln.split(":", 1)[1].strip()
                elif ln.startswith("REPLY_TO:"):
                    envelope["reply_to"] = ln.split(":", 1)[1].strip()
                elif ln.startswith("TIMESTAMP:"):
                    envelope["timestamp"] = ln.split(":", 1)[1].strip()
                elif ln.startswith("CALL_ID:"):
                    envelope["call_id"] = ln.split(":", 1)[1].strip()
                elif ln.startswith("SPRINT_ID:"):
                    envelope["sprint_id"] = ln.split(":", 1)[1].strip()
                elif ln.startswith("PRIORITY:"):
                    envelope["priority"] = ln.split(":", 1)[1].strip()
                elif ln == "" or ln.startswith("BODY:") or ln.startswith("SOVEREIGN SPRINT OBJECTIVE:"):
                    body_start_idx = idx
                    break

            body_text = "\n".join(lines[body_start_idx:]).strip()
            if body_text.startswith("BODY:"):
                body_text = body_text[len("BODY:"):].strip()
            envelope["body"] = body_text

    # Extrações complementares no corpo
    if not envelope["call_id"]:
        m = re.search(r"CALL_ID:\s*([^\s\n]+)", envelope["body"])
        if m:
            envelope["call_id"] = m.group(1).strip()

    if not envelope["sprint_id"]:
        m = re.search(r"SPRINT_ID:\s*([^\s\n]+)", envelope["body"])
        if m:
            envelope["sprint_id"] = m.group(1).strip()

    if not envelope["timestamp"]:
        envelope["timestamp"] = get_current_iso_timestamp()

    envelope["body_sha256"] = compute_sha256(envelope["body"])

    # Validação mínima
    if envelope["message_id"] and envelope["body"]:
        return envelope

    return None


def format_result_envelope(
    message_id: str,
    reply_to: str,
    status: str,
    body: str,
    sprint_id: Optional[str] = None,
    call_id: Optional[str] = None,
) -> str:
    """Formata um RESULT no padrão canônico para publicação no GitHub PR #1."""
    timestamp = get_current_iso_timestamp()
    body_clean = body.strip()
    body_sha = compute_sha256(body_clean)

    headers = [
        f"MESSAGE_ID: {message_id}",
        f"TIMESTAMP: {timestamp}",
        f"FROM: ANTIGRAVITY",
        f"TO: CHATGPT",
        f"TYPE: RESULT",
        f"REPLY_TO: {reply_to}",
    ]
    if sprint_id:
        headers.append(f"SPRINT_ID: {sprint_id}")
    if call_id:
        headers.append(f"CALL_ID: {call_id}")
    headers.append(f"STATUS: {status}")

    header_text = "\n".join(headers)
    return f"{header_text}\n\nBODY:\n{body_clean}\n\nBODY_SHA256: {body_sha}\n"


def format_owner_event(
    event_type: str,
    channel: str,
    summary: str,
    sprint_id: Optional[str] = None,
    task_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Cria um registro estruturado de OWNER_EVENT para intervenção e telemetria humana."""
    return {
        "schema": SCHEMA_VERSION,
        "type": "OWNER_EVENT",
        "event_type": event_type,
        "timestamp": get_current_iso_timestamp(),
        "date_local": get_current_local_date(),
        "channel": channel,  # CHATGPT | GITHUB_PR1 | ANTIGRAVITY | TELEGRAM | BRIDGE_V2
        "sprint_id": sprint_id,
        "task_id": task_id,
        "summary": summary,
        "human_intervention": True,
        "details": details or {},
    }


def format_context_packet(
    sprint_id: str,
    owner_objective: str,
    done_criteria: str,
    out_of_scope: str,
    last_call_id: str,
    last_message_id: str,
    github_comment_id: Optional[int],
    result_status: str,
    result_summary: str,
    current_state: str,
    blockers: str = "NONE",
    next_gpt_action: Optional[str] = None,
) -> str:
    """
    Constrói o CONTEXT_PACKET compacto (<= 4 KiB) para a extensão injetar no ChatGPT.
    Substitui o antigo 'v' cego por contexto executivo de continuidade.
    """
    if not next_gpt_action:
        next_gpt_action = (
            "1. Reconciliar RESULT com o OWNER_OBJECTIVE da Sprint.\n"
            "2. Se restarem itens autorizados, emitir próxima CALL mínima.\n"
            "3. Se todos os critérios estiverem satisfeitos, emitir STOP em Review/T4.\n"
            "4. Se houver divergência, acionar OWNER_DECISION_REQUIRED."
        )

    packet = f"""[CONTEXT_PACKET — SPRINT CONTINUITY]
SPRINT_ID: {sprint_id}
OWNER_OBJECTIVE: {owner_objective.strip()}
DONE_CRITERIA: {done_criteria.strip()}
OUT_OF_SCOPE: {out_of_scope.strip()}

LAST_CALL: {last_message_id} ({last_call_id}) | GitHub Comment: {github_comment_id or 'LOCAL'}
LATEST_RESULT_STATUS: {result_status}
LATEST_RESULT_SUMMARY:
{result_summary.strip()}

CURRENT_STATE: {current_state.strip()}
BLOCKERS: {blockers.strip()}

NEXT_GPT_ACTION:
{next_gpt_action.strip()}
"""
    # Garantir tamanho <= 4 KiB
    packet_bytes = packet.encode("utf-8")
    if len(packet_bytes) > 4000:
        packet = packet[:3800] + "\n...[TRUNCADO PARA CABER EM 4 KiB]..."

    return packet
