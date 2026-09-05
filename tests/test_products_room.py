#!/usr/bin/env python3
"""
test_products_room.py — Suíte de testes unitários para validação do cômodo PRODUCTS (Tier 11 - Final).
Garante conformidade com ARCA (R-DOM-002, R-DOM-005, R-DOM-006).
Critérios: "Todos os 10 cômodos precedentes fechados e auditados", "Homologação explícita do Proprietário".
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
from az000_governance.products import (
    CanonicalReleaseNotes,
    ProductArtifact,
    ProductIntegrityManifest,
    ProductReleaseManager,
    get_global_product_release_manager,
)


class TestProductsRoom(unittest.TestCase):

    def setUp(self):
        self.manager = ProductReleaseManager(repo_root=str(REPO_ROOT))

    def test_01_arca_canonical_dependencies(self):
        """Valida se o cômodo PRODUCTS depende formalmente de todos os 10 cômodos anteriores."""
        rooms = get_room_order()
        prod_room = next((r for r in rooms if r.room_name == "PRODUCTS"), None)
        self.assertIsNotNone(prod_room, "Cômodo PRODUCTS deve existir na ARCA.")
        self.assertEqual(prod_room.tier, 11)

        expected_deps = (
            "GOVERNANCE", "WORLD", "PLANT", "PORTS", "CAPABILITIES",
            "MACHINES", "INTELLIGENCE", "EXTERNAL", "TRACE", "COCKPITS"
        )
        for dep in expected_deps:
            self.assertIn(dep, prod_room.dependencies, f"Dependência ausente em PRODUCTS: {dep}")

        self.assertIn("Todos os 10 cômodos precedentes fechados e auditados", prod_room.closure_criteria)
        self.assertIn("Homologação explícita do Proprietário", prod_room.closure_criteria)

    def test_02_canonical_release_notes_generation(self):
        """Valida geração e estrutura das release notes canônicas para os 11 cômodos."""
        notes = self.manager.generate_release_notes("v1.0.0")
        self.assertIsInstance(notes, CanonicalReleaseNotes)
        self.assertEqual(notes.release_tag, "v1.0.0")
        self.assertEqual(len(notes.tier_summaries), 11, "Release notes devem abranger os 11 cômodos da ARCA.")
        self.assertEqual(notes.overall_status, "HOMOLOGATED")
        self.assertEqual(notes.total_tests_passed, 79)

        # Validar serialização JSON
        json_output = notes.to_json()
        self.assertIn("v1.0.0", json_output)
        self.assertIn("GOVERNANCE", json_output)
        self.assertIn("PRODUCTS", json_output)

    def test_03_integrity_manifest_emission_and_verification(self):
        """Valida emissão do manifesto de integridade final e verificação matemática."""
        manifest = self.manager.emit_integrity_manifest("v1.0.0")
        self.assertIsInstance(manifest, ProductIntegrityManifest)
        self.assertTrue(manifest.is_complete)
        self.assertEqual(len(manifest.root_sha256), 64)
        self.assertTrue(manifest.verify_integrity())

        # Verificar integridade pelo manager
        ok, msg = self.manager.verify_release_integrity(manifest)
        self.assertTrue(ok)
        self.assertIn("MANIFEST_VERIFIED_OK", msg)

    def test_04_fail_closed_on_tampered_manifest(self):
        """R-DOM-002: FAIL_CLOSED caso o manifesto seja adulterado ou falte algum cômodo."""
        manifest = self.manager.emit_integrity_manifest("v1.0.0")

        # 1. Adulterar digest de um cômodo
        manifest.room_digests["GOVERNANCE"] = "bad_digest_corrupted_value"
        ok, msg = self.manager.verify_release_integrity(manifest)
        self.assertFalse(ok)
        self.assertIn("FAIL_CLOSED", msg)

        # 2. Remover cômodo obrigatório
        del manifest.room_digests["GOVERNANCE"]
        ok, msg = self.manager.verify_release_integrity(manifest)
        self.assertFalse(ok)
        self.assertIn("FAIL_CLOSED", msg)

    def test_05_upstream_dependencies_complete_in_kanban(self):
        """Valida que todos os 10 cômodos anteriores (Tier 1 a 10) estão em 'done' no Hermes Kanban."""
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
            "t_hangar_cockpits_room_completion_01",
        ]

        for tid in tasks_to_check:
            cur.execute("SELECT id, status FROM tasks WHERE id = ?", (tid,))
            row = cur.fetchone()
            self.assertIsNotNone(row, f"Card '{tid}' deve existir no Hermes Kanban.")
            self.assertEqual(row[1], "done", f"Card '{tid}' deve estar 'done'.")

        conn.close()

    def test_06_terminal_room_all_complete(self):
        """Valida que PRODUCTS é o cômodo terminal da ARCA e conclui a cadeia linear de 11 cômodos."""
        rooms = get_room_order()
        self.assertEqual(len(rooms), 11, "A ARCA deve ter exatamente 11 cômodos.")

        last_room = rooms[-1]
        self.assertEqual(last_room.room_name, "PRODUCTS")
        self.assertEqual(last_room.tier, 11)


if __name__ == "__main__":
    unittest.main()
