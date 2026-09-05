#!/usr/bin/env python3
"""
tests/test_bridge_v2_cleanroom.py — Testes Automatizados da Ponte Clean-Room V2.
Porta P-EXT-BRIDGE-V2-01 / SPRINT-BRIDGE-V2-CLEANROOM-001
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from bridge_v2.daily_journal import DailyCircuitJournal
from bridge_v2.schema import (
    compute_sha256,
    format_context_packet,
    format_owner_event,
    format_result_envelope,
    normalize_call_envelope,
)
from bridge_v2.state_manager import CleanroomStateManager


class TestBridgeV2Cleanroom(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_full_envelope_parsing(self):
        raw = """MESSAGE_ID: CG-000146
TIMESTAMP: 2026-09-05T08:00:00-03:00
FROM: CHATGPT
TO: ANTIGRAVITY
TYPE: CALL
REPLY_TO: CG-000145

BODY:
CALL_ID: CALL-TEST-001
SPRINT_ID: SPRINT-TEST-001
PRIORITY: P0
ACTION: EXECUTE_TEST
"""
        env = normalize_call_envelope(raw, comment_id=12345)
        self.assertIsNotNone(env)
        self.assertEqual(env["message_id"], "CG-000146")
        self.assertEqual(env["from"], "CHATGPT")
        self.assertEqual(env["to"], "ANTIGRAVITY")
        self.assertEqual(env["type"], "CALL")
        self.assertEqual(env["call_id"], "CALL-TEST-001")
        self.assertEqual(env["sprint_id"], "SPRINT-TEST-001")
        self.assertEqual(env["raw_format"], "FULL_ENVELOPE")
        self.assertEqual(env["github_comment_id"], 12345)

    def test_02_compact_envelope_parsing(self):
        raw = """CG-000148
TYPE: CALL
TO: ANTIGRAVITY
CALL_ID: CALL-BRIDGE-V2-CLEANROOM-BUILD-001
SPRINT_ID: SPRINT-BRIDGE-V2-CLEANROOM-001
PRIORITY: P0
ACTION: PLAN_CREATE_CARD_AND_BUILD_NEW_BRIDGE_CLEANROOM

SOVEREIGN SPRINT OBJECTIVE:
Construir uma NOVA ponte Hangar V1 em clean-room.
"""
        env = normalize_call_envelope(raw, comment_id=54321)
        self.assertIsNotNone(env)
        self.assertEqual(env["message_id"], "CG-000148")
        self.assertEqual(env["from"], "CHATGPT")
        self.assertEqual(env["to"], "ANTIGRAVITY")
        self.assertEqual(env["call_id"], "CALL-BRIDGE-V2-CLEANROOM-BUILD-001")
        self.assertEqual(env["sprint_id"], "SPRINT-BRIDGE-V2-CLEANROOM-001")
        self.assertEqual(env["raw_format"], "COMPACT_CHATGPT")
        self.assertIn("Construir uma NOVA ponte", env["body"])

    def test_03_malformed_envelope_fail_closed(self):
        raw = "Mensagem aleatória sem cabeçalhos nem CG-id"
        env = normalize_call_envelope(raw)
        self.assertIsNone(env)

    def test_04_context_packet_formatting_and_size(self):
        packet = format_context_packet(
            sprint_id="SPRINT-TEST-001",
            owner_objective="Construir a ponte V2 com qualidade máxima.",
            done_criteria="Zero legacy, webhook primário, dedupe global.",
            out_of_scope="Obsidian/Canvas.",
            last_call_id="CALL-001",
            last_message_id="CG-000148",
            github_comment_id=99999,
            result_status="SUCCESS",
            result_summary="Ponte construída e testada.",
            current_state="WAITING_NEXT_STEP",
        )
        self.assertIn("SPRINT_ID: SPRINT-TEST-001", packet)
        self.assertIn("LATEST_RESULT_STATUS: SUCCESS", packet)
        self.assertIn("NEXT_GPT_ACTION:", packet)
        self.assertLessEqual(len(packet.encode("utf-8")), 4000)

    def test_05_daily_journal_jsonl_and_markdown(self):
        journal = DailyCircuitJournal(target_dir=self.test_dir)
        date_str = "2026-09-05"

        ev1 = journal.record_event(
            event_type="CALL_RECEIVED",
            actor_from="CHATGPT",
            actor_to="ANTIGRAVITY",
            channel="GITHUB_PR1",
            summary="Chamada CG-000148 recebida via Webhook",
            message_id="CG-000148",
            call_id="CALL-001",
            date_str=date_str,
        )
        self.assertIsNotNone(ev1)

        # Provar deduplicação
        ev2 = journal.record_event(
            event_type="CALL_RECEIVED",
            actor_from="CHATGPT",
            actor_to="ANTIGRAVITY",
            channel="GITHUB_PR1",
            summary="Chamada CG-000148 recebida via Webhook",
            message_id="CG-000148",
            call_id="CALL-001",
            date_str=date_str,
        )
        self.assertIsNone(ev2)  # Deve ignorar duplicata

        # Adicionar segundo evento (RESULT)
        journal.record_event(
            event_type="RESULT_PUBLISHED",
            actor_from="ANTIGRAVITY",
            actor_to="CHATGPT",
            channel="GITHUB_PR1",
            summary="Laudo AG-RES-000144 publicado",
            message_id="AG-RES-000144",
            date_str=date_str,
        )

        jsonl_file = self.test_dir / f"{date_str}.jsonl"
        md_file = self.test_dir / f"{date_str}.md"

        self.assertTrue(jsonl_file.exists())
        self.assertTrue(md_file.exists())

        lines = [ln for ln in jsonl_file.read_text("utf-8").splitlines() if ln.strip()]
        self.assertEqual(len(lines), 2)

        md_text = md_file.read_text("utf-8")
        self.assertIn("CIRCUITO DIÁRIO OPERACIONAL — 2026-09-05", md_text)
        self.assertIn("Chamada CG-000148", md_text)
        self.assertIn("Laudo AG-RES-000144", md_text)

    def test_06_state_manager_deduplication(self):
        mgr = CleanroomStateManager(runtime_dir=self.test_dir)
        test_cid = 8888881
        test_deliv = "deliv-test-uuid"
        test_mid = "CG-TEST-UNIQUE-01"

        self.assertFalse(mgr.is_duplicate(comment_id=test_cid, delivery_id=test_deliv, message_id=test_mid))
        mgr.mark_processed(comment_id=test_cid, delivery_id=test_deliv, message_id=test_mid)
        self.assertTrue(mgr.is_duplicate(comment_id=test_cid))
        self.assertTrue(mgr.is_duplicate(delivery_id=test_deliv))
        self.assertTrue(mgr.is_duplicate(message_id=test_mid))


if __name__ == "__main__":
    unittest.main()
