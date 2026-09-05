#!/usr/bin/env python3
"""
test_policy_engines.py — Suíte de testes unitários dos Motores Formais de Política (Cedar e OPA).
Garante conformidade com Critério 2 do Roadtrace (DOCS/09_HANGAR_GOVERNANCE_ROADTRACE.md)
e Invariantes ARCA (R-DOM-001, R-DOM-002, R-DOM-006, R-DOM-007).
"""

import hashlib
import unittest
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from az000_governance.policy import (
    CedarAuthorityEngine,
    CedarDecision,
    CedarEffect,
    CedarEntity,
    CedarPolicy,
    OpaGateVerdict,
    OpaQualityGateEngine,
    QualityGateEvaluation,
)


class TestPolicyEngines(unittest.TestCase):

    def setUp(self):
        self.cedar = CedarAuthorityEngine()
        self.opa = OpaQualityGateEngine()

    def test_01_cedar_owner_sovereign_permit(self):
        """R-DOM-001: Soberania do Proprietário confere PERMIT irrestrito."""
        owner = CedarEntity(entity_type="User", entity_id="PROPRIETARIO")
        res = CedarEntity(entity_type="Room", entity_id="GOVERNANCE")
        
        decision, reason = self.cedar.evaluate(owner, 'Action::"PUBLISH_RELEASE"', res)
        self.assertEqual(decision, CedarDecision.PERMIT)
        self.assertIn("policy-sovereign-owner-all", reason)

    def test_02_cedar_executor_mutate_code_permit(self):
        """Executor N03 detém PERMIT para mutações físicas autorizadas."""
        executor = CedarEntity(entity_type="Agent", entity_id="CHAR-EXECUTOR-01")
        artifact = CedarEntity(entity_type="Artifact", entity_id="code_file.py")

        decision, reason = self.cedar.evaluate(executor, 'Action::"MUTATE_CODE"', artifact)
        self.assertEqual(decision, CedarDecision.PERMIT)
        self.assertIn("policy-executor-write-code", reason)

    def test_03_cedar_lens_read_only_forbid_fail_closed(self):
        """Lentes são isoladas em modo read-only; tentativa de mutação dispara FORBID estrito."""
        # 1. Tentativa de mutação por lente de segurança -> FORBID
        security = CedarEntity(entity_type="Agent", entity_id="CHAR-SECURITY-01")
        artifact = CedarEntity(entity_type="Artifact", entity_id="code_file.py")
        decision, reason = self.cedar.evaluate(security, 'Action::"MUTATE_CODE"', artifact)
        self.assertEqual(decision, CedarDecision.FORBID)
        self.assertIn("FAIL_CLOSED", reason)
        self.assertIn("policy-forbid-write-char-security-01", reason)

        # 2. Agente desconhecido -> Default Deny (FAIL_CLOSED)
        unknown = CedarEntity(entity_type="Agent", entity_id="ROGUE-BOT-01")
        decision2, reason2 = self.cedar.evaluate(unknown, 'Action::"ANY_ACTION"', artifact)
        self.assertEqual(decision2, CedarDecision.FORBID)
        self.assertIn("Default Deny", reason2)

    def test_04_opa_gate_allow_valid_evidence(self):
        """R-DOM-007: OPA delibera ALLOW quando evidências N08/N06 são íntegras e completas."""
        sha_art = hashlib.sha256(b"code_artifact").hexdigest()
        sha_sec = hashlib.sha256(b"security_ok").hexdigest()

        gate_input = {
            "verifier_status": "VERIFICATION_PASSED",
            "security_status": "SECURITY_PASS",
            "evidence_digests": {
                "artifact_sha256": sha_art,
                "security_sha256": sha_sec,
            },
            "blocking_reasons": []
        }

        eval_res = self.opa.evaluate_gate(gate_input)
        self.assertEqual(eval_res.verdict, OpaGateVerdict.ALLOW)
        self.assertTrue(eval_res.allowed)
        self.assertEqual(len(eval_res.violations), 0)

    def test_05_opa_gate_hold_on_missing_or_corrupted_evidence(self):
        """R-DOM-002: OPA trava em HOLD fail-closed se qualquer evidência falhar ou divergir."""
        sha_art = hashlib.sha256(b"code_artifact").hexdigest()

        # 1. Verifier falhou
        input_failed_verifier = {
            "verifier_status": "VERIFICATION_FAILED",
            "security_status": "SECURITY_PASS",
            "evidence_digests": {"artifact_sha256": sha_art},
            "blocking_reasons": []
        }
        res1 = self.opa.evaluate_gate(input_failed_verifier)
        self.assertEqual(res1.verdict, OpaGateVerdict.HOLD)
        self.assertFalse(res1.allowed)
        self.assertTrue(any("OPA_REGO_RULE_01_FAIL" in v for v in res1.violations))

        # 2. Hash SHA-256 corrompido
        input_bad_hash = {
            "verifier_status": "VERIFICATION_PASSED",
            "security_status": "SECURITY_PASS",
            "evidence_digests": {"artifact_sha256": "corrupted_non_hex_short_hash"},
            "blocking_reasons": []
        }
        res2 = self.opa.evaluate_gate(input_bad_hash)
        self.assertEqual(res2.verdict, OpaGateVerdict.HOLD)
        self.assertFalse(res2.allowed)
        self.assertTrue(any("OPA_REGO_RULE_03_FAIL" in v for v in res2.violations))

        # 3. Presença de razões impeditivas
        input_blocking = {
            "verifier_status": "VERIFICATION_PASSED",
            "security_status": "SECURITY_PASS",
            "evidence_digests": {"artifact_sha256": sha_art},
            "blocking_reasons": ["CRITICAL_SECURITY_VULNERABILITY"]
        }
        res3 = self.opa.evaluate_gate(input_blocking)
        self.assertEqual(res3.verdict, OpaGateVerdict.HOLD)
        self.assertFalse(res3.allowed)
        self.assertTrue(any("OPA_REGO_RULE_04_FAIL" in v for v in res3.violations))

    def test_06_governance_roadtrace_criterion_2_compliance(self):
        """Garante que ambos os motores estão ativos, em conformidade e sem dependência de rede."""
        # Cedar engine possui políticas carregadas
        self.assertGreaterEqual(len(self.cedar._policies), 3)

        # OPA engine opera localmente e devolve verdicts tipados
        empty_eval = self.opa.evaluate_gate({})
        self.assertEqual(empty_eval.verdict, OpaGateVerdict.HOLD)


if __name__ == "__main__":
    unittest.main()
