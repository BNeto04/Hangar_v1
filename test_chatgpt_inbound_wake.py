#!/usr/bin/env python3
"""
test_chatgpt_inbound_wake.py — Suíte de Testes da Análise de Gap Inbound ChatGPT.
"""

import unittest
import sqlite3
from pathlib import Path

class TestChatGPTInboundWake(unittest.TestCase):
    def setUp(self):
        self.hangar_dir = Path(r"C:\Users\PICHAU\Hangar_v1")
        self.db_path = Path(r"C:\Users\PICHAU\AppData\Local\hermes\kanban.db")
        self.doc_file = self.hangar_dir / "DOCS" / "15_CHATGPT_INBOUND_WAKE_ANALYSIS.md"

    def test_01_card_created_in_review(self):
        """Verifica se o card t_bridge_chatgpt_inbound_wake_01 foi criado em review (T4)."""
        self.assertTrue(self.db_path.exists())
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT status FROM tasks WHERE id = 't_bridge_chatgpt_inbound_wake_01'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "review", "Card deve estar em status review (T4)")

    def test_02_canonical_analysis_file_exists(self):
        """Verifica se a documentação canônica DOCS/15 existe e cobre a matriz de mecanismos."""
        self.assertTrue(self.doc_file.exists())
        content = self.doc_file.read_text(encoding="utf-8")
        self.assertIn("Matriz de Mecanismos Reais Disponíveis", content)
        self.assertIn("IMPLEMENTATION_GAP", content)
        self.assertIn("Chrome DevTools Protocol", content)

    def test_03_no_simulated_pass_invariant(self):
        """Valida que o resultado respeita o fail-closed e não inventa capacidade ativa sem porta CDP."""
        content = self.doc_file.read_text(encoding="utf-8")
        self.assertIn("BLOQUEIO FACTUAL ATUAL", content)
        self.assertIn("Fail-Closed", content)

if __name__ == "__main__":
    unittest.main()
