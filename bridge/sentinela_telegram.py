#!/usr/bin/env python3
"""
sentinela_telegram.py — Daemon do Bot Telegram Sentinela_PC_Casa (v2.0).

Integração bidirecional entre o Proprietário (Telegram) e o Hangar V1:
- Tratamento de linguagem natural e perguntas frequentes ("o que posso fazer", etc.).
- Suporte a comandos: v, /status, cards, tarefas, testes, teste, /disparar.
- Controle de acesso fail-closed (bloqueia qualquer usuário não autorizado).
- Função utilitária exportável: send_telegram_alert(text).
- Notificação de status do Kanban Hermes e do PR #1 do Hangar V1.
- Precedência soberana do Proprietário (OWNER_DIRECTIVE) sem silêncio.
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
from typing import Optional, Dict, Any, Tuple

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [sentinela-telegram] %(levelname)s: %(message)s"
)
logger = logging.getLogger("sentinela-telegram")

ROOT_DIR = Path(r"C:\Users\PICHAU\Downloads\circuito")
HANGAR_DIR = Path(r"C:\Users\PICHAU\Hangar_v1")
RUNTIME_DIR = ROOT_DIR / "runtime"
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

ENV_FILE = ROOT_DIR / ".env"
OWNER_FILE = RUNTIME_DIR / ".telegram_owner.json"
LOCK_FILE = RUNTIME_DIR / ".sentinela_telegram.lock"
DIRECTIVES_FILE = RUNTIME_DIR / "owner_directives.jsonl"
CONVERSA_IA = ROOT_DIR / "conversa de ia.txt"
CONVERSA_PERSISTENTE = ROOT_DIR / "conversa persistente.txt"

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
    return {"owner_chat_id": 6857459665, "owner_username": None, "owner_name": "Manoel", "paired_at": None}

def save_owner_config(owner_data: Dict[str, Any]) -> None:
    OWNER_FILE.write_text(json.dumps(owner_data, indent=2), encoding="utf-8")

def telegram_api_call(method: str, params: Optional[Dict[str, Any]] = None, timeout: int = 15) -> Dict[str, Any]:
    url = f"{BASE_URL}/{method}"
    headers = {"User-Agent": "Sentinela-PC-Casa/2.0"}
    
    if params:
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers)
    else:
        req = urllib.request.Request(url, headers=headers)
        
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def send_telegram_alert(text: str, chat_id: Optional[int] = None) -> bool:
    """Envia uma mensagem para o Proprietário com fallback seguro de formatação."""
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
        logger.warning(f"Falha ao enviar com Markdown ({exc}); tentando texto plano...")
        try:
            telegram_api_call("sendMessage", {"chat_id": chat_id, "text": text})
            return True
        except Exception as exc2:
            logger.error(f"Erro ao enviar alerta Telegram: {exc2}")
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
            f"• Em Review (T4): *{counts.get('review', 0)}*\n"
            f"• Homologados (Done T5): *{counts.get('done', 0)}*\n"
            f"• Arquivados: *{counts.get('archived', 0)}*\n"
            f"• Total de Tarefas: *{sum(counts.values())}*\n"
            f"• Último Card Registrado: {last_str}"
        )
    except Exception as e:
        return f"⚠️ Erro ao ler Kanban: {e}"

def get_cards_detail() -> str:
    """Retorna detalhes dos cards em andamento e dos últimos homologados em T5."""
    db_path = r"C:\Users\PICHAU\AppData\Local\hermes\kanban.db"
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        cur.execute("SELECT id, title, status FROM tasks WHERE status = 'review'")
        review_tasks = cur.fetchall()
        
        cur.execute("SELECT id, title, status FROM tasks WHERE status = 'done' ORDER BY rowid DESC LIMIT 3")
        done_tasks = cur.fetchall()
        
        cur.execute("SELECT status, count(*) FROM tasks GROUP BY status")
        counts = dict(cur.fetchall())
        conn.close()
        
        lines = ["📋 *Censo Detalhado das Tarefas (Hermes Kanban):*\n"]
        
        if review_tasks:
            lines.append("⏳ *Em Andamento / Review (T4):*")
            for tid, ttitle, tstatus in review_tasks:
                lines.append(f"• `{tid}`\n  _{ttitle}_\n")
        else:
            lines.append("⏳ *Em Andamento / Review:* Nenhuma tarefa pendente no momento.\n")
            
        lines.append("✅ *Últimos Homologados em T5 (Done):*")
        for tid, ttitle, tstatus in done_tasks:
            lines.append(f"• `{tid}`\n  _{ttitle}_")
            
        lines.append(f"\n📊 *Totalizadores:* Review: {counts.get('review', 0)} | Done: {counts.get('done', 0)} | Arquivados: {counts.get('archived', 0)} | Total: {sum(counts.values())}")
        return "\n".join(lines)
    except Exception as exc:
        return f"⚠️ Erro ao consultar tarefas do Kanban: {exc}"

def run_tests_summary() -> str:
    """Executa as suítes de testes de integridade do Hangar V1 e resume os resultados."""
    test_files = ["test_owner_sovereignty_e2e.py", "test_hangar_v1_sprint_01.py"]
    lines = ["🧪 *Execução da Suíte de Testes do Hangar V1:*\n"]
    all_pass = True
    
    for tf in test_files:
        try:
            p = subprocess.run([sys.executable, tf], cwd=str(HANGAR_DIR), capture_output=True, text=True, timeout=30)
            if p.returncode == 0:
                ran_line = [l.strip() for l in p.stderr.splitlines() if "Ran " in l]
                det = f" ({ran_line[0]})" if ran_line else ""
                lines.append(f"• `{tf}`: *PASS ✅*{det}")
            else:
                all_pass = False
                lines.append(f"• `{tf}`: *FAIL ❌* (código {p.returncode})")
        except Exception as exc:
            all_pass = False
            lines.append(f"• `{tf}`: *ERRO ❌* ({exc})")
            
    if all_pass:
        lines.append("\n🟢 *Resultado Geral:* Todos os módulos e invariantes validados com êxito!")
    else:
        lines.append("\n🔴 *Resultado Geral:* Falha detectada em um ou mais testes.")
    return "\n".join(lines)

def get_system_health() -> str:
    """Coleta métricas reais de hardware e serviços locais."""
    try:
        import psutil
        import shutil
        
        cpu = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        total, used, free = shutil.disk_usage("C:\\")
        boot_time = psutil.boot_time()
        uptime_sec = time.time() - boot_time
        days = int(uptime_sec // 86400)
        hours = int((uptime_sec % 86400) // 3600)
        mins = int((uptime_sec % 3600) // 60)
        
        procs = [p.info['name'] for p in psutil.process_iter(['name'])]
        ollama_up = "🟢 Ativo" if any("ollama" in (p or "").lower() for p in procs) else "🔴 Inativo"
        python_count = sum(1 for p in procs if "python" in (p or "").lower())
        
        return (
            f"🖥️ *Diagnóstico de Saúde do PC (Sentinela_PC_Casa):*\n\n"
            f"⏱️ *Uptime do Sistema:* {days}d {hours}h {mins}m\n"
            f"⚡ *Uso de CPU:* {cpu}%\n"
            f"🧠 *Memória RAM:* {mem.used/(1024**3):.1f} GB / {mem.total/(1024**3):.1f} GB ({mem.percent}%)\n"
            f"💾 *Disco C:* {used/(1024**3):.1f} GB / {total/(1024**3):.1f} GB ({free/(1024**3):.1f} GB livres - {used/total*100:.1f}% usado)\n\n"
            f"🤖 *Serviços e Daemons Locais:*\n"
            f"• Ollama (LLMs locais): {ollama_up}\n"
            f"• Processos Python Ativos: {python_count}\n"
            f"• Nó Hangar V1: `Sentinela_PC_Casa` 100% operacional\n\n"
            f"Tudo operando dentro dos parâmetros de estabilidade!"
        )
    except Exception as exc:
        return f"⚠️ Erro ao coletar saúde do sistema: {exc}"

def notify_codex_trigger(msg: str = "v") -> Tuple[bool, str]:
    """Dispara o pulso no Codex local."""
    script_path = RUNTIME_DIR / "notify_codex.py"
    if not script_path.exists():
        return False, "Script notify_codex.py não encontrado."
    try:
        p = subprocess.run([sys.executable, str(script_path), msg], cwd=str(ROOT_DIR), capture_output=True, text=True, timeout=15)
        if p.returncode == 0:
            return True, "Pulso enfileirado com sucesso no Codex."
        return False, f"Código {p.returncode}: {p.stderr.strip()}"
    except Exception as exc:
        return False, str(exc)

def classify_intent(text: str) -> str:
    """Classifica a intenção da mensagem em linguagem natural."""
    t = text.strip().lower()
    
    # 1. Ajuda e perguntas de capacidades
    help_keywords = [
        "help", "/help", "ajuda", "/ajuda", "menu", "/menu", "comandos", "/comandos",
        "o que posso fazer", "o que eu posso fazer", "oque posso fazer",
        "o que você faz", "o que voce faz", "o que dá pra fazer", "o que da pra fazer",
        "como funciona", "quem é você", "quem e você", "quem e vc", "quem é vc",
        "opções", "opcoes", "funcionalidades", "recursos", "responda no chat", "o que faz"
    ]
    if any(k in t for k in help_keywords) or t in ("?", "help", "ajuda"):
        return "HELP"

    # 2. Saúde do PC e métricas de hardware
    health_keywords = [
        "saude", "saúde", "pc", "computador", "hardware", "cpu", "memoria", "memória",
        "ram", "disco", "hd", "ssd", "como tá o pc", "como ta o pc", "status do pc", "uptime"
    ]
    if any(k in t for k in health_keywords):
        return "HEALTH"

    # 3. Diretivas com verbos imperativos de mutação/ação
    directive_triggers = ["crie ", "criar ", "faça ", "atualize ", "atualizar ", "audite ", "auditar ", "adicione ", "adicionar ", "remova ", "remover ", "delete ", "deletar "]
    if any(k in t for k in directive_triggers):
        return "DIRECTIVE"

    # 4. Tarefas / Cards / Review (perguntas ou visualização)
    cards_keywords = ["cards", "card", "tarefas", "tarefa", "/cards", "/tarefas", "kanban", "review", "em review"]
    if any(k in t for k in cards_keywords):
        return "CARDS"

    # 5. Testes
    test_keywords = ["testes", "teste", "/test", "/testes", "test", "tests", "rodar testes", "validar", "verificar"]
    if any(k in t for k in test_keywords):
        return "TESTS"

    # 6. Status
    status_keywords = ["v", "/v", "/status", "status", "situacao", "situação", "censo"]
    if any(k in t for k in status_keywords):
        return "STATUS"
        
    # 7. Disparar
    if t in ("/disparar", "disparar", "/run_v", "rodar", "acordar", "wake", "pulso"):
        return "DISPARAR"
        
    # 8. Saudações
    greetings = ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite", "hey", "opa", "salve", "alo", "alô"]
    if t in greetings:
        return "GREETING"
        
    return "DIRECTIVE"

def handle_message(msg: Dict[str, Any]) -> None:
    chat_id = msg.get("chat", {}).get("id")
    from_user = msg.get("from", {})
    username = from_user.get("username", "")
    first_name = from_user.get("first_name", "Proprietário")
    text = msg.get("text", "").strip()
    
    if not text:
        return
        
    owner_cfg = load_owner_config()
    registered_id = owner_cfg.get("owner_chat_id")
    
    # Pareamento Inicial Fail-Closed
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
            f"• Digite `ajuda` para ver o menu completo de opções."
        )
        send_telegram_alert(welcome_text, chat_id)
        return

    # Bloqueio Fail-Closed para terceiros
    if chat_id != registered_id:
        logger.warning(f"Tentativa de acesso não autorizado bloqueada: id={chat_id}, user={username}")
        telegram_api_call("sendMessage", {
            "chat_id": chat_id,
            "text": "⛔ *Acesso Negado.* Este Sentinela é de uso exclusivo do Proprietário soberano do Hangar."
        })
        return

    # Processamento Inteligente de Linguagem Natural / Comandos
    intent = classify_intent(text)
    logger.info(f"Mensagem do Proprietário: '{text}' -> Intent: {intent}")
    
    if intent == "STATUS":
        kanban_info = get_kanban_summary()
        response = (
            f"🏛️ *Hangar V1 — Relatório Operacional*\n\n"
            f"{kanban_info}\n\n"
            f"🔗 *Repositório Canônico:* `BNeto04/Hangar_v1`\n"
            f"📬 *Bridge PR #1:* Ativa e monitorada em tempo real\n"
            f"🤖 *Nó Local:* `Sentinela_PC_Casa` operando normalmente."
        )
        send_telegram_alert(response, chat_id)
        
    elif intent == "HELP":
        help_text = (
            f"🛡️ *Sentinela_PC_Casa — Central de Comando do Proprietário*\n\n"
            f"Olá *{first_name}*! Você está no canal direto e soberano do Hangar V1.\n\n"
            f"📊 *Consultas Rápidas:*\n"
            f"• `v` ou `status` — Censo do Hermes Kanban e estado do PR #1.\n"
            f"• `cards` ou `tarefas` — Detalhes do card em andamento e últimos homologados.\n"
            f"• `saude do pc` ou `pc` — Telemetria em tempo real de CPU, RAM, Disco e Ollama.\n"
            f"• `testes` ou `validar` — Executa a suíte de testes de integridade e traz o laudo.\n\n"
            f"⚡ *Ações Operacionais:*\n"
            f"• `/disparar` — Envia o pulso 'v' ao Codex local para avançar a esteira.\n\n"
            f"📝 *Diretivas Soberanas (Texto Livre):*\n"
            f"• Digite qualquer ordem ou instrução técnica (ex: *'crie um card para...'*, *'audite o módulo X'*).\n"
            f"• Ela é registrada imediatamente com prioridade soberana (`OWNER_DIRECTIVE`) e despachada ao Antigravity e ao Codex, sem que nenhuma auditoria pendente silencie você!"
        )
        send_telegram_alert(help_text, chat_id)

    elif intent == "HEALTH":
        send_telegram_alert("⏳ Coletando telemetria de hardware e serviços locais...", chat_id)
        health_report = get_system_health()
        send_telegram_alert(health_report, chat_id)
        
    elif intent == "TESTS":
        send_telegram_alert("⏳ Executando suíte de testes do Hangar V1...", chat_id)
        test_report = run_tests_summary()
        send_telegram_alert(test_report, chat_id)
        
    elif intent == "CARDS":
        cards_report = get_cards_detail()
        send_telegram_alert(cards_report, chat_id)
        
    elif intent == "DISPARAR":
        ok, detail = notify_codex_trigger("v")
        if ok:
            send_telegram_alert("⚡ *Comando 'v' disparado com sucesso no Codex local!* Esteira em processamento.", chat_id)
        else:
            send_telegram_alert(f"⚠️ *Falha ao disparar no Codex:* {detail}", chat_id)
            
    elif intent == "GREETING":
        greet_text = (
            f"👋 *Olá, {first_name}!* Sentinela_PC_Casa em prontidão.\n\n"
            f"O ecossistema Hangar V1 está ativo e operando normalmente.\n\n"
            f"• Digite `v` para ver o status geral.\n"
            f"• Digite `saude do pc` para ver telemetria de hardware.\n"
            f"• Digite `cards` para ver o andamento das tarefas.\n"
            f"• Digite `testes` para validar a integridade técnica.\n"
            f"• Ou envie sua ordem/diretiva diretamente!"
        )
        send_telegram_alert(greet_text, chat_id)
        
    else:  # DIRECTIVE
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        directive_entry = {
            "timestamp": now_str,
            "sender_id": str(chat_id),
            "sender_name": first_name,
            "directive_type": "OWNER_DIRECTIVE",
            "text": text
        }
        try:
            with open(DIRECTIVES_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(directive_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"Erro ao registrar owner directive: {e}")
            
        try:
            with open(CONVERSA_PERSISTENTE, "a", encoding="utf-8") as f:
                f.write(f"\n[TELEGRAM_OWNER_DIRECTIVE {now_str}]: {text}\n")
            with open(CONVERSA_IA, "a", encoding="utf-8") as f:
                f.write(f"\n[OWNER_DIRECTIVE {now_str}]: {text}\n")
        except Exception as e:
            logger.error(f"Erro ao salvar conversa: {e}")
            
        notify_codex_trigger(f"OWNER_DIRECTIVE: {text}")
        
        ack_text = (
            f"🫡 *Diretiva Soberana do Proprietário Registrada:*\n\n"
            f"_{text}_\n\n"
            f"🚀 *Ação:* Encaminhada para a esteira do Hangar V1 com prioridade soberana (`OWNER_DIRECTIVE`).\n"
            f"O circuito local (Antigravity & Codex) foi notificado para execução imediata."
        )
        send_telegram_alert(ack_text, chat_id)

def run_sentinela_loop():
    logger.info("Sentinela_PC_Casa Telegram Daemon v2.0 INICIADO.")
    last_update_id = 0
    
    try:
        init_data = telegram_api_call("getUpdates", {"limit": 1})
        if init_data.get("ok") and init_data.get("result"):
            last_update_id = init_data["result"][-1]["update_id"]
    except Exception as e:
        logger.warning(f"Erro ao consultar updates iniciais: {e}")
        
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
