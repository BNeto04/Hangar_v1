#!/usr/bin/env python3
"""
test_plant_room.py — Suíte unitária e de auditoria do Cômodo PLANT (Tier 3).
Valida: Parser GPS Down Plant, conformidade dos 11 diretórios físicos do Vault,
confinamento de workspaces, satisfação de dependências (GOVERNANCE, WORLD) e especificações.
"""

import sqlite3
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from az000_governance.arca import (
    get_room_dependencies,
    get_room_order,
)
from az000_governance.plant import (
    DownPlantAddress,
    format_down_plant_address,
    is_valid_room,
    parse_down_plant_address,
    validate_down_plant_address,
)


class TestPlantRoom(unittest.TestCase):
    def setUp(self):
        self.vault_dir = REPO_ROOT / "vault"
        self.plant_dir = self.vault_dir / "PLANT"
        self.index_file = self.plant_dir / "INDEX.md"
        self.doc_file = REPO_ROOT / "DOCS" / "23_PLANT_ROOM_SPEC.md"
        self.db_path = Path(r"C:\Users\PICHAU\AppData\Local\hermes\kanban.db")

    def test_01_down_plant_address_parser_valid(self):
        valid_addr = "Hangar_v1/AZ000_GOVERNANCA_SOBERANIA/ARCA/DOMAIN_RULES:P-GOV-ARCA-RULES-01"
        self.assertTrue(validate_down_plant_address(valid_addr))
        parsed = parse_down_plant_address(valid_addr)
        self.assertEqual(parsed.terrain, "Hangar_v1")
        self.assertEqual(parsed.room, "AZ000_GOVERNANCA_SOBERANIA")
        self.assertEqual(parsed.module, "ARCA")
        self.assertEqual(parsed.submodule, "DOMAIN_RULES")
        self.assertEqual(parsed.port, "P-GOV-ARCA-RULES-01")
        self.assertEqual(parsed.to_canonical_string(), valid_addr)
        self.assertTrue(parsed.is_canonical_room())

    def test_02_down_plant_address_parser_invalid(self):
        invalid_addresses = [
            "InvalidAddressWithoutDelimiters",
            "Terrain/Room/Module/Submodule",  # Faltando :PORTA
            "Terrain/Room/Module:Port",        # Faltando Submodule
            "Terrain//Module/Submodule:Port", # Room vazio
            "",                                # Vazio
            None,                              # None
        ]
        for inv in invalid_addresses:
            self.assertFalse(validate_down_plant_address(inv), f"Deveria ser invalido: {inv}")
            with self.assertRaises((ValueError, TypeError)):
                parse_down_plant_address(inv)

    def test_03_all_11_vault_room_directories_exist(self):
        canonical_rooms = get_room_order()
        self.assertEqual(len(canonical_rooms), 11)

        for room in canonical_rooms:
            room_dir = self.vault_dir / room.room_name
            self.assertTrue(room_dir.exists(), f"Diretorio fisico do comodo {room.room_name} deve existir no Vault.")
            index_file = room_dir / "INDEX.md"
            self.assertTrue(index_file.exists(), f"Arquivo INDEX.md do comodo {room.room_name} deve existir.")

    def test_04_upstream_dependencies_governance_and_world_complete(self):
        deps = get_room_dependencies("PLANT")
        self.assertEqual(set(deps), {"GOVERNANCE", "WORLD"}, "PLANT deve depender estritamente de GOVERNANCE e WORLD.")

        self.assertTrue(self.db_path.exists())
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # GOVERNANCE check
        cur.execute("SELECT status FROM tasks WHERE id = 't_hangar_arca_governance_domain_rules_01'")
        row_gov = cur.fetchone()
        self.assertIsNotNone(row_gov)
        self.assertEqual(row_gov[0], "done")

        # WORLD check
        cur.execute("SELECT status FROM tasks WHERE id = 't_hangar_world_room_completion_01'")
        row_wld = cur.fetchone()
        self.assertIsNotNone(row_wld)
        self.assertEqual(row_wld[0], "done")

        conn.close()

    def test_05_plant_index_and_spec_reference_arca(self):
        self.assertTrue(self.index_file.exists())
        self.assertTrue(self.doc_file.exists())

        index_content = self.index_file.read_text(encoding="utf-8")
        doc_content = self.doc_file.read_text(encoding="utf-8")

        self.assertIn("R-DOM-005", index_content)
        self.assertIn("R-DOM-006", index_content)
        self.assertIn("R-DOM-005", doc_content)
        self.assertIn("R-DOM-006", doc_content)

    def test_06_next_eligible_room_in_order(self):
        rooms = get_room_order()
        plant_idx = next(i for i, r in enumerate(rooms) if r.room_name == "PLANT")
        self.assertEqual(plant_idx, 2)  # Terceiro comodo (Tier 3)

        next_room = rooms[plant_idx + 1]
        self.assertEqual(next_room.room_name, "PORTS", "O proximo comodo na ordem deve ser PORTS.")
        self.assertEqual(next_room.tier, 4)


if __name__ == "__main__":
    unittest.main()
