#!/usr/bin/env python3
"""
test_az000_bridge_ingestor.py — Suíte unitária do Ingestor e Selador Criptográfico AZ000.
Valida: Ingestão de CALLs da PR #1/Webhook, normalização, validação fail-closed,
selagem SHA-256 (SealedIntentContract), persistência em disco e envelope de handoff.
"""

import json
import os
import shutil
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from az000_governance.owner_intent.contracts import SealedIntentContract
from az000_governance.owner_intent.ingestor import (
    SEALED_CONTRACTS_DIR,
    ingest_and_seal_call,
    parse_raw_call_envelope,
)


class TestAZ000BridgeIngestor(unittest.TestCase):
    def setUp(self):
        self.test_contracts = []

    def tearDown(self):
        # Limpar contratos gerados pelos testes
        for cid in self.test_contracts:
            target = SEALED_CONTRACTS_DIR / f"{cid}.json"
            if target.exists():
                try:
                    target.unlink()
                except OSError:
                    pass

    def test_01_parse_raw_call_envelope(self):
        raw_text = """CG-000128
TYPE: CALL
TO: ANTIGRAVITY
CALL_ID: CALL-HANGAR-CONTINUOUS-FLOW-NEXT-CYCLE-001
FROM: CHATGPT
ACTION: CONTINUE_WITH_NEXT_USEFUL_TASK
DP_PROJECT: Hangar_v1
OWNER_DIRECTIVE: TRUE
DP_RULE: FAIL_CLOSED
"""
        parsed = parse_raw_call_envelope(raw_text)
        self.assertEqual(parsed["call_id"], "CALL-HANGAR-CONTINUOUS-FLOW-NEXT-CYCLE-001")
        self.assertEqual(parsed["owner_id"], "CHATGPT")
        self.assertEqual(parsed["action"], "CONTINUE_WITH_NEXT_USEFUL_TASK")
        self.assertEqual(parsed["scope"], "Hangar_v1")
        self.assertIn("OWNER_DIRECTIVE: TRUE", parsed["directives"])
        self.assertIn("DP_RULE: FAIL_CLOSED", parsed["directives"])

    def test_02_ingest_and_seal_valid_call(self):
        raw_text = """CG-000128
TYPE: CALL
TO: ANTIGRAVITY
CALL_ID: CALL-HANGAR-CONTINUOUS-FLOW-NEXT-CYCLE-001
FROM: CHATGPT
ACTION: CONTINUE_WITH_NEXT_USEFUL_TASK
DP_PROJECT: Hangar_v1
OWNER_DIRECTIVE: TRUE
"""
        res = ingest_and_seal_call(raw_text)
        self.assertEqual(res.get("status"), "SUCCESS")
        self.assertEqual(res.get("stage"), "HANDOFF_COMPLETED")
        self.assertEqual(res.get("validation", {}).get("verdict"), "ACCEPT")

        contract = res.get("sealed_contract")
        self.assertIsNotNone(contract)
        cid = contract.get("contract_id")
        self.test_contracts.append(cid)
        self.assertTrue(cid.startswith("CONTRACT-CALL-HANGAR-CONTINUOUS-FLOW-NEXT-CYCLE-001"))
        self.assertIsNotNone(contract.get("contract_sha256"))

        # Validar persistência no disco
        contract_file = Path(res.get("contract_file"))
        self.assertTrue(contract_file.exists())
        file_data = json.loads(contract_file.read_text("utf-8"))
        self.assertEqual(file_data["contract_id"], cid)
        self.assertEqual(file_data["contract_sha256"], contract["contract_sha256"])

        # Reconstruir dataclass e validar integridade criptográfica
        obj = SealedIntentContract(
            schema=file_data["schema"],
            contract_id=file_data["contract_id"],
            call_id=file_data["call_id"],
            owner_id=file_data["owner_id"],
            action=file_data["action"],
            scope=file_data["scope"],
            directives=file_data["directives"],
            mode=file_data["mode"],
            route=file_data["route"],
            created_at_iso=file_data["created_at_iso"],
            contract_sha256=file_data["contract_sha256"],
            validation_verdict=file_data["validation_verdict"],
        )
        self.assertTrue(obj.verify_integrity())

        # Validar envelope de handoff
        handoff = res.get("handoff_envelope")
        self.assertIsNotNone(handoff)
        self.assertIn("P-INTENT-HANDOFF-N01-01", handoff.get("source_port"))
        self.assertIn("P-PLAN-01", handoff.get("target_port"))

    def test_03_reject_missing_call_id(self):
        raw_text = """TYPE: CALL
TO: ANTIGRAVITY
ACTION: RUN_SOMETHING
DP_PROJECT: Hangar_v1
"""
        res = ingest_and_seal_call(raw_text)
        self.assertEqual(res.get("status"), "FAILED")
        self.assertEqual(res.get("stage"), "INGESTION")
        self.assertIn("CALL_ID", res.get("error", ""))

    def test_04_reject_unauthorized_owner(self):
        raw_text = """CALL_ID: CALL-HACKER-ATTEMPT-001
FROM: ROGUE_EXTERNAL_AGENT
ACTION: MUTATE_PRODUCTION
DP_PROJECT: Hangar_v1
"""
        res = ingest_and_seal_call(raw_text)
        self.assertEqual(res.get("status"), "BLOCKED")
        self.assertEqual(res.get("stage"), "VALIDATION")
        self.assertEqual(res.get("validation", {}).get("verdict"), "REJECT_UNAUTHORIZED")

    def test_05_hold_ambiguous_directive(self):
        raw_text = """CALL_ID: CALL-AMBIGUOUS-001
FROM: CHATGPT
ACTION: UPDATE_SOMETHING
DP_PROJECT: Hangar_v1
OWNER_DIRECTIVE: talvez se possível fazer deploy agora
"""
        res = ingest_and_seal_call(raw_text)
        self.assertEqual(res.get("status"), "BLOCKED")
        self.assertEqual(res.get("stage"), "VALIDATION")
        self.assertEqual(res.get("validation", {}).get("verdict"), "HOLD_INCONCLUSIVE")
        self.assertEqual(res.get("validation", {}).get("error_code"), "AMBIGUOUS_DIRECTIVE")
        self.assertIn("talvez", res.get("validation", {}).get("error_message", ""))

    def test_06_reject_unauthorized_scope(self):
        raw_text = """CALL_ID: CALL-UNAUTHORIZED-SCOPE-001
FROM: OWNER
ACTION: RUN_JOB
DP_PROJECT: external_third_party_repo
"""
        res = ingest_and_seal_call(raw_text)
        self.assertEqual(res.get("status"), "BLOCKED")
        self.assertEqual(res.get("stage"), "VALIDATION")
        self.assertEqual(res.get("validation", {}).get("verdict"), "REJECT_UNAUTHORIZED")
        self.assertEqual(res.get("validation", {}).get("error_code"), "OUT_OF_BOUNDS_SCOPE")
        self.assertIn("fora dos limites", res.get("validation", {}).get("error_message", ""))


if __name__ == "__main__":
    unittest.main()
