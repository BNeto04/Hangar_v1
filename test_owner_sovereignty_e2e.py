import unittest
import sys
from pathlib import Path

# Add bridge to path
bridge_dir = Path(__file__).resolve().parent / "bridge"
if str(bridge_dir) not in sys.path:
    sys.path.insert(0, str(bridge_dir))

from owner_sovereignty import evaluate_precedence, REAL_POWERS_MATRIX

class TestOwnerSovereigntyE2E(unittest.TestCase):
    def test_01_owner_precedence_over_pending_audit_pass(self):
        """Prova que a diretiva do Owner tem precedência sobre auditoria pendente sem causar silêncio."""
        res = evaluate_precedence(
            sender_id="OWNER",
            directive_type="OWNER_DIRECTIVE",
            action="CHECK_STATUS_OR_RUN",
            pending_audit=True,
            safety_violation=False,
            scope_violation=False
        )
        self.assertEqual(res["decision"], "EXECUTE_IMMEDIATELY_PREEMPT_AUDIT")
        self.assertTrue(res["action_allowed"])
        self.assertIn("sem causar silêncio", res["anti_silence_response"])

    def test_02_owner_directive_factual_safety_blocker_hold(self):
        """Prova que violação de segurança é reportada como bloqueio factual sem silenciar o Owner."""
        res = evaluate_precedence(
            sender_id="OWNER",
            directive_type="OWNER_DIRECTIVE",
            action="DELETE_DATABASE",
            pending_audit=False,
            safety_violation=True,
            scope_violation=False
        )
        self.assertEqual(res["decision"], "REPORT_FACTUAL_BLOCKER")
        self.assertEqual(res["blocker_type"], "SAFETY_VIOLATION")
        self.assertFalse(res["action_allowed"])
        self.assertIn("segurança", res["anti_silence_response"])

    def test_03_owner_directive_scope_blocker_hold(self):
        """Prova que violação de escopo é reportada como bloqueio factual imediato."""
        res = evaluate_precedence(
            sender_id="OWNER",
            directive_type="OWNER_DIRECTIVE",
            action="MUTATE_EXTERNAL_PROJECT",
            pending_audit=False,
            safety_violation=False,
            scope_violation=True
        )
        self.assertEqual(res["decision"], "REPORT_FACTUAL_BLOCKER")
        self.assertEqual(res["blocker_type"], "SCOPE_VIOLATION")
        self.assertFalse(res["action_allowed"])

    def test_04_non_owner_respects_audit_wait(self):
        """Prova que rotinas internas sem diretiva do Owner aguardam auditoria pendente."""
        res = evaluate_precedence(
            sender_id="AGENT_N03",
            directive_type="INTERNAL_ROUTINE",
            action="CONTINUE_AUTO_TASK",
            pending_audit=True
        )
        self.assertEqual(res["decision"], "WAIT_FOR_AUDIT")
        self.assertFalse(res["action_allowed"])

    def test_05_real_powers_matrix_contains_both_nodes(self):
        """Verifica integridade da matriz de poderes reais."""
        self.assertIn("Sentinela_PC_Casa", REAL_POWERS_MATRIX)
        self.assertIn("Antigravity", REAL_POWERS_MATRIX)
        bot_powers = REAL_POWERS_MATRIX["Sentinela_PC_Casa"]["authorized_powers"]
        self.assertIn("RECEIVE_AUTHENTICATED_OWNER_COMMANDS", bot_powers)
        self.assertIn("PUSH_TELEGRAM_NOTIFICATIONS_TO_OWNER", bot_powers)

if __name__ == "__main__":
    unittest.main()
