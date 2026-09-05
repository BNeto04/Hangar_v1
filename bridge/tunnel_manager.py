#!/usr/bin/env python3
"""
tunnel_manager.py — Gerenciador do túnel seguro local (Cloudflare Quick Tunnel)
e registro automatizado do Webhook na API do GitHub.
"""

import json
import logging
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s [tunnel-manager] %(levelname)s: %(message)s")
logger = logging.getLogger("tunnel-manager")

BIN_DIR = Path(r"C:\Users\PICHAU\Hangar_v1\bin")
CLOUDFLARED_EXE = BIN_DIR / "cloudflared.exe"
DOWNLOAD_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

STATE_FILE = Path(r"C:\Users\PICHAU\Hangar_v1\runtime\.tunnel_state.json")

def get_github_token() -> Optional[str]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token
    git_config = Path(r"C:\Users\PICHAU\Hangar_v1\.git\config")
    if git_config.exists():
        try:
            content = git_config.read_text(encoding="utf-8")
            m = re.search(r"x-access-token:([a-zA-Z0-9_]+)@github\.com", content)
            if m:
                return m.group(1)
        except Exception:
            pass
    return None

def ensure_cloudflared_binary() -> Path:
    """Garante a existência do binário oficial cloudflared.exe em bin/."""
    if CLOUDFLARED_EXE.exists() and CLOUDFLARED_EXE.stat().st_size > 10_000_000:
        return CLOUDFLARED_EXE
        
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    logger.info(f"Baixando binario oficial cloudflared.exe para {CLOUDFLARED_EXE}...")
    req = urllib.request.Request(DOWNLOAD_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp, open(CLOUDFLARED_EXE, "wb") as out:
        out.write(resp.read())
        
    logger.info(f"Download concluido com sucesso ({CLOUDFLARED_EXE.stat().st_size} bytes).")
    return CLOUDFLARED_EXE

class TunnelManager:
    def __init__(self, local_port: int = 8766, repo: str = "BNeto04/Hangar_v1", secret: str = "hangar_v1_webhook_secret_soberano"):
        self.local_port = local_port
        self.repo = repo
        self.secret = secret
        self.process: Optional[subprocess.Popen] = None
        self.public_url: Optional[str] = None
        self.webhook_id: Optional[int] = None

    def start_tunnel(self, timeout: int = 30) -> str:
        exe = ensure_cloudflared_binary()
        cmd = [str(exe), "tunnel", "--url", f"http://127.0.0.1:{self.local_port}", "--no-autoupdate"]
        logger.info(f"Iniciando tunel: {' '.join(cmd)}")
        
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        
        t0 = time.time()
        url = None
        while time.time() - t0 < timeout:
            line = self.process.stderr.readline()
            if not line and self.process.poll() is not None:
                raise RuntimeError(f"Processo cloudflared encerrou prematuramente com codigo {self.process.poll()}")
            m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if m:
                url = m.group(0)
                break
            time.sleep(0.1)
            
        if not url:
            self.stop_tunnel()
            raise TimeoutError(f"Nao foi possivel obter a URL do tunel em {timeout}s")
            
        self.public_url = url
        logger.info(f"Tunel estabelecido com sucesso: {self.public_url}")
        self._save_state()
        return self.public_url

    def register_github_webhook(self) -> int:
        if not self.public_url:
            raise ValueError("O tunel deve ser iniciado antes de registrar o webhook.")
            
        token = get_github_token()
        if not token:
            raise ValueError("GITHUB_TOKEN nao encontrado para registrar o webhook via API.")
            
        target_url = f"{self.public_url}/github-webhook"
        logger.info(f"Registrando webhook no GitHub para {self.repo} -> {target_url}")
        
        url = f"https://api.github.com/repos/{self.repo}/hooks"
        payload = {
            "name": "web",
            "active": True,
            "events": ["issue_comment"],
            "config": {
                "url": target_url,
                "content_type": "json",
                "secret": self.secret,
                "insecure_ssl": "0"
            }
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
                "User-Agent": "Hangar-V1-Webhook-Manager"
            }
        )
        
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            self.webhook_id = data.get("id")
            logger.info(f"Webhook registrado com sucesso no GitHub! ID={self.webhook_id}")
            self._save_state()
            return self.webhook_id

    def delete_github_webhook(self) -> bool:
        if not self.webhook_id:
            # Tentar carregar do estado
            st = self._load_state()
            self.webhook_id = st.get("webhook_id")
            
        if not self.webhook_id:
            logger.warning("Nenhum webhook_id registrado para deletar.")
            return False
            
        token = get_github_token()
        if not token:
            logger.error("GITHUB_TOKEN nao encontrado para deletar o webhook.")
            return False
            
        url = f"https://api.github.com/repos/{self.repo}/hooks/{self.webhook_id}"
        req = urllib.request.Request(
            url,
            method="DELETE",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Hangar-V1-Webhook-Manager"
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status in (204, 200):
                    logger.info(f"Webhook ID={self.webhook_id} deletado com sucesso do GitHub.")
                    self.webhook_id = None
                    self._save_state()
                    return True
        except Exception as exc:
            logger.error(f"Erro ao deletar webhook ID={self.webhook_id}: {exc}")
            return False
        return False

    def stop_tunnel(self):
        if self.process:
            logger.info("Encerrando processo cloudflared...")
            if self.process.stdout:
                try:
                    self.process.stdout.close()
                except Exception:
                    pass
            if self.process.stderr:
                try:
                    self.process.stderr.close()
                except Exception:
                    pass
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            logger.info("Processo cloudflared encerrado.")
            
        self.public_url = None
        self._save_state()

    def teardown(self):
        """Rollback completo e limpo."""
        logger.info("Executando teardown completo do tunel e webhook...")
        self.delete_github_webhook()
        self.stop_tunnel()
        if STATE_FILE.exists():
            try:
                STATE_FILE.unlink()
            except Exception:
                pass
        logger.info("Teardown concluido.")

    def _save_state(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps({
            "public_url": self.public_url,
            "webhook_id": self.webhook_id,
            "local_port": self.local_port,
            "repo": self.repo,
            "pid": self.process.pid if self.process else None,
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }, indent=2), "utf-8")

    def _load_state(self) -> dict:
        if STATE_FILE.exists():
            try:
                return json.loads(STATE_FILE.read_text("utf-8"))
            except Exception:
                pass
        return {}
