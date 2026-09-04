#!/usr/bin/env python3
"""
GitHub PR Relay: Polling bidirecional do PR #2 (BNeto04/syntheon_adk) para o circuito local.
Intervalo: 10s. Deduplicação estrita por comment_id e MESSAGE_ID.
"""

import argparse
import datetime
import hashlib
import json
import logging
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("github-pr-relay")


def get_git_executable() -> str:
    import shutil
    git_path = shutil.which("git")
    if git_path:
        return git_path
    candidates = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Users\PICHAU\AppData\Local\Programs\Git\cmd\git.exe",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return "git"


def get_github_token(repo_dir: Optional[str] = None) -> Optional[str]:
    """Obtém o token do GitHub com segurança."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token

    # 1. Tentar ler do .git/config do Hangar_v1
    git_config = Path(r"C:\Users\PICHAU\Hangar_v1\.git\config")
    if git_config.exists():
        try:
            content = git_config.read_text(encoding="utf-8")
            import re
            m = re.search(r"x-access-token:([a-zA-Z0-9_]+)@github\.com", content)
            if m:
                return m.group(1)
        except Exception:
            pass

    target_cwd = repo_dir if (repo_dir and Path(repo_dir).exists()) else r"C:\Users\PICHAU\Hangar_v1"
    git_bin = get_git_executable()

    try:
        env = os.environ.copy()
        env["GCM_INTERACTIVE"] = "never"
        env["GIT_TERMINAL_PROMPT"] = "0"
        res = subprocess.run(
            [git_bin, "credential", "fill"],
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True,
            text=True,
            timeout=3,
            cwd=target_cwd,
            env=env
        )
        for line in res.stdout.splitlines():
            if line.startswith("password="):
                pwd = line.split("=", 1)[1].strip()
                if pwd:
                    return pwd
    except Exception as exc:
        logger.error(f"Erro ao buscar credenciais git: {exc}")
    return None


def compute_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_envelope(raw_text: str) -> Optional[Dict[str, Any]]:
    """Faz o parse estrito do envelope YAML-like de mensagens da ponte."""
    lines = raw_text.strip().splitlines()
    data = {}
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
            if "MESSAGE_ID" in data and "FROM" in data and "TO" in data:
                if line.startswith("BODY_SHA256:"):
                    data["BODY_SHA256"] = line.split(":", 1)[1].strip()
                else:
                    body_lines.append(line)

    data["BODY"] = "\n".join(body_lines).strip()
    if not data["BODY"] and raw_text.strip():
        data["BODY"] = raw_text.strip()

    if "MESSAGE_ID" in data and "FROM" in data and "TO" in data and data["BODY"]:
        return data
    return None


def format_envelope(
    message_id: str,
    from_agent: str,
    to_agent: str,
    msg_type: str,
    body: str,
    reply_to: Optional[str] = None,
) -> str:
    timestamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat()
    body_sha = compute_sha256(body.strip())
    
    return (
        f"MESSAGE_ID: {message_id}\n"
        f"TIMESTAMP: {timestamp}\n"
        f"FROM: {from_agent}\n"
        f"TO: {to_agent}\n"
        f"TYPE: {msg_type}\n"
        f"REPLY_TO: {reply_to or 'null'}\n\n"
        f"BODY:\n{body.strip()}\n\n"
        f"BODY_SHA256: {body_sha}\n"
    )


class GitHubPRRelay:
    def __init__(
        self,
        repo: str = "BNeto04/Hangar_v1",
        pr_number: int = 1,
        root_dir: str = r"C:\Users\PICHAU\Downloads\circuito",
        poll_interval: int = 10,
    ):
        self.repo = repo
        self.pr_number = pr_number
        self.root_dir = Path(root_dir)
        self.poll_interval = poll_interval
        self.token = get_github_token()
        self.state_file = self.root_dir / "runtime" / ".github_bridge_state.json"
        self.lock_file = self.root_dir / "runtime" / ".github_pr_relay.lock"
        self.target_ia_file = self.root_dir / "conversa de ia.txt"
        
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text("utf-8"))
            except Exception as e:
                logger.warning(f"Erro ao carregar estado: {e}")
        return {"processed_comment_ids": [], "processed_message_ids": []}

    def _save_state(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def post_comment(self, envelope_text: str) -> Optional[int]:
        if not self.token:
            self.token = get_github_token()
        if not self.token:
            logger.error("Token do GitHub não disponível para postar comentário.")
            return None

        url = f"https://api.github.com/repos/{self.repo}/issues/{self.pr_number}/comments"
        headers = {
            "Authorization": f"token {self.token}",
            "User-Agent": "Antigravity-GitHub-Relay/1.0",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }
        payload = json.dumps({"body": envelope_text}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                comment_id = data.get("id")
                logger.info(f"Comentário postado com sucesso no PR #{self.pr_number}! ID={comment_id}")
                try:
                    from sentinela_telegram import send_telegram_alert
                    send_telegram_alert(f"📤 *Novo Comentário/RESULT Publicado no PR #{self.pr_number}!* (ID: `{comment_id}`)")
                except Exception:
                    pass
                return comment_id
        except Exception as exc:
            logger.error(f"Falha ao postar comentário no PR #{self.pr_number}: {exc}")
            return None

    def fetch_comments(self) -> List[Dict[str, Any]]:
        if not self.token:
            self.token = get_github_token()
        if not self.token:
            logger.error("Token do GitHub não disponível para fetch.")
            return []

        all_comments = []
        page = 1
        while True:
            url = f"https://api.github.com/repos/{self.repo}/issues/{self.pr_number}/comments?per_page=100&page={page}"
            headers = {
                "Authorization": f"token {self.token}",
                "User-Agent": "Antigravity-GitHub-Relay/1.0",
                "Accept": "application/vnd.github.v3+json",
            }
            req = urllib.request.Request(url, headers=headers)

            try:
                with urllib.request.urlopen(req) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    if not data or not isinstance(data, list):
                        break
                    all_comments.extend(data)
                    if len(data) < 100:
                        break
                    page += 1
            except Exception as exc:
                logger.error(f"Erro ao buscar comentários do PR #{self.pr_number} (página {page}): {exc}")
                break
        return all_comments

    def process_cycle(self) -> int:
        comments = self.fetch_comments()
        new_delivered = 0

        for c in comments:
            cid = c.get("id")
            if cid in self.state["processed_comment_ids"]:
                continue

            raw_body = c.get("body", "")
            envelope = parse_envelope(raw_body)
            if not envelope:
                # Não é um envelope estruturado, marca como visto para não reanalisar
                self.state["processed_comment_ids"].append(cid)
                continue

            mid = envelope.get("MESSAGE_ID")
            from_agent = envelope.get("FROM")
            to_agent = envelope.get("TO")
            msg_type = envelope.get("TYPE")

            if from_agent == "CHATGPT" and to_agent == "ANTIGRAVITY" and msg_type in ("CALL", "MESSAGE"):
                if mid in self.state["processed_message_ids"]:
                    logger.info(f"Mensagem {mid} já processada anteriormente (deduplicação).")
                    self.state["processed_comment_ids"].append(cid)
                    continue

                logger.info(f"NOVA MENSAGEM DETECTADA: {mid} (Comment ID: {cid})")
                
                # Entrega para conversa de ia.txt
                body_content = envelope.get("BODY", "")
                self.target_ia_file.write_text(body_content, encoding="utf-8")
                logger.info(f"Conteúdo de {mid} entregue com sucesso para {self.target_ia_file}")
                try:
                    from sentinela_telegram import send_telegram_alert
                    send_telegram_alert(f"📥 *Nova CALL Recebida do ChatGPT!*\n\n• *MESSAGE_ID:* `{mid}`\n• *PR #{self.pr_number} Comment ID:* `{cid}`\n\n_{body_content[:180]}..._")
                except Exception:
                    pass

                self.state["processed_message_ids"].append(mid)
                self.state["processed_comment_ids"].append(cid)
                new_delivered += 1
                break  # Processa uma por ciclo para manter ordem rigorosa
            else:
                self.state["processed_comment_ids"].append(cid)

        if new_delivered > 0:
            self._save_state()

        return new_delivered

    def run_forever(self):
        self.lock_file.parent.mkdir(parents=True, exist_ok=True)
        self.lock_file.write_text(str(os.getpid()), encoding="utf-8")
        logger.info(f"GitHub PR Relay INICIADO (PID {os.getpid()}). Polling: {self.poll_interval}s")

        try:
            while True:
                try:
                    self.process_cycle()
                except Exception as exc:
                    logger.error(f"Erro no ciclo de polling: {exc}")
                time.sleep(self.poll_interval)
        finally:
            if self.lock_file.exists():
                self.lock_file.unlink()
            logger.info("GitHub PR Relay ENCERRADO.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitHub PR Relay")
    parser.add_argument("--daemon", action="store_true", help="Executa o loop contínuo de polling")
    parser.add_argument("--post-ack", action="store_true", help="Posta um ACK no PR #2")
    parser.add_argument("--post-result", action="store_true", help="Posta um RESULT no PR #2")
    parser.add_argument("--message-id", default=None)
    parser.add_argument("--reply-to", default=None)
    parser.add_argument("--body", default=None)
    parser.add_argument("--poll-interval", type=int, default=10)
    args = parser.parse_args()

    relay = GitHubPRRelay(poll_interval=args.poll_interval)

    if args.post_ack:
        mid = args.message_id or f"AG-ACK-{int(time.time())}"
        reply_to = args.reply_to or "CG-000002"
        body = args.body or "ACK: Mensagem recebida e processada com sucesso pelo Antigravity."
        env = format_envelope(mid, "ANTIGRAVITY", "CHATGPT", "ACK", body, reply_to)
        relay.post_comment(env)
    elif args.post_result:
        mid = args.message_id or f"AG-RES-{int(time.time())}"
        reply_to = args.reply_to or "CG-000002"
        body = args.body or "RESULT: Execução concluída."
        env = format_envelope(mid, "ANTIGRAVITY", "CHATGPT", "RESULT", body, reply_to)
        relay.post_comment(env)
    elif args.daemon:
        relay.run_forever()
    else:
        delivered = relay.process_cycle()
        print(f"CYCLE_COMPLETED. Delivered: {delivered}")
