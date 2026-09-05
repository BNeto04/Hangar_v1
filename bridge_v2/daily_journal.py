#!/usr/bin/env python3
"""
bridge_v2/daily_journal.py — Diário Operacional de Circuito da Ponte Clean-Room V2.
Porta P-EXT-BRIDGE-V2-01 / CG-000149 / SPRINT-BRIDGE-V2-CLEANROOM-001

Gerencia a pasta canônica:
  C:\\Users\\PICHAU\\Hangar_v1\\runtime\\bridge_v2\\circuito_diario\\
com dois arquivos sincronizados por data local:
  1. YYYY-MM-DD.jsonl (append-only estruturado e auditável)
  2. YYYY-MM-DD.md (visão humana cronológica de fácil leitura)
"""

import datetime
import hashlib
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("daily-journal-v2")

REPO_ROOT = Path(__file__).resolve().parent.parent
CIRCUITO_DIARIO_DIR = REPO_ROOT / "runtime" / "bridge_v2" / "circuito_diario"


def ensure_journal_dir():
    CIRCUITO_DIARIO_DIR.mkdir(parents=True, exist_ok=True)


def get_local_date_str() -> str:
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%Y-%m-%d")


def get_local_time_str() -> str:
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%H:%M:%S")


def compute_event_hash(event: Dict[str, Any]) -> str:
    """Gera hash determinístico para deduplicação do evento no diário."""
    identity_str = (
        f"{event.get('channel')}|{event.get('event_type')}|{event.get('message_id')}|"
        f"{event.get('call_id')}|{event.get('github_comment_id')}|{event.get('summary')}"
    )
    return hashlib.sha256(identity_str.encode("utf-8")).hexdigest()


class DailyCircuitJournal:
    """Gerenciador do diário operacional diário em JSONL e Markdown."""

    def __init__(self, target_dir: Optional[Path] = None):
        self.journal_dir = target_dir or CIRCUITO_DIARIO_DIR
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        self.seen_event_hashes = set()

    def record_event(
        self,
        event_type: str,
        actor_from: str,
        actor_to: str,
        channel: str,
        summary: str,
        sprint_id: Optional[str] = None,
        task_id: Optional[str] = None,
        message_id: Optional[str] = None,
        call_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        github_comment_id: Optional[int] = None,
        status: Optional[str] = None,
        human_intervention: bool = False,
        source_ref: Optional[str] = None,
        date_str: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Grava um evento no diário do dia (JSONL append-only e atualização de Markdown).
        Realiza deduplicação automática.
        """
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))
        if not date_str:
            date_str = now.strftime("%Y-%m-%d")

        event = {
            "timestamp_iso8601": now.isoformat(),
            "time_local": now.strftime("%H:%M:%S"),
            "date_local": date_str,
            "sprint_id": sprint_id or "SPRINT-BRIDGE-V2-CLEANROOM-001",
            "task_id": task_id,
            "event_type": event_type,
            "actor_from": actor_from,
            "actor_to": actor_to,
            "channel": channel,
            "message_id": message_id,
            "call_id": call_id,
            "reply_to": reply_to,
            "github_comment_id": github_comment_id,
            "status": status or "INFO",
            "summary": summary.strip(),
            "human_intervention": human_intervention,
            "source_ref": source_ref,
        }

        event_hash = compute_event_hash(event)
        event["event_sha256"] = event_hash

        jsonl_path = self.journal_dir / f"{date_str}.jsonl"
        md_path = self.journal_dir / f"{date_str}.md"

        # Carregar hashes já vistos do JSONL se ainda não carregados
        if not self.seen_event_hashes and jsonl_path.exists():
            for line in jsonl_path.read_text("utf-8").splitlines():
                if line.strip():
                    try:
                        entry = json.loads(line)
                        if "event_sha256" in entry:
                            self.seen_event_hashes.add(entry["event_sha256"])
                    except Exception:
                        pass

        if event_hash in self.seen_event_hashes:
            logger.info(f"Evento já registrado no diário (dedupe: {event_hash[:12]}). Ignorando.")
            return None

        self.seen_event_hashes.add(event_hash)

        # 1. Append no JSONL
        with open(jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        # 2. Atualizar Markdown da visão diária
        self._update_markdown(date_str, jsonl_path, md_path)

        logger.info(f"Diário atualizado: [{event['time_local']}] {actor_from} -> {actor_to} ({event_type})")
        return event

    def _update_markdown(self, date_str: str, jsonl_path: Path, md_path: Path):
        """Regenera a visão humana Markdown a partir do histórico fiel do JSONL."""
        events = []
        if jsonl_path.exists():
            for line in jsonl_path.read_text("utf-8").splitlines():
                if line.strip():
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        pass

        timeline_lines = []
        started_tasks = []
        completed_tasks = []
        blocked_tasks = []
        human_interventions = []
        latest_sprint_state = "EM EXECUÇÃO"

        for ev in events:
            time_str = ev.get("time_local", "??:??:??")
            afrom = ev.get("actor_from", "SISTEMA")
            ato = ev.get("actor_to", "SISTEMA")
            etype = ev.get("event_type", "EVENT")
            sum_text = ev.get("summary", "")
            chan = ev.get("channel", "")

            # Linha do tempo
            timeline_lines.append(f"- **`{time_str}`** `[{chan}]` **{afrom} → {ato}** (`{etype}`): {sum_text}")

            # Classificação por seções
            if etype == "TASK_STARTED" and ev.get("task_id"):
                started_tasks.append(f"- `{ev.get('task_id')}`: {sum_text}")
            elif etype == "TASK_COMPLETED" and ev.get("task_id"):
                completed_tasks.append(f"- `{ev.get('task_id')}`: {sum_text}")
            elif etype in ("TASK_BLOCKED", "HOLD"):
                blocked_tasks.append(f"- `{ev.get('task_id', 'GERAL')}`: {sum_text}")

            if ev.get("human_intervention"):
                human_interventions.append(f"- **`{time_str}`** via `{chan}`: {sum_text}")

            if etype == "SPRINT_STATE_CHANGED" and ev.get("status"):
                latest_sprint_state = ev.get("status")

        md_content = f"""# CIRCUITO DIÁRIO OPERACIONAL — {date_str}

- **Data Local:** {date_str} (America/Recife)
- **Sprint Ativa:** SPRINT-BRIDGE-V2-CLEANROOM-001
- **Total de Eventos Registrados:** {len(events)}
- **Estado da Sprint:** `{latest_sprint_state}`

---

## 1. Linha do Tempo Cronológica

""" + ("\n".join(timeline_lines) if timeline_lines else "_Nenhum evento registrado hoje._") + f"""

---

## 2. Tarefas Iniciadas no Dia

""" + ("\n".join(started_tasks) if started_tasks else "_Nenhuma tarefa nova iniciada._") + f"""

---

## 3. Tarefas Concluídas no Dia

""" + ("\n".join(completed_tasks) if completed_tasks else "_Nenhuma tarefa concluída hoje._") + f"""

---

## 4. Bloqueios e HOLD

""" + ("\n".join(blocked_tasks) if blocked_tasks else "_Zero bloqueios ativos no momento._") + f"""

---

## 5. Intervenções Humanas

""" + ("\n".join(human_interventions) if human_interventions else "_Nenhuma intervenção humana registrada hoje._") + f"""

---

## 6. Estado Final da Sprint

- **Status:** `{latest_sprint_state}`
- **Última Atualização:** {get_local_time_str()}
- **Arquivo Canônico Auditável:** `circuito_diario/{date_str}.jsonl`
"""

        tmp_md = md_path.with_suffix(".tmp")
        tmp_md.write_text(md_content, encoding="utf-8")
        tmp_md.replace(md_path)
