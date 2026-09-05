#!/usr/bin/env python3
"""
tests/test_bridge_v2_e2e.py — Suíte de Provas Reais E2E da Ponte Clean-Room V2.
Valida os critérios de aceitação de CG-000148 e CG-000149.
"""

import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path

from bridge_v2.daily_journal import DailyCircuitJournal
from bridge_v2.owner_telemetry import OwnerTelemetryManager
from bridge_v2.schema import (
    format_context_packet,
    format_owner_event,
    format_result_envelope,
    normalize_call_envelope,
)
from bridge_v2.state_manager import CleanroomStateManager


class TestBridgeV2E2E(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.state_mgr = CleanroomStateManager(runtime_dir=self.test_dir)
        self.journal = DailyCircuitJournal(target_dir=self.test_dir / "circuito_diario")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_e2e_01_call_ingestion_and_daily_journal_single_entry(self):
        """TEST 1 & TEST_A: Processamento de CALL e comprovação de entrada única no JSONL e MD."""
        raw_call = """CG-000148
TYPE: CALL
TO: ANTIGRAVITY
CALL_ID: CALL-BRIDGE-V2-CLEANROOM-BUILD-001
SPRINT_ID: SPRINT-BRIDGE-V2-CLEANROOM-001
PRIORITY: P0
ACTION: PLAN_CREATE_CARD_AND_BUILD_NEW_BRIDGE_CLEANROOM

SOVEREIGN SPRINT OBJECTIVE:
Construir uma NOVA ponte Hangar V1 em clean-room, sem poluicao operacional por nenhum legado anterior.
"""
        env = normalize_call_envelope(raw_call, comment_id=5551717892)
        self.assertIsNotNone(env)

        # 1. Ingestão na rota primária (Webhook)
        inbox_file = self.state_mgr.deliver_to_inbox(env["body"], env["message_id"], env["call_id"])
        self.state_mgr.mark_processed(comment_id=env["github_comment_id"], message_id=env["message_id"], call_id=env["call_id"])

        ev = self.journal.record_event(
            event_type="CALL_RECEIVED",
            actor_from=env["from"],
            actor_to=env["to"],
            channel="GITHUB_PR1",
            summary=f"CALL recebida: {env['message_id']} ({env['call_id']})",
            sprint_id=env["sprint_id"],
            message_id=env["message_id"],
            call_id=env["call_id"],
            github_comment_id=env["github_comment_id"],
        )
        self.assertIsNotNone(ev)

        # Verificar integridade no arquivo
        today = self.journal.journal_dir / f"{ev['date_local']}.jsonl"
        md_file = self.journal.journal_dir / f"{ev['date_local']}.md"
        self.assertTrue(today.exists())
        self.assertTrue(md_file.exists())

        lines = [ln for ln in today.read_text("utf-8").splitlines() if ln.strip()]
        self.assertEqual(len(lines), 1)
        self.assertIn("CALL-BRIDGE-V2-CLEANROOM-BUILD-001", lines[0])

    def test_e2e_02_duplicate_webhook_and_fallback_polling_dedupe(self):
        """TEST 5 & TEST_E: Webhook duplicado + fallback polling gera exatamente 1 evento lógico."""
        cid = 5551717892
        mid = "CG-000148"
        call_id = "CALL-BRIDGE-V2-CLEANROOM-BUILD-001"

        # Webhook processa primeiro
        self.assertFalse(self.state_mgr.is_duplicate(comment_id=cid, message_id=mid, call_id=call_id))
        self.state_mgr.mark_processed(comment_id=cid, message_id=mid, call_id=call_id)
        ev1 = self.journal.record_event(
            event_type="CALL_RECEIVED",
            actor_from="CHATGPT",
            actor_to="ANTIGRAVITY",
            channel="GITHUB_PR1",
            summary=f"CALL {mid}",
            message_id=mid,
            call_id=call_id,
            github_comment_id=cid,
        )
        self.assertIsNotNone(ev1)

        # Fallback polling tenta processar logo em seguida
        self.assertTrue(self.state_mgr.is_duplicate(comment_id=cid, message_id=mid, call_id=call_id))
        # Polling detecta duplicate e não chama record_event nem deliver_to_inbox!

        # Se webhook tentar novamente com o mesmo evento:
        ev2 = self.journal.record_event(
            event_type="CALL_RECEIVED",
            actor_from="CHATGPT",
            actor_to="ANTIGRAVITY",
            channel="GITHUB_PR1",
            summary=f"CALL {mid}",
            message_id=mid,
            call_id=call_id,
            github_comment_id=cid,
        )
        self.assertIsNone(ev2)  # Diário bloqueia duplicata

        today_jsonl = self.journal.journal_dir / f"{ev1['date_local']}.jsonl"
        lines = [ln for ln in today_jsonl.read_text("utf-8").splitlines() if ln.strip()]
        self.assertEqual(len(lines), 1, "Deve conter exatamente uma única linha!")

    def test_e2e_03_result_publishing_and_context_packet_generation(self):
        """TEST 2 & TEST_B: Antigravity publica RESULT e gera CONTEXT_PACKET para o ChatGPT."""
        result_text = format_result_envelope(
            message_id="AG-RES-000148",
            reply_to="CG-000148",
            status="COMPLETED",
            body="Construção da ponte V2 clean-room concluída e validada.",
            sprint_id="SPRINT-BRIDGE-V2-CLEANROOM-001",
            call_id="CALL-BRIDGE-V2-CLEANROOM-BUILD-001",
        )
        self.assertIn("MESSAGE_ID: AG-RES-000148", result_text)
        self.assertIn("TYPE: RESULT", result_text)

        # Gravar outbox
        outbox_file = self.state_mgr.deliver_to_outbox(result_text, status="COMPLETED", summary="Ponte V2 concluída.")
        self.assertTrue(outbox_file.exists())

        # Gerar CONTEXT_PACKET
        packet = format_context_packet(
            sprint_id="SPRINT-BRIDGE-V2-CLEANROOM-001",
            owner_objective="Construir a nova ponte V2.",
            done_criteria="Zero legacy, webhook primário.",
            out_of_scope="Obsidian.",
            last_call_id="CALL-BRIDGE-V2-CLEANROOM-BUILD-001",
            last_message_id="CG-000148",
            github_comment_id=5551717892,
            result_status="COMPLETED",
            result_summary="Ponte V2 construída com sucesso.",
            current_state="RESULT_DELIVERED",
        )
        self.assertIn("SPRINT_ID: SPRINT-BRIDGE-V2-CLEANROOM-001", packet)
        self.assertIn("LATEST_RESULT_STATUS: COMPLETED", packet)
        self.assertLessEqual(len(packet.encode("utf-8")), 4000)

        # Registro no diário
        ev = self.journal.record_event(
            event_type="RESULT_PUBLISHED",
            actor_from="ANTIGRAVITY",
            actor_to="CHATGPT",
            channel="GITHUB_PR1",
            summary="Laudo AG-RES-000148 publicado com sucesso.",
            message_id="AG-RES-000148",
            call_id="CALL-BRIDGE-V2-CLEANROOM-BUILD-001",
            reply_to="CG-000148",
            status="COMPLETED",
        )
        self.assertIsNotNone(ev)

    def test_e2e_04_human_interventions_telegram_and_antigravity(self):
        """TEST 3, 4, TEST_G, TEST_H: Intervenções humanas via Telegram e Antigravity registradas."""
        # 1. Intervenção via Telegram
        ev_tg = self.journal.record_event(
            event_type="OWNER_DIRECTIVE",
            actor_from="OWNER",
            actor_to="ANTIGRAVITY",
            channel="TELEGRAM",
            summary="Proprietário enviou diretiva: 'priorize os testes E2E antes do cutover'",
            sprint_id="SPRINT-BRIDGE-V2-CLEANROOM-001",
            human_intervention=True,
        )
        self.assertIsNotNone(ev_tg)
        self.assertTrue(ev_tg["human_intervention"])
        self.assertEqual(ev_tg["channel"], "TELEGRAM")

        # 2. Intervenção direta no Antigravity
        ev_ag = self.journal.record_event(
            event_type="OWNER_DIRECTIVE",
            actor_from="OWNER",
            actor_to="ANTIGRAVITY",
            channel="ANTIGRAVITY",
            summary="Proprietário ordenou localmente: 'vá'",
            sprint_id="SPRINT-BRIDGE-V2-CLEANROOM-001",
            human_intervention=True,
        )
        self.assertIsNotNone(ev_ag)
        self.assertTrue(ev_ag["human_intervention"])
        self.assertEqual(ev_ag["channel"], "ANTIGRAVITY")

        # Verificar se ambas constam no Markdown humano na seção "Intervenções Humanas"
        md_file = self.journal.journal_dir / f"{ev_ag['date_local']}.md"
        md_content = md_file.read_text("utf-8")
        self.assertIn("## 5. Intervenções Humanas", md_content)
        self.assertIn("via `TELEGRAM`: Proprietário enviou diretiva", md_content)
        self.assertIn("via `ANTIGRAVITY`: Proprietário ordenou localmente", md_content)

    def test_e2e_05_restart_safe_without_replaying_old_events(self):
        """TEST 6 & TEST_D: Reinício de processo preserva journal e não repete eventos antigos."""
        date_str = "2026-09-05"
        ev = self.journal.record_event(
            event_type="TASK_STARTED",
            actor_from="ANTIGRAVITY",
            actor_to="SISTEMA",
            channel="KANBAN",
            summary="Tarefa iniciada: t_bridge_v2_cleanroom_sprint_01",
            task_id="t_bridge_v2_cleanroom_sprint_01",
            date_str=date_str,
        )
        self.assertIsNotNone(ev)

        # Simular reinício completo recriando a instância DailyCircuitJournal e CleanroomStateManager
        new_journal = DailyCircuitJournal(target_dir=self.test_dir / "circuito_diario")
        new_state_mgr = CleanroomStateManager(runtime_dir=self.test_dir)

        # Tentar reprocessar o mesmo evento
        dup = new_journal.record_event(
            event_type="TASK_STARTED",
            actor_from="ANTIGRAVITY",
            actor_to="SISTEMA",
            channel="KANBAN",
            summary="Tarefa iniciada: t_bridge_v2_cleanroom_sprint_01",
            task_id="t_bridge_v2_cleanroom_sprint_01",
            date_str=date_str,
        )
        self.assertIsNone(dup, "Evento pós-restart não pode ser duplicado no diário!")

        lines = (self.test_dir / "circuito_diario" / f"{date_str}.jsonl").read_text("utf-8").splitlines()
        self.assertEqual(len([l for l in lines if l.strip()]), 1)


if __name__ == "__main__":
    unittest.main()
