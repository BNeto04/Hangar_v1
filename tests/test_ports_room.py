import unittest
import sqlite3
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from az000_governance.ports import (
    TypedPortEnvelope,
    create_port_envelope,
    validate_port_envelope,
    PortRegistry,
    PortDefinition,
)
from az000_governance.arca import (
    get_room_dependencies,
    get_room_order,
)


class TestPortsRoom(unittest.TestCase):
    def setUp(self):
        self.registry = PortRegistry()
        self.src_addr = "Hangar_v1/AZ000_GOVERNANCA_SOBERANIA/OWNER_INTENT/INGESTOR:P-GOV-INTENT-IN-01"
        self.tgt_addr = "Hangar_v1/PORTS/REGISTRY/DISPATCHER:P-PORTS-ROUTER-01"
        self.out_addr = "Hangar_v1/EXTERNAL/TELEGRAM/BOT:P-EXT-NOTIFY-OUT-01"

    def test_01_typed_port_envelope_creation_and_hash(self):
        payload = {"directive": "EXECUTE_ROOM", "room": "PORTS"}
        envelope = create_port_envelope(
            source_id=self.src_addr,
            target=self.tgt_addr,
            schema="PORT_ENVELOPE_V1",
            payload=payload,
            evidence_refs=["SHA256:abcd1234"]
        )
        self.assertEqual(envelope.schema, "PORT_ENVELOPE_V1")
        self.assertEqual(envelope.source_id, self.src_addr)
        self.assertEqual(envelope.target, self.tgt_addr)
        self.assertTrue(len(envelope.payload_sha256) == 64)
        
        d = envelope.to_dict()
        valid, msg = validate_port_envelope(d)
        self.assertTrue(valid, msg)

    def test_02_typed_port_envelope_validation_rules(self):
        # Invalid source address
        with self.assertRaises(ValueError):
            create_port_envelope(
                source_id="INVALID_ADDR_NO_SLASH",
                target=self.tgt_addr,
                schema="SCHEMA_V1",
                payload={"test": 1}
            )

        # Tampered payload hash
        envelope = create_port_envelope(
            source_id=self.src_addr,
            target=self.tgt_addr,
            schema="PORT_ENVELOPE_V1",
            payload={"initial": "data"}
        )
        data = envelope.to_dict()
        data["payload_sha256"] = "0" * 64
        valid, msg = validate_port_envelope(data)
        self.assertFalse(valid)
        self.assertIn("Hash SHA-256 do payload divergente", msg)

    def test_03_port_registry_and_dispatch(self):
        self.registry.register_port(self.src_addr, direction="INOUT", description="Gov Port")
        self.registry.register_port(self.tgt_addr, direction="INOUT", description="Router Port", allowed_schemas=["PORT_ENVELOPE_V1"])
        self.registry.register_port(self.out_addr, direction="OUT", description="Out only Port")

        received = []
        def listener(env: TypedPortEnvelope):
            received.append(env)

        self.registry.subscribe(self.tgt_addr, listener)

        envelope = create_port_envelope(
            source_id=self.src_addr,
            target=self.tgt_addr,
            schema="PORT_ENVELOPE_V1",
            payload={"msg": "hello"}
        )
        success = self.registry.dispatch(envelope)
        self.assertTrue(success)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].payload["msg"], "hello")

        # Proibir envio para porta OUT-only
        env_to_out = create_port_envelope(
            source_id=self.src_addr,
            target=self.out_addr,
            schema="PORT_ENVELOPE_V1",
            payload={"msg": "blocked"}
        )
        with self.assertRaises(PermissionError):
            self.registry.dispatch(env_to_out)

    def test_04_upstream_dependencies_governance_world_plant_complete(self):
        db_path = Path(r"C:\Users\PICHAU\AppData\Local\hermes\kanban.db")
        self.assertTrue(db_path.exists())
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        cur.execute("SELECT id, status FROM tasks WHERE id = 't_hangar_az000_intent_seal_ingestion_01'")
        gov_card = cur.fetchone()
        self.assertIsNotNone(gov_card)
        self.assertEqual(gov_card[1], "done")

        cur.execute("SELECT id, status FROM tasks WHERE id = 't_hangar_world_room_completion_01'")
        world_card = cur.fetchone()
        self.assertIsNotNone(world_card)
        self.assertEqual(world_card[1], "done")

        cur.execute("SELECT id, status FROM tasks WHERE id = 't_hangar_plant_room_completion_01'")
        plant_card = cur.fetchone()
        self.assertIsNotNone(plant_card)
        self.assertEqual(plant_card[1], "done")

        conn.close()

    def test_05_ports_index_and_spec_reference_arca(self):
        index_file = REPO_ROOT / "vault" / "PORTS" / "INDEX.md"
        spec_file = REPO_ROOT / "DOCS" / "24_PORTS_ROOM_SPEC.md"

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
        ports_idx = next(i for i, r in enumerate(rooms) if r.room_name == "PORTS")
        self.assertEqual(ports_idx, 3)  # Quarto comodo (Tier 4)

        next_room = rooms[ports_idx + 1]
        self.assertEqual(next_room.room_name, "CAPABILITIES", "O proximo comodo na ordem deve ser CAPABILITIES.")
        self.assertEqual(next_room.tier, 5)


if __name__ == "__main__":
    unittest.main()
