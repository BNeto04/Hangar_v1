#!/usr/bin/env python3
"""
test_tunnel_manager.py — Teste de integração do túnel local seguro Cloudflare Quick Tunnel.
Inicia o servidor webhook local, abre o túnel transitório e testa a requisição externa via HTTPS.
"""

import json
import threading
import time
import unittest
import urllib.request
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import bridge.github_webhook_server as gws
import bridge.tunnel_manager as tm

TEST_PORT = 8766

class TestTunnelManager(unittest.TestCase):
    def test_quick_tunnel_e2e_health(self):
        server = gws.create_server("127.0.0.1", TEST_PORT)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        time.sleep(0.5)

        mgr = tm.TunnelManager(local_port=TEST_PORT)
        try:
            url = mgr.start_tunnel(timeout=35)
            self.assertTrue(url.startswith("https://"))
            self.assertIn(".trycloudflare.com", url)
            print(f"\n[E2E] Tunel ativo em: {url}")

            # Testar requisição HTTPS externa passando pela Cloudflare até o localhost com retry para propagação de DNS
            health_url = f"{url}/health"
            print(f"[E2E] Testando GET {health_url} (aguardando propagacao DNS)...")
            data = None
            t0 = time.time()
            last_err = None
            while time.time() - t0 < 30:
                try:
                    req = urllib.request.Request(health_url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        if resp.status == 200:
                            data = json.loads(resp.read().decode("utf-8"))
                            break
                except Exception as exc:
                    last_err = exc
                    time.sleep(2)

            if data is None:
                raise RuntimeError(f"Falha na consulta externa apos 30s: {last_err}")

            self.assertEqual(data.get("status"), "healthy")
            print(f"[E2E] Sucesso! Resposta da nuvem: {data}")

        finally:
            mgr.stop_tunnel()
            server.shutdown()
            server.server_close()
            print("[E2E] Servidor e tunel encerrados com sucesso.")

if __name__ == "__main__":
    unittest.main()
