#!/usr/bin/env python3
"""
test_arca_domain_rules.py — Suíte unitária do Módulo ARCA e Política de Ordem de Cômodos.
Valida: Presença das 7 regras canônicas, integridade SHA-256, imutabilidade,
topologia acíclica de cômodos (DAG), referências em módulos satélites e espelho documental.
"""

import sys
import unittest
from pathlib import Path
from dataclasses import FrozenInstanceError

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from az000_governance.arca import (
    ARCA_DOMAIN_RULES,
    ROOM_EXECUTION_ORDER,
    compute_arca_sha256,
    get_domain_rules,
    get_room_dependencies,
    get_room_order,
    get_rule_by_id,
    verify_arca_integrity,
)
from az000_governance.owner_intent import circuit as circuit_mod


class TestARCADomainRules(unittest.TestCase):
    def test_01_all_7_domain_rules_present(self):
        rules = get_domain_rules()
        self.assertEqual(len(rules), 7, "A ARCA deve conter exatamente 7 regras fundamentais.")
        
        expected_ids = {
            "R-DOM-001", "R-DOM-002", "R-DOM-003", "R-DOM-004",
            "R-DOM-005", "R-DOM-006", "R-DOM-007"
        }
        actual_ids = {r.rule_id for r in rules}
        self.assertEqual(actual_ids, expected_ids)

        expected_names = {
            "SOBERANIA_PROPRIETARIO",
            "FAIL_CLOSED_SYSTEMIC",
            "NO_UNSEALED_PASS",
            "NO_SPEC_NO_CODE",
            "ROOM_BY_ROOM_ORDER",
            "SINGLE_SOURCE_OF_TRUTH_ARCA",
            "EVIDENCE_FIRST_PROMOTION",
        }
        actual_names = {r.name for r in rules}
        self.assertEqual(actual_names, expected_names)

        for r in rules:
            self.assertTrue(r.is_active)
            self.assertTrue(len(r.description) > 20)
            self.assertTrue(len(r.rationale) > 10)

    def test_02_arca_integrity_and_sha256(self):
        self.assertTrue(verify_arca_integrity())
        sha = compute_arca_sha256()
        self.assertEqual(len(sha), 64)
        # Determinismo: re-cálculo deve produzir exatamente o mesmo hash
        self.assertEqual(compute_arca_sha256(), sha)

    def test_03_immutability_enforcement(self):
        rule = get_rule_by_id("R-DOM-001")
        self.assertIsNotNone(rule)
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            rule.name = "MUTATED_NAME"

        with self.assertRaises(TypeError):
            ARCA_DOMAIN_RULES[0] = None  # Tupla imutável

    def test_04_room_order_and_dependencies(self):
        rooms = get_room_order()
        self.assertEqual(len(rooms), 11, "Devem existir exatamente 11 cômodos topológicos.")

        # Primeiro cômodo deve ser GOVERNANCE com tier 1 e zero dependências
        gov_room = rooms[0]
        self.assertEqual(gov_room.room_name, "GOVERNANCE")
        self.assertEqual(gov_room.tier, 1)
        self.assertEqual(len(gov_room.dependencies), 0)

        # Último cômodo deve ser PRODUCTS com tier 11
        prod_room = rooms[-1]
        self.assertEqual(prod_room.room_name, "PRODUCTS")
        self.assertEqual(prod_room.tier, 11)

        # Validar topologia acíclica: todo cômodo só pode depender de cômodos de tier inferior
        room_tiers = {r.room_name: r.tier for r in rooms}
        for r in rooms:
            for dep in r.dependencies:
                self.assertIn(dep, room_tiers, f"Dependência '{dep}' desconhecida.")
                self.assertLess(
                    room_tiers[dep], r.tier,
                    f"Violação topológica: {r.room_name} (tier {r.tier}) depende de {dep} (tier {room_tiers[dep]})."
                )

        # Testar consulta de dependências
        self.assertEqual(get_room_dependencies("WORLD"), ["GOVERNANCE"])
        with self.assertRaises(KeyError):
            get_room_dependencies("NON_EXISTENT_ROOM")

    def test_05_covered_modules_reference_arca(self):
        # Módulo owner_intent/circuit.py deve referenciar explicitamente a ARCA
        self.assertTrue(hasattr(circuit_mod, "ARCA_RULES_REF"))
        self.assertEqual(circuit_mod.ARCA_RULES_REF.get("sovereignty"), "R-DOM-001")
        self.assertEqual(circuit_mod.ARCA_RULES_REF.get("fail_closed"), "R-DOM-002")
        self.assertEqual(circuit_mod.ARCA_RULES_REF.get("no_unsealed_pass"), "R-DOM-003")

    def test_06_vault_and_doc_sync(self):
        vault_file = REPO_ROOT / "vault" / "GOVERNANCE" / "ARCA_DOMAIN_RULES.md"
        doc_file = REPO_ROOT / "DOCS" / "20_ARCA_GOVERNANCE_AND_ROOM_ORDER_SPEC.md"

        self.assertTrue(vault_file.exists(), "vault/GOVERNANCE/ARCA_DOMAIN_RULES.md deve existir.")
        self.assertTrue(doc_file.exists(), "DOCS/20_ARCA_GOVERNANCE_AND_ROOM_ORDER_SPEC.md deve existir.")

        vault_content = vault_file.read_text(encoding="utf-8")
        doc_content = doc_file.read_text(encoding="utf-8")

        for r_id in ["R-DOM-001", "R-DOM-002", "R-DOM-003", "R-DOM-004", "R-DOM-005", "R-DOM-006", "R-DOM-007"]:
            self.assertIn(r_id, vault_content)
            self.assertIn(r_id, doc_content)


if __name__ == "__main__":
    unittest.main()
