#!/usr/bin/env python3
"""
Exporta o estado atual do Kanban Hermes (SQLite) para espelho no Git:
  - kanban/kanban_state.json
  - kanban/cards/<card_id>.md
"""

import datetime
import json
import os
import sqlite3
import subprocess
from pathlib import Path
from typing import Any, Dict, List


def export_kanban_to_git(
    db_path: str = r"C:\Users\PICHAU\AppData\Local\hermes\kanban.db",
    repo_path: str = r"C:\Users\PICHAU\syntheon_adk",
    push: bool = True,
) -> Dict[str, Any]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT id, title, body, status, priority, created_at, started_at, completed_at, result FROM tasks")
    rows = cur.fetchall()

    cards = []
    counts = {
        "triage": 0,
        "ready": 0,
        "todo": 0,
        "in_progress": 0,
        "blocked": 0,
        "review": 0,
        "done": 0,
        "archived": 0,
    }

    repo = Path(repo_path)
    kanban_dir = repo / "kanban"
    cards_dir = kanban_dir / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)

    for row in rows:
        cid, title, body, status, priority, created_at, started_at, completed_at, result_json = row
        if status in counts:
            counts[status] += 1
        else:
            counts[status] = 1

        try:
            meta = json.loads(result_json or "{}")
        except:
            meta = {}

        card_data = {
            "card_id": cid,
            "title": title,
            "body": body,
            "status": status,
            "priority": priority,
            "created_at": created_at,
            "started_at": started_at,
            "completed_at": completed_at,
            "metadata": meta,
        }
        cards.append(card_data)

        # Gera Markdown individual do card
        card_md = (
            f"# {title}\n\n"
            f"- **CARD_ID:** `{cid}`\n"
            f"- **STATUS:** `{status}`\n"
            f"- **PRIORITY:** `{priority}`\n"
            f"- **CREATED_AT:** `{created_at}`\n"
            f"- **COMPLETED_AT:** `{completed_at or 'null'}`\n\n"
            f"## Descrição\n{body or 'Sem descrição.'}\n\n"
            f"## Metadados Fatuais\n```json\n{json.dumps(meta, indent=2)}\n```\n"
        )
        (cards_dir / f"{cid}.md").write_text(card_md, encoding="utf-8")

    state_payload = {
        "schema": "HERMES-KANBAN-GIT-MIRROR-1",
        "generated_at": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(),
        "total_cards": len(cards),
        "counts": counts,
        "cards": cards,
    }

    state_file = kanban_dir / "kanban_state.json"
    state_file.write_text(json.dumps(state_payload, indent=2), encoding="utf-8")

    git_bin = r"C:\Program Files\Git\cmd\git.exe"
    if not Path(git_bin).exists():
        git_bin = "git"

    if push:
        try:
            subprocess.run([git_bin, "add", "kanban"], cwd=str(repo), check=True, capture_output=True)
            subprocess.run([git_bin, "commit", "-m", f"chore(kanban): atualizar espelho git ({counts['done']} done, {counts['review']} review)"], cwd=str(repo), check=True, capture_output=True)
            subprocess.run([git_bin, "push", "origin", "bridge/chatgpt-antigravity"], cwd=str(repo), check=True, capture_output=True)
            print("KANBAN_MIRROR_PUSHED_OK")
        except Exception as e:
            print(f"KANBAN_MIRROR_PUSH_ERROR: {e}")

    conn.close()
    return state_payload


if __name__ == "__main__":
    res = export_kanban_to_git()
    print(f"TOTAL_CARDS_EXPORTED: {res['total_cards']}, COUNTS: {res['counts']}")
