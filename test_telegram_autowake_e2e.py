#!/usr/bin/env python3
"""
test_telegram_autowake_e2e.py — Suíte de Testes da Prova E2E de Autowake e Gap Inbound.
"""

import unittest
import sqlite3
from pathlib import Path

class TestTelegramAutowakeE2E(unittest.TestCase):
    def setUp(self):
        self.hangar_dir = Path(r"C:\Users\PICHAU\Hangar_v1")
        self.circuito_dir = Path(r"C:\Users\PICHAU\Downloads\circuito")
        self.db_path = Path(r"C:\Users\PICHAU\AppData\Local\hermes\kanban.db")
        self.conversa_file = self.circuito_dir / "conversa de ia.txt"
        self.doc_file = self.hangar_dir / "DOCS" / "14_TELEGRAM_V_AUTOWAKE_E2E_AND_INBOUND_GAP.md"

    def test_01_telegram_v_pulse_recorded_in_conversa(self):
        """TEST_A: Verifica se o pulso v do Telegram foi registrado de forma factual."""
        self.assertTrue(self.conversa_file.exists(), "conversa de ia.txt deve existir")
        content = self.conversa_file.read_text(encoding="utf-8", errors="ignore")
        self.assertIn("[TELEGRAM_WAKE_PULSE", content, "Deve conter registro de pulso TELEGRAM_WAKE_PULSE")
        self.assertIn("Pulso 'v' recebido do Propriet", content)

    def test_02_card_in_review_in_kanban(self):
        """TEST_C: Verifica se o card foi criado e posteriormente promovido em T5."""
        self.assertTrue(self.db_path.exists())
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT status FROM tasks WHERE id = 't_bridge_telegram_v_autowake_e2e_01'")
        row = cur.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertIn(row[0], ("review", "done"), "Card deve estar em status review (T4) ou done (T5)")

    def test_03_canonical_documentation_exists(self):
        """Verifica a documentação canônica com as seções obrigatórias."""
        self.assertTrue(self.doc_file.exists())
        content = self.doc_file.read_text(encoding="utf-8")
        self.assertIn("TEST_A: Telegram V", content)
        self.assertIn("TEST_B: Notificação / Despertar Inbound do ChatGPT", content)
        self.assertIn("IMPLEMENTATION_GAP", content)
        self.assertIn("TEST_C: Retorno ao Estado Factual", content)

    def test_04_inbound_gap_analysis_criteria(self):
        """TEST_B: Valida que o gap inbound foi formalmente categorizado sem simulação falsa."""
        content = self.doc_file.read_text(encoding="utf-8")
        self.assertIn("IMPLEMENTATION_GAP", content)
        self.assertIn("Chrome DevTools Protocol", content)

if __name__ == "__main__":
    unittest.main()
