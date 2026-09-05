import unittest
import sqlite3
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from az000_governance.capabilities import (
    CapabilityDefinition,
    CapabilityRegistry,
    get_global_capability_registry,
    GraphifyEngine,
)
from az000_governance.arca import (
    get_room_dependencies,
    get_room_order,
)


class TestCapabilitiesRoom(unittest.TestCase):
    def setUp(self):
        self.registry = get_global_capability_registry()
        self.vault_path = REPO_ROOT / "vault"

    def test_01_canonical_capabilities_registered(self):
        caps = self.registry.list_all()
        cap_ids = {c.capability_id for c in caps}
        expected = {"GRAPHIFY", "OPEN_DESIGN", "PONYTAIL", "IMPROVE", "RUFLO"}
        self.assertTrue(expected.issubset(cap_ids), f"Capacidades ausentes: {expected - cap_ids}")

        for cap in caps:
            self.assertTrue(cap.primary_port.startswith("Hangar_v1/CAPABILITIES/"))
            self.assertTrue(cap.is_active)

    def test_02_acyclic_dependency_validation(self):
        local_reg = CapabilityRegistry()
        local_reg.register(CapabilityDefinition(
            capability_id="ENGINE_A",
            name="Engine A",
            version="1.0",
            description="Test Engine A",
            primary_port="Hangar_v1/CAPABILITIES/A:P-01",
            dependencies=["ENGINE_B"]
        ))
        local_reg.register(CapabilityDefinition(
            capability_id="ENGINE_B",
            name="Engine B",
            version="1.0",
            description="Test Engine B",
            primary_port="Hangar_v1/CAPABILITIES/B:P-01",
            dependencies=[]
        ))

        # Adicionar dependencia circular deve falhar
        with self.assertRaises(ValueError) as ctx:
            local_reg.register(CapabilityDefinition(
                capability_id="ENGINE_B",
                name="Engine B Modified",
                version="1.0",
                description="Test Cycle",
                primary_port="Hangar_v1/CAPABILITIES/B:P-01",
                dependencies=["ENGINE_A"]
            ))
        self.assertIn("ciclica", str(ctx.exception).lower())

    def test_03_graphify_engine_audit(self):
        engine = GraphifyEngine(self.vault_path)
        result, metrics = engine.audit_vault_graph()

        self.assertEqual(result.capability_id, "GRAPHIFY")
        self.assertEqual(result.status, "SUCCESS")
        self.assertGreater(metrics["total_nodes"], 10)
        self.assertIsNotNone(result.evidence_sha256)
        self.assertEqual(len(result.evidence_sha256), 64)

    def test_04_upstream_dependencies_governance_world_plant_ports_complete(self):
        db_path = Path(r"C:\Users\PICHAU\AppData\Local\hermes\kanban.db")
        self.assertTrue(db_path.exists())
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        tasks_to_check = [
            "t_hangar_az000_intent_seal_ingestion_01",
            "t_hangar_world_room_completion_01",
            "t_hangar_plant_room_completion_01",
            "t_hangar_ports_room_completion_01",
        ]

        for tid in tasks_to_check:
            cur.execute("SELECT id, status FROM tasks WHERE id = ?", (tid,))
            row = cur.fetchone()
            self.assertIsNotNone(row, f"Card '{tid}' deve existir no Hermes Kanban.")
            self.assertEqual(row[1], "done", f"Card '{tid}' deve estar 'done'.")

        conn.close()

    def test_05_capabilities_index_and_spec_reference_arca(self):
        index_file = REPO_ROOT / "vault" / "CAPABILITIES" / "INDEX.md"
        spec_file = REPO_ROOT / "DOCS" / "25_CAPABILITIES_ROOM_SPEC.md"

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
        cap_idx = next(i for i, r in enumerate(rooms) if r.room_name == "CAPABILITIES")
        self.assertEqual(cap_idx, 4)  # Quinto comodo (Tier 5)

        next_room = rooms[cap_idx + 1]
        self.assertEqual(next_room.room_name, "MACHINES", "O proximo comodo na ordem deve ser MACHINES.")
        self.assertEqual(next_room.tier, 6)


if __name__ == "__main__":
    unittest.main()
