#!/usr/bin/env python3
"""
test_cockpits_room.py — Suíte de testes unitários para validação do cômodo COCKPITS (Tier 10).
Garante conformidade com ARCA (R-DOM-001, R-DOM-002, R-DOM-005, R-DOM-006).
Critérios: "Visualização espacial sem atrito", "Mapeamento de comandos do Proprietário".
"""

import json
import sqlite3
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from az000_governance.arca import (
    get_room_dependencies,
    get_room_order,
)
from az000_governance.cockpits import (
    CockpitController,
    CockpitView,
    OwnerCommand,
    RoomSnapshot,
    TeacherModeState,
    get_global_cockpit_controller,
)
from az000_governance.plant.addressing import validate_down_plant_address


class TestCockpitsRoom(unittest.TestCase):

    def setUp(self):
        self.controller = CockpitController(owner_secret="test_owner_secret_key")

    def test_01_arca_canonical_dependencies(self):
        """Valida se o cômodo COCKPITS está registrado na ARCA com dependências estritas."""
        rooms = get_room_order()
        cockpit_room = next((r for r in rooms if r.room_name == "COCKPITS"), None)
        self.assertIsNotNone(cockpit_room, "Cômodo COCKPITS deve existir na ARCA.")
        self.assertEqual(cockpit_room.tier, 10)
        self.assertIn("INTELLIGENCE", cockpit_room.dependencies)
        self.assertIn("TRACE", cockpit_room.dependencies)
        self.assertIn("Visualização espacial sem atrito", cockpit_room.closure_criteria)
        self.assertIn("Mapeamento de comandos do Proprietário", cockpit_room.closure_criteria)

    def test_02_frictionless_spatial_visualization(self):
        """Valida geração da visualização espacial completa dos 11 cômodos sem atrito."""
        view = self.controller.render_spatial_view()
        self.assertIsInstance(view, CockpitView)
        self.assertEqual(len(view.rooms), 11, "A visualização espacial deve conter exatamente os 11 cômodos.")

        room_names = [r.room_name for r in view.rooms]
        self.assertEqual(room_names[0], "GOVERNANCE")
        self.assertEqual(room_names[9], "COCKPITS")
        self.assertEqual(room_names[10], "PRODUCTS")

        for r in view.rooms:
            self.assertTrue(validate_down_plant_address(r.primary_port))
            self.assertIn(r.status, ("COMPLETE", "IN_PROGRESS", "PENDING"))

        # Testar serialização sem falhas
        view_json = view.to_json()
        self.assertIn("VIEW-SPATIAL-", view_json)

    def test_03_owner_command_mapping_and_dispatch(self):
        """Valida mapeamento e despacho autorizado de comando soberano do Proprietário (R-DOM-001)."""
        cmd = OwnerCommand(
            command_id="CMD-SOVEREIGN-001",
            command_type="APPROVE_ROOM",
            issuer="PROPRIETARIO",
            parameters={"target_room": "COCKPITS", "verdict": "HOMOLOGADO"},
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            auth_token="test_owner_secret_key",
        )

        ok, msg, env = self.controller.dispatch_owner_command(cmd)
        self.assertTrue(ok)
        self.assertIn("mapeado e despachado", msg)
        self.assertIsNotNone(env)
        self.assertEqual(env.schema, "OWNER_COMMAND_V1")
        self.assertTrue(validate_down_plant_address(env.source_id))
        self.assertTrue(validate_down_plant_address(env.target))
        self.assertEqual(env.payload["issuer"], "PROPRIETARIO")
        self.assertTrue(env.payload["authorized"])

    def test_04_fail_closed_on_unauthorized_or_forged_command(self):
        """R-DOM-001 e R-DOM-002: FAIL_CLOSED caso comando não provenha do Proprietário ou token seja inválido."""
        # 1. Emissor não soberano
        cmd_unauth = OwnerCommand(
            command_id="CMD-ROGUE-001",
            command_type="PAUSE_PIPELINE",
            issuer="CHAR-EXECUTOR-01",
            auth_token="test_owner_secret_key",
        )
        ok, msg, env = self.controller.dispatch_owner_command(cmd_unauth)
        self.assertFalse(ok)
        self.assertIn("FAIL_CLOSED", msg)
        self.assertIsNone(env)

        # 2. Token incorreto
        cmd_bad_token = OwnerCommand(
            command_id="CMD-BAD-TOKEN-001",
            command_type="PAUSE_PIPELINE",
            issuer="PROPRIETARIO",
            auth_token="wrong_secret",
        )
        ok, msg, env = self.controller.dispatch_owner_command(cmd_bad_token)
        self.assertFalse(ok)
        self.assertIn("FAIL_CLOSED", msg)
        self.assertIsNone(env)

        # 3. Tipo de comando desconhecido
        cmd_unknown = OwnerCommand(
            command_id="CMD-UNKNOWN-001",
            command_type="DESTROY_DATABASE",
            issuer="PROPRIETARIO",
            auth_token="test_owner_secret_key",
        )
        ok, msg, env = self.controller.dispatch_owner_command(cmd_unknown)
        self.assertFalse(ok)
        self.assertIn("FAIL_CLOSED", msg)
        self.assertIsNone(env)

    def test_05_upstream_dependencies_complete_in_kanban(self):
        """Valida que todos os cômodos a montante (Tier 1 a 9) estão concluídos no Hermes."""
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
            "t_hangar_trace_room_completion_01",
        ]

        for tid in tasks_to_check:
            cur.execute("SELECT id, status FROM tasks WHERE id = ?", (tid,))
            row = cur.fetchone()
            self.assertIsNotNone(row, f"Card '{tid}' deve existir no Hermes Kanban.")
            self.assertEqual(row[1], "done", f"Card '{tid}' deve estar 'done'.")

        conn.close()

    def test_06_next_eligible_room_is_products(self):
        """Valida que o próximo e último cômodo na ordem linear da ARCA é PRODUCTS (Tier 11)."""
        rooms = get_room_order()
        cockpit_idx = next(i for i, r in enumerate(rooms) if r.room_name == "COCKPITS")
        self.assertEqual(cockpit_idx, 9)  # Décimo cômodo (Tier 10)

        next_room = rooms[cockpit_idx + 1]
        self.assertEqual(next_room.room_name, "PRODUCTS", "O próximo cômodo na ordem deve ser PRODUCTS.")
        self.assertEqual(next_room.tier, 11)


if __name__ == "__main__":
    unittest.main()
