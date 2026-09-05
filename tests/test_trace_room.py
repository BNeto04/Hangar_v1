#!/usr/bin/env python3
"""
test_trace_room.py — Suíte de testes unitários para validação do cômodo TRACE (Tier 9).
Garante conformidade com ARCA (R-DOM-002, R-DOM-005, R-DOM-006) e DOCS/06_TRACE_SCHEMA.md.
Critérios: "06_TRACE_SCHEMA.md em conformidade", "Hashes SHA-256 verificáveis".
"""

import hashlib
import json
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from az000_governance.arca import (
    get_room_dependencies,
    get_room_order,
)
from az000_governance.trace import (
    CryptographicTraceEngine,
    SHA256_HEX_REGEX,
    TraceRecord,
    get_global_trace_engine,
)


class TestTraceRoom(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.ledger_file = os.path.join(self.temp_dir, "test_trace_ledger.jsonl")
        self.engine = CryptographicTraceEngine(ledger_path=self.ledger_file)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_arca_canonical_dependencies(self):
        """Valida se o cômodo TRACE está registrado na ARCA com dependências estritas."""
        rooms = get_room_order()
        trace_room = next((r for r in rooms if r.room_name == "TRACE"), None)
        self.assertIsNotNone(trace_room, "Cômodo TRACE deve existir na ARCA.")
        self.assertEqual(trace_room.tier, 9)
        self.assertIn("GOVERNANCE", trace_room.dependencies)
        self.assertIn("INTELLIGENCE", trace_room.dependencies)
        self.assertIn("EXTERNAL", trace_room.dependencies)
        self.assertIn("06_TRACE_SCHEMA.md em conformidade", trace_room.closure_criteria)
        self.assertIn("Hashes SHA-256 verificáveis", trace_room.closure_criteria)

    def test_02_trace_schema_compliance(self):
        """Valida conformidade estrutural com DOCS/06_TRACE_SCHEMA.md."""
        dummy_sha = hashlib.sha256(b"dummy_artifact").hexdigest()
        sec_sha = hashlib.sha256(b"security_ok").hexdigest()

        record = TraceRecord(
            trace_id="TRACE-HANGAR-V1-TEST-001",
            call_id="CALL-TEST-001",
            card_id="t_test_01",
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            route_taken="N01 -> N02 -> N03 -> N10 -> N09 -> N08 -> N05 -> N04 -> N06 -> N07",
            actors={
                "N01": {"actor": "CHAR-PLANNER-01", "port": "P-PLAN-01"},
                "N03": {"actor": "CHAR-EXECUTOR-01", "port": "P-EXECUTE-01", "status": "EXECUTED"},
                "N08": {"actor": "CHAR-VERIFIER-01", "port": "P-VERIFY-01", "verifier_sha256": dummy_sha},
            },
            evidence_digests={
                "artifact_sha256": dummy_sha,
                "security_sha256": sec_sha,
            },
            overall_verdict="COMPLIANT_PASS",
        )

        record.seal()
        self.assertTrue(SHA256_HEX_REGEX.match(record.trace_sha256))
        self.assertTrue(record.verify_integrity())

        as_dict = record.to_dict()
        required_keys = [
            "trace_id", "call_id", "card_id", "timestamp_iso",
            "route_taken", "actors", "evidence_digests", "overall_verdict",
            "parent_trace_hash", "trace_sha256"
        ]
        for k in required_keys:
            self.assertIn(k, as_dict)

    def test_03_append_only_cryptographic_chain(self):
        """Valida encadeamento contínuo de blocos com SHA-256 no ledger append-only."""
        sha_a = hashlib.sha256(b"ev_a").hexdigest()
        sha_b = hashlib.sha256(b"ev_b").hexdigest()

        t1 = TraceRecord(
            trace_id="TRACE-001",
            call_id="CALL-001",
            card_id="CARD-001",
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            route_taken="N01 -> N03 -> N08",
            actors={"N01": "PLANNER"},
            evidence_digests={"ev_a": sha_a},
            overall_verdict="COMPLIANT_PASS",
        )
        rec1 = self.engine.record_trace(t1)
        self.assertEqual(rec1.parent_trace_hash, CryptographicTraceEngine.GENESIS_HASH)

        t2 = TraceRecord(
            trace_id="TRACE-002",
            call_id="CALL-002",
            card_id="CARD-002",
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            route_taken="N01 -> N03 -> N08",
            actors={"N01": "PLANNER"},
            evidence_digests={"ev_b": sha_b},
            overall_verdict="COMPLIANT_PASS",
        )
        rec2 = self.engine.record_trace(t2)
        self.assertEqual(rec2.parent_trace_hash, rec1.trace_sha256)

        # Verificar integridade da cadeia
        ok, msg = self.engine.verify_chain()
        self.assertTrue(ok)
        self.assertIn("CHAIN_VERIFIED_OK", msg)

    def test_04_fail_closed_on_corrupted_digest_or_tampered_trace(self):
        """R-DOM-002: FAIL_CLOSED em digests corrompidos ou adulteração de registros."""
        # 1. Digest inválido deve lançar ValueError imediatamente
        t_invalid = TraceRecord(
            trace_id="TRACE-BAD-001",
            call_id="CALL-BAD",
            card_id="CARD-BAD",
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            route_taken="N01",
            actors={},
            evidence_digests={"bad_digest": "not_a_64_hex_hash"},
            overall_verdict="HOLD_BLOCKED",
        )
        with self.assertRaises(ValueError):
            self.engine.record_trace(t_invalid)

        # 2. Adulteração retroativa de trace deve quebrar verify_chain
        sha_valid = hashlib.sha256(b"ok").hexdigest()
        t_valid = TraceRecord(
            trace_id="TRACE-GOOD-001",
            call_id="CALL-GOOD",
            card_id="CARD-GOOD",
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            route_taken="N01",
            actors={},
            evidence_digests={"valid": sha_valid},
            overall_verdict="COMPLIANT_PASS",
        )
        self.engine.record_trace(t_valid)

        # Adulterar em memória
        self.engine._chain[0].overall_verdict = "TAMPERED_VERDICT"
        ok, msg = self.engine.verify_chain()
        self.assertFalse(ok)
        self.assertIn("FAIL_CLOSED", msg)

    def test_05_upstream_dependencies_complete_in_kanban(self):
        """Valida que todos os cômodos a montante (Tier 1 a 8) estão concluídos no Hermes."""
        db_path = Path(r"C:\Users\PICHAU\AppData\Local\hermes\kanban.db")
        self.assertTrue(db_path.exists())
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        tasks_to_check = [
            "t_hangar_az000_intent_seal_ingestion_01",
            "t_hangar_world_room_completion_01",
            "t_hangar_plant_room_completion_01",
            "t_hangar_ports_room_completion_01",
            "t_hangar_capabilities_room_completion_01",
            "t_hangar_machines_room_completion_01",
            "t_hangar_intelligence_room_completion_01",
            "t_hangar_external_room_completion_01",
        ]

        for tid in tasks_to_check:
            cur.execute("SELECT id, status FROM tasks WHERE id = ?", (tid,))
            row = cur.fetchone()
            self.assertIsNotNone(row, f"Card '{tid}' deve existir no Hermes Kanban.")
            self.assertEqual(row[1], "done", f"Card '{tid}' deve estar 'done'.")

        conn.close()

    def test_06_next_eligible_room_in_order(self):
        """Valida que o próximo cômodo na ordem linear da ARCA é COCKPITS (Tier 10)."""
        rooms = get_room_order()
        trace_idx = next(i for i, r in enumerate(rooms) if r.room_name == "TRACE")
        self.assertEqual(trace_idx, 8)  # Nono cômodo (Tier 9)

        next_room = rooms[trace_idx + 1]
        self.assertEqual(next_room.room_name, "COCKPITS", "O próximo cômodo na ordem deve ser COCKPITS.")
        self.assertEqual(next_room.tier, 10)


if __name__ == "__main__":
    unittest.main()
