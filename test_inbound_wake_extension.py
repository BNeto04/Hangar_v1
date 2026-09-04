#!/usr/bin/env python3
"""
test_inbound_wake_extension.py — Suíte de Testes da Extensão Manifest V3 Inbound Wake.
"""

import unittest
import json
import sqlite3
from pathlib import Path

class TestInboundWakeExtension(unittest.TestCase):
    def setUp(self):
        self.hangar_dir = Path(r"C:\Users\PICHAU\Hangar_v1")
        self.ext_dir = self.hangar_dir / "bridge" / "extension"
        self.db_path = Path(r"C:\Users\PICHAU\AppData\Local\hermes\kanban.db")
        self.docs_path = self.hangar_dir / "DOCS" / "16_CHATGPT_INBOUND_WAKE_EXTENSION.md"

    def test_01_card_in_review(self):
        """Verifica se o card t_bridge_inbound_wake_extension_01 existe e está em review (T4)."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT status FROM tasks WHERE id = 't_bridge_inbound_wake_extension_01'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "review", "Card deve estar em status review (T4)")

    def test_02_manifest_v3_structure(self):
        """Valida que o manifest.json segue rigorosamente o padrão Manifest V3."""
        manifest_file = self.ext_dir / "manifest.json"
        self.assertTrue(manifest_file.exists())
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
        self.assertEqual(data.get("manifest_version"), 3)
        self.assertIn("https://chatgpt.com/*", data.get("host_permissions", []))
        self.assertIn("http://127.0.0.1:8765/*", data.get("host_permissions", []))

    def test_03_content_script_dedupe_logic(self):
        """Valida a presença de lógica de dedupe e anti-loop no content.js."""
        content_file = self.ext_dir / "content.js"
        self.assertTrue(content_file.exists())
        text = content_file.read_text(encoding="utf-8")
        self.assertIn("lastProcessedMessageId", text)
        self.assertIn("sessionStorage", text)
        self.assertIn("injectWakeMessage", text)

    def test_04_planner_decision_and_stop_rule_documented(self):
        """Valida que a decisão do Planner (EXTENSION) e a regra de parada em T4 estão documentadas."""
        self.assertTrue(self.docs_path.exists())
        content = self.docs_path.read_text(encoding="utf-8")
        self.assertIn("Decisão do Planner: EXTENSION vs CDP/Playwright", content)
        self.assertIn("ESCOLHIDA (MENOR IMPLEMENTAÇÃO FACTUAL)", content)
        self.assertIn("STOP em T4/Review", content)

if __name__ == "__main__":
    unittest.main()
