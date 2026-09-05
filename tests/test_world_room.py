#!/usr/bin/env python3
"""
test_world_room.py — Suíte unitária e de auditoria do Cômodo WORLD (Tier 2).
Valida: Integridade do Master_World.canvas, zero links quebrados, conformidade com a ARCA,
satisfação da dependência a montante (GOVERNANCE) e documentação canônica.
"""

import json
import re
import sqlite3
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from az000_governance.arca import (
    get_room_dependencies,
    get_room_order,
    get_rule_by_id,
)


class TestWorldRoom(unittest.TestCase):
    def setUp(self):
        self.vault_dir = REPO_ROOT / "vault"
        self.world_dir = self.vault_dir / "WORLD"
        self.canvas_file = self.world_dir / "Master_World.canvas"
        self.index_file = self.world_dir / "INDEX.md"
        self.doc_file = REPO_ROOT / "DOCS" / "22_WORLD_ROOM_SPEC.md"
        self.db_path = Path(r"C:\Users\PICHAU\AppData\Local\hermes\kanban.db")

    def test_01_canvas_structure_and_zero_broken_links(self):
        self.assertTrue(self.canvas_file.exists(), "Master_World.canvas deve existir.")
        canvas_data = json.loads(self.canvas_file.read_text(encoding="utf-8"))

        nodes = canvas_data.get("nodes", [])
        edges = canvas_data.get("edges", [])

        self.assertGreaterEqual(len(nodes), 17, "Canvas deve conter pelo menos 17 nós.")
        self.assertGreaterEqual(len(edges), 24, "Canvas deve conter pelo menos 24 arestas.")

        # Extrair todos os wikilinks [[caminho|label]] ou [[caminho]]
        wikilinks = []
        for node in nodes:
            text = node.get("text", "")
            matches = re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", text)
            wikilinks.extend(matches)

        self.assertGreater(len(wikilinks), 0, "Canvas deve conter navegação por wikilinks.")

        broken_links = []
        for link in set(wikilinks):
            target = self.vault_dir / f"{link}.md"
            if not target.exists():
                broken_links.append(link)

        self.assertEqual(len(broken_links), 0, f"Links quebrados no Canvas: {broken_links}")

    def test_02_upstream_dependency_governance_complete(self):
        deps = get_room_dependencies("WORLD")
        self.assertEqual(deps, ["GOVERNANCE"], "WORLD só deve depender de GOVERNANCE.")

        # Verificar se as tarefas fundamentais de GOVERNANCE estão concluídas no Kanban
        self.assertTrue(self.db_path.exists())
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT status FROM tasks WHERE id = 't_hangar_arca_governance_domain_rules_01'")
        row = cur.fetchone()
        conn.close()

        self.assertIsNotNone(row)
        self.assertEqual(row[0], "done", "t_hangar_arca_governance_domain_rules_01 deve estar em DONE.")

    def test_03_world_index_and_spec_reference_arca(self):
        self.assertTrue(self.index_file.exists())
        self.assertTrue(self.doc_file.exists())

        index_content = self.index_file.read_text(encoding="utf-8")
        doc_content = self.doc_file.read_text(encoding="utf-8")

        # Deve referenciar a regra de ordem por cômodo e unicidade da ARCA
        self.assertIn("R-DOM-005", index_content)
        self.assertIn("R-DOM-006", index_content)
        self.assertIn("R-DOM-005", doc_content)
        self.assertIn("R-DOM-006", doc_content)

        # Deve referenciar o Canvas
        self.assertIn("Master_World.canvas", index_content)
        self.assertIn("Master_World.canvas", doc_content)

    def test_04_next_eligible_room_in_order(self):
        rooms = get_room_order()
        world_idx = next(i for i, r in enumerate(rooms) if r.room_name == "WORLD")
        self.assertEqual(world_idx, 1)  # Segundo cômodo (Tier 2)

        next_room = rooms[world_idx + 1]
        self.assertEqual(next_room.room_name, "PLANT", "O próximo cômodo na ordem deve ser PLANT.")
        self.assertEqual(next_room.tier, 3)


if __name__ == "__main__":
    unittest.main()
