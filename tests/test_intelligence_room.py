import unittest
import sqlite3
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from az000_governance.intelligence import (
    CognitiveAgentDefinition,
    AgentThoughtChain,
    TypedAgentOrchestrator,
    get_global_agent_orchestrator,
)
from az000_governance.arca import (
    get_room_dependencies,
    get_room_order,
)


class TestIntelligenceRoom(unittest.TestCase):
    def setUp(self):
        self.orchestrator = get_global_agent_orchestrator()

    def test_01_canonical_cognitive_agents_registered(self):
        agents = self.orchestrator.list_agents()
        agent_ids = {a.agent_id for a in agents}
        expected = {
            "CHAR-PLANNER-01",
            "CHAR-EXECUTOR-01",
            "CHAR-VERIFIER-01",
            "CHAR-CURATOR-01",
            "CHAR-OBSIDIAN-01",
        }
        self.assertTrue(expected.issubset(agent_ids), f"Agentes ausentes: {expected - agent_ids}")

        for a in agents:
            self.assertTrue(a.primary_port.startswith("Hangar_v1/INTELLIGENCE/"))
            self.assertTrue(a.level.startswith("N"))
            self.assertTrue(a.is_active)

    def test_02_structured_reasoning_verification(self):
        facts = {
            "FACT: GOVERNANCE Tier 1 is COMPLETE",
            "FACT: MACHINES Tier 6 is COMPLETE",
        }
        chain = AgentThoughtChain(
            chain_id="CHAIN-TEST-001",
            agent_id="CHAR-PLANNER-01",
            premises=[
                "FACT: GOVERNANCE Tier 1 is COMPLETE",
                "FACT: MACHINES Tier 6 is COMPLETE",
            ],
            deductions=[
                "DEDUCTION: Preconditions satisfied, ready to open INTELLIGENCE (Tier 7)"
            ],
            verdict="APPROVED"
        )
        success = self.orchestrator.verify_and_record_thought_chain(chain, known_facts=facts)
        self.assertTrue(success)
        self.assertEqual(len(chain.anti_hallucination_sha256), 64)
        self.assertEqual(chain.verdict, "APPROVED")

    def test_03_anti_hallucination_fail_closed(self):
        facts = {
            "FACT: GOVERNANCE Tier 1 is COMPLETE",
        }
        # Premissa não comprovada
        hallucinated_chain = AgentThoughtChain(
            chain_id="CHAIN-TEST-002",
            agent_id="CHAR-EXECUTOR-01",
            premises=[
                "FACT: GOVERNANCE Tier 1 is COMPLETE",
                "UNPROVEN: Production deployment was authorized without owner intent",
            ],
            deductions=[
                "DEDUCTION: Trigger production deploy"
            ],
            verdict="APPROVED"
        )

        with self.assertRaises(ValueError) as ctx:
            self.orchestrator.verify_and_record_thought_chain(hallucinated_chain, known_facts=facts)

        self.assertIn("ANTI_ALUCINACAO", str(ctx.exception))
        self.assertEqual(hallucinated_chain.verdict, "HOLD")

    def test_04_upstream_dependencies_governance_to_machines_complete(self):
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
        ]

        for tid in tasks_to_check:
            cur.execute("SELECT id, status FROM tasks WHERE id = ?", (tid,))
            row = cur.fetchone()
            self.assertIsNotNone(row, f"Card '{tid}' deve existir no Hermes Kanban.")
            self.assertEqual(row[1], "done", f"Card '{tid}' deve estar 'done'.")

        conn.close()

    def test_05_intelligence_index_and_spec_reference_arca(self):
        index_file = REPO_ROOT / "vault" / "INTELLIGENCE" / "INDEX.md"
        spec_file = REPO_ROOT / "DOCS" / "27_INTELLIGENCE_ROOM_SPEC.md"

        self.assertTrue(index_file.exists())
        self.assertTrue(spec_file.exists())

        idx_text = index_file.read_text(encoding="utf-8")
        spec_text = spec_file.read_text(encoding="utf-8")

        self.assertIn("R-DOM-005", idx_text)
        self.assertIn("R-DOM-006", idx_text)
        self.assertIn("R-DOM-005", spec_text)
        self.assertIn("R-DOM-006", spec_text)

    def test_06_next_eligible_room_in_order(self):
        rooms = get_room_order()
        intel_idx = next(i for i, r in enumerate(rooms) if r.room_name == "INTELLIGENCE")
        self.assertEqual(intel_idx, 6)  # Sétimo cômodo (Tier 7)

        next_room = rooms[intel_idx + 1]
        self.assertEqual(next_room.room_name, "EXTERNAL", "O próximo cômodo na ordem deve ser EXTERNAL.")
        self.assertEqual(next_room.tier, 8)


if __name__ == "__main__":
    unittest.main()
