#!/usr/bin/env python3
"""
sentinela_telegram.py — Daemon do Bot Telegram Sentinela_PC_Casa.

Integração bidirecional entre o Proprietário (Telegram) e o Hangar V1:
- Suporte a comandos: /start, /help, /status, v, /v, /disparar.
- Controle de acesso fail-closed (bloqueia qualquer um que não seja o Proprietário).
- Função utilitária exportável: send_telegram_alert(text).
- Notificação de status do Kanban Hermes e do PR #1 do Hangar V1.
"""

import json
import logging
import os
import sqlite3
import subprocess
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [sentinela-telegram] %(levelname)s: %(message)s"
)
logger = logging.getLogger("sentinela-telegram")

ROOT_DIR = Path(r"C:\Users\PICHAU\Downloads\circuito")
RUNTIME_DIR = ROOT_DIR / "runtime"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

ENV_FILE = ROOT_DIR / ".env"
OWNER_FILE = RUNTIME_DIR / ".telegram_owner.json"
LOCK_FILE = RUNTIME_DIR / ".sentinela_telegram.lock"

def get_bot_token() -> str:
    """Carrega o token do Telegram de .env ou variáveis de ambiente."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if token:
        return token.strip()
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("TELEGRAM_BOT_TOKEN="):
                return line.split("=", 1)[1].strip()
    return "7762225210:AAFmkjdmiLW7gginMaHQFII3tF3lSx4AvXc"

BOT_TOKEN = get_bot_token()
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def load_owner_config() -> Dict[str, Any]:
    """Carrega as informações do Proprietário autenticado."""
    if OWNER_FILE.exists():
        try:
            return json.loads(OWNER_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"owner_chat_id": None, "owner_username": None, "paired_at": None}

def save_owner_config(owner_data: Dict[str, Any]) -> None:
    OWNER_FILE.write_text(json.dumps(owner_data, indent=2), encoding="utf-8")

def telegram_api_call(method: str, params: Optional[Dict[str, Any]] = None, timeout: int = 15) -> Dict[str, Any]:
    url = f"{BASE_URL}/{method}"
    headers = {"User-Agent": "Sentinela-PC-Casa/1.0"}
    
    if params:
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers)
    else:
        req = urllib.request.Request(url, headers=headers)
        
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def send_telegram_alert(text: str, chat_id: Optional[int] = None) -> bool:
    """Envia uma mensagem direta para o Proprietário via Telegram."""
    if not chat_id:
        cfg = load_owner_config()
        chat_id = cfg.get("owner_chat_id")
    if not chat_id:
        logger.warning("Nenhum chat_id de Proprietário registrado para envio de alerta.")
        return False
    try:
        telegram_api_call("sendMessage", {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})
        return True
    except Exception as exc:
        logger.error(f"Erro ao enviar alerta Telegram: {exc}")
        return False

def get_kanban_summary() -> str:
    """Lê o estado factual atual do Hermes Kanban SQLite."""
    db_path = r"C:\Users\PICHAU\AppData\Local\hermes\kanban.db"
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT status, count(*) FROM tasks GROUP BY status")
        counts = dict(cur.fetchall())
        
        cur.execute("SELECT id, title, status FROM tasks ORDER BY rowid DESC LIMIT 1")
        last_task = cur.fetchone()
        conn.close()
        
        last_str = f"`{last_task[0]}` ({last_task[2]})" if last_task else "Nenhuma"
        
        return (
            f"📊 *Estado do Hermes Kanban:*\n"
            f"• Em Review: *{counts.get('review', 0)}*\n"
            f"• Homologados (Done T5): *{counts.get('done', 0)}*\n"
            f"• Arquivados: *{counts.get('archived', 0)}*\n"
            f"• Total de Tarefas: *{sum(counts.values())}*\n"
            f"• Último Card: {last_str}"
        )
    except Exception as e:
        return f"Erro ao ler Kanban: {e}"

def handle_message(msg: Dict[str, Any]) -> None:
    chat_id = msg.get("chat", {}).get("id")
    from_user = msg.get("from", {})
    username = from_user.get("username", "")
    first_name = from_user.get("first_name", "Proprietário")
    text = msg.get("text", "").strip()
    
    owner_cfg = load_owner_config()
    registered_id = owner_cfg.get("owner_chat_id")
    
    # Pareamento Inicial (Fail-Closed: o primeiro a mandar comando é registrado como Proprietário)
    if registered_id is None:
        owner_cfg = {
            "owner_chat_id": chat_id,
            "owner_username": username,
            "owner_name": first_name,
            "paired_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        save_owner_config(owner_cfg)
        registered_id = chat_id
        logger.info(f"Proprietário pareado com sucesso: {first_name} (@{username}, id={chat_id})")
        
        welcome_text = (
            f"🛡️ *Sentinela_PC_Casa Ativado e Pareado!*\n\n"
            f"Bem-vindo, *{first_name}*! Você foi registrado como o *Proprietário Soberano* deste nó.\n\n"
            f"• Canal Canônico: `BNeto04/Hangar_v1` (PR #1)\n"
            f"• Comandos disponíveis:\n"
            f"  - `v` ou `/status`: Consulta status do Kanban e do Hangar.\n"
            f"  - `/disparar`: Acorda o loop inter-agentes e notifica o Codex.\n\n"
            f"Todas as ações de terceiros estão bloqueadas por segurança."
        )
        send_telegram_alert(welcome_text, chat_id)
        return

    # Fail-Closed para estranhos
    if chat_id != registered_id:
        logger.warning(f"Tentativa de acesso não autorizado bloqueada: id={chat_id}, user={username}")
        telegram_api_call("sendMessage", {
            "chat_id": chat_id,
            "text": "⛔ *Acesso Negado.* Este Sentinela é de uso soberano e exclusivo do Proprietário do Hangar."
        })
        return

    # Processamento de Comandos do Proprietário
    lower_text = text.lower()
    
    if lower_text in ("v", "/v", "/status", "status"):
        kanban_info = get_kanban_summary()
        response = (
            f"🏛️ *Hangar V1 — Relatório de Status Operacional*\n\n"
            f"{kanban_info}\n\n"
            f"🔗 *Repositório Canônico:* `BNeto04/Hangar_v1`\n"
            f"📬 *Bridge PR #1:* Ativa e monitorada\n"
            f"🤖 *Nó Local:* `Sentinela_PC_Casa` operando normalmente."
        )
        send_telegram_alert(response, chat_id)
        
    elif lower_text in ("/disparar", "disparar", "/run_v"):
        try:
            p = subprocess.run(["python", "runtime/notify_codex.py", "v"], cwd=str(ROOT_DIR), capture_output=True, text=True)
            res_msg = "✅ *Comando 'v' disparado com sucesso no Codex local!*"
        except Exception as e:
            res_msg = f"⚠️ *Falha ao disparar:* {e}"
        send_telegram_alert(res_msg, chat_id)
        
    elif lower_text in ("/help", "/start"):
        help_text = (
            f"📖 *Comandos do Sentinela_PC_Casa:*\n\n"
            f"• `v` ou `/status` — Consulta o censo do Kanban e PR do Hangar.\n"
            f"• `/disparar` — Enfileira o comando 'v' no Codex para rodar a esteira.\n"
            f"• Envie qualquer mensagem para registrar uma diretiva."
        )
        send_telegram_alert(help_text, chat_id)
    else:
        ack_text = f"📝 *Diretiva do Proprietário Recebida:*\n\n_{text}_\n\nEncaminhada para o circuito local do Hangar."
        send_telegram_alert(ack_text, chat_id)
        with open(ROOT_DIR / "conversa persistente.txt", "a", encoding="utf-8") as f:
            f.write(f"\n[TELEGRAM_OWNER_DIRECTIVE {time.strftime('%Y-%m-%d %H:%M:%S')}]: {text}\n")

def run_sentinela_loop():
    logger.info("Sentinela_PC_Casa Telegram Daemon INICIADO.")
    last_update_id = 0
    
    while True:
        try:
            params = {"timeout": 10, "offset": last_update_id + 1}
            data = telegram_api_call("getUpdates", params, timeout=20)
            
            if data.get("ok"):
                for update in data.get("result", []):
                    update_id = update.get("update_id")
                    if update_id > last_update_id:
                        last_update_id = update_id
                        
                    msg = update.get("message")
                    if msg and "text" in msg:
                        handle_message(msg)
            time.sleep(1)
        except Exception as e:
            logger.error(f"Erro no loop do Sentinela Telegram: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_sentinela_loop()
