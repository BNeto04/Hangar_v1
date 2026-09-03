#!/usr/bin/env python3
"""
SUÍTE DE TESTES DETERMINÍSTICA DO HANGAR V1 — SPRINT 01
Validação dos entregáveis fundacionais dentro do repositório syntheon_adk:
- WORLD_MODEL
- EXECUTION_ALGORITHM
- ADDRESS_SCHEMA
- PILOT_RULE
- AUTH_GATE
- TRACE_SCHEMA
- VAULT_V0.1
"""

import hashlib
import json
import os
import sys
import unittest
from pathlib import Path

# Paths canônicos reais
HANGAR_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = HANGAR_DIR.parent

# Mock Terrain para carregamento dos bridges e nanomachines dos CHARs
MOCK_TERRAIN_DIR = Path(r"C:\Users\PICHAU\.gemini\antigravity\scratch\MOCK-TERRAIN")
if str(MOCK_TERRAIN_DIR) not in sys.path:
    sys.path.insert(0, str(MOCK_TERRAIN_DIR))

from bridges.char_obsidian import CharObsidianAgent
from bridges.char_quality_gate import CharQualityGateAgent


class TestHangarV1Sprint01(unittest.TestCase):
    """Suíte de verificação arquitetural do Hangar V1 Sprint 01 no repositório syntheon_adk."""

    def setUp(self):
        self.hangar_dir = HANGAR_DIR
        self.docs_dir = HANGAR_DIR / "DOCS"
        self.vault_dir = HANGAR_DIR / "vault"
        self.nm_registry = {
            "NM-OBS-READ": str(MOCK_TERRAIN_DIR / "nanomachines" / "NM-OBS-READ" / "nm_obs_read.py"),
            "NM-OBS-WRITE": str(MOCK_TERRAIN_DIR / "nanomachines" / "NM-OBS-WRITE" / "nm_obs_write.py"),
            "NM-OBS-PATCH": str(MOCK_TERRAIN_DIR / "nanomachines" / "NM-OBS-PATCH" / "nm_obs_patch.py"),
            "NM-OBS-VERIFY-FILE": str(MOCK_TERRAIN_DIR / "nanomachines" / "NM-OBS-VERIFY-FILE" / "nm_obs_verify_file.py"),
            "NM-OBS-PARSE-CANVAS": str(MOCK_TERRAIN_DIR / "nanomachines" / "NM-OBS-PARSE-CANVAS" / "nm_obs_parse_canvas.py"),
            "NM-OBS-BUILD-CANVAS": str(MOCK_TERRAIN_DIR / "nanomachines" / "NM-OBS-BUILD-CANVAS" / "nm_obs_build_canvas.py"),
        }
        self.obsidian_agent = CharObsidianAgent(
            root=str(self.vault_dir),
            nm_registry=self.nm_registry,
        )

    def test_01_all_sprint01_deliverables_exist(self):
        """Verifica se todos os 6 documentos arquiteturais e o Vault V0.1 existem com conteúdo válido."""
        expected_docs = [
            "01_WORLD_MODEL.md",
            "02_EXECUTION_ALGORITHM.md",
            "03_ADDRESS_SCHEMA.md",
            "04_PILOT_RULE.md",
            "05_AUTH_GATE.md",
            "06_TRACE_SCHEMA.md",
        ]
        for doc in expected_docs:
            doc_path = self.docs_dir / doc if (self.docs_dir / doc).exists() else (self.hangar_dir / doc)
            self.assertTrue(doc_path.exists(), f"Documento {doc} ausente no Hangar V1 DOCS.")
            content = doc_path.read_text(encoding="utf-8")
            self.assertGreater(len(content), 100, f"Documento {doc} com conteúdo insuficiente.")

        # Vault Canônico (11 seções top-level + INDEX.md)
        self.assertTrue((self.vault_dir / "INDEX.md").exists(), "Root INDEX.md ausente.")
        top_level_sections = [
            "WORLD", "PLANT", "INTELLIGENCE", "COCKPITS", "CAPABILITIES",
            "MACHINES", "PORTS", "GOVERNANCE", "EXTERNAL", "TRACE", "PRODUCTS"
        ]
        for sec in top_level_sections:
            sec_dir = self.vault_dir / sec
            self.assertTrue(sec_dir.exists() and sec_dir.is_dir(), f"Seção {sec} ausente no Vault.")
            self.assertTrue((sec_dir / "INDEX.md").exists(), f"INDEX.md da seção {sec} ausente.")

    def test_02_vault_v01_graphify_connectivity(self):
        """Verifica a conectividade semântica do Vault através do motor Graphify."""
        index_content = (self.vault_dir / "INDEX.md").read_text(encoding="utf-8")
        top_level_sections = [
            "WORLD", "PLANT", "INTELLIGENCE", "COCKPITS", "CAPABILITIES",
            "MACHINES", "PORTS", "GOVERNANCE", "EXTERNAL", "TRACE", "PRODUCTS"
        ]
        for sec in top_level_sections:
            self.assertIn(f"[[{sec}/INDEX|{sec}]]", index_content)

        # Graphify parsing
        envelope_dir = str(self.hangar_dir / "envelopes")
        os.makedirs(envelope_dir, exist_ok=True)
        graph_res = self.obsidian_agent.execute_graphify_native_pipeline(
            operation_id="op-vault-graph",
            directory_path=".",
            target_canvas_path=None,
            graph_output_path=None,
            envelope_dir=envelope_dir,
        )
        self.assertIn("nodes_count", graph_res)
        self.assertGreaterEqual(graph_res["nodes_count"], 11)
        self.assertGreaterEqual(graph_res["edges_count"], 10)

    def test_03_world_model_and_address_schema_invariants(self):
        """Verifica os invariantes de modelo de mundo e endereçamento canônico."""
        wm_path = self.docs_dir / "01_WORLD_MODEL.md" if (self.docs_dir / "01_WORLD_MODEL.md").exists() else (self.hangar_dir / "01_WORLD_MODEL.md")
        wm_content = wm_path.read_text(encoding="utf-8")
        self.assertIn("WORLD MODEL TOPOLOGY", wm_content)
        self.assertIn("REUSE_FIRST_BUILD_LAST", wm_content)

        addr_path = self.docs_dir / "03_ADDRESS_SCHEMA.md" if (self.docs_dir / "03_ADDRESS_SCHEMA.md").exists() else (self.hangar_dir / "03_ADDRESS_SCHEMA.md")
        addr_content = addr_path.read_text(encoding="utf-8")
        self.assertIn("P-QUALITY-GATE-DECISION-01", addr_content)

    def test_04_execution_algorithm_and_trace_schema_compliance(self):
        """Verifica integridade do algoritmo de execução e formato do trace."""
        trace_path = self.docs_dir / "06_TRACE_SCHEMA.md" if (self.docs_dir / "06_TRACE_SCHEMA.md").exists() else (self.hangar_dir / "06_TRACE_SCHEMA.md")
        trace_content = trace_path.read_text(encoding="utf-8")
        self.assertIn("TRACE-HANGAR-V1", trace_content)
        self.assertIn("evidence_digests", trace_content)
        self.assertIn("route_taken", trace_content)

    def test_05_auth_gate_fail_closed_logic(self):
        """Verifica a lógica fail-closed do Quality Gate de acordo com a especificação de Auth Gate."""
        sec_hash = "a" * 64
        verif_hash = "b" * 64
        target_art = "01_WORLD_MODEL.md"

        sec_payload = {
            "schema": "SECURITY-REVIEW-1",
            "verdict": "SECURITY_PASS",
            "target": target_art,
            "security_review_sha256": sec_hash,
            "source_id": "CHAR-SECURITY-01/P-SECURITY-REVIEW-01",
        }

        verif_payload = {
            "schema": "CHAR-VERIFIER-RESULT-1",
            "overall_verdict": "VERIFICATION_PASSED",
            "target": target_art,
            "target_artifact": target_art,
            "verifier_sha256": verif_hash,
            "source_id": "CHAR-VERIFIER-01/P-VERIFICATION-RESULT-01",
        }

        # Quality Gate Input válido
        valid_gate = {
            "schema": "QUALITY-GATE-INPUT-1",
            "decision_id": "DEC-HANGAR-001",
            "target": target_art,
            "evidence": [
                {
                    "kind": "SECURITY_REVIEW",
                    "schema": "SECURITY-REVIEW-1",
                    "source_id": "CHAR-SECURITY-01/P-SECURITY-REVIEW-01",
                    "verdict": "SECURITY_PASS",
                    "evidence_refs": [sec_hash],
                    "payload": sec_payload,
                },
                {
                    "kind": "VERIFICATION_EVIDENCE",
                    "schema": "VERIFICATION-EVIDENCE-1",
                    "source_id": "CHAR-VERIFIER-01/P-VERIFICATION-RESULT-01",
                    "verdict": "VERIFICATION_PASSED",
                    "evidence_refs": [verif_hash],
                    "payload": verif_payload,
                }
            ]
        }
        dec = CharQualityGateAgent.evaluate_quality_gate(valid_gate)
        self.assertEqual(dec["status"], "QUALITY_GATE_PASS")
        self.assertEqual(dec["recommendation"], "ADVANCE")
        self.assertTrue(dec["eligible_for_promotion"])

        # Quality Gate com evidência corrompida (fail-closed)
        sec_fail_payload = {
            "schema": "SECURITY-REVIEW-1",
            "verdict": "SECURITY_FAIL",
            "target": target_art,
            "security_review_sha256": "c" * 64,
            "source_id": "CHAR-SECURITY-01/P-SECURITY-REVIEW-01",
        }
        corrupt_gate = {
            "schema": "QUALITY-GATE-INPUT-1",
            "decision_id": "DEC-HANGAR-FAIL-001",
            "target": target_art,
            "evidence": [
                {
                    "kind": "SECURITY_REVIEW",
                    "schema": "SECURITY-REVIEW-1",
                    "source_id": "CHAR-SECURITY-01/P-SECURITY-REVIEW-01",
                    "verdict": "SECURITY_FAIL",
                    "evidence_refs": ["c" * 64],
                    "payload": sec_fail_payload,
                }
            ]
        }
        dec_fail = CharQualityGateAgent.evaluate_quality_gate(corrupt_gate)
        self.assertEqual(dec_fail["status"], "QUALITY_GATE_FAIL")
        self.assertEqual(dec_fail["recommendation"], "REJECT")
        self.assertFalse(dec_fail["eligible_for_promotion"])

    def test_06_doc_tree_curatorship_invariants(self):
        """Verifica a conformidade determinística do contrato de curatela contínua da árvore documental."""
        import re

        # 1. Contrato de curatela existe
        contract_path = self.docs_dir / "07_DOC_TREE_CURATORSHIP.md"
        self.assertTrue(contract_path.exists(), "Contrato 07_DOC_TREE_CURATORSHIP.md ausente.")
        content = contract_path.read_text(encoding="utf-8")
        self.assertIn("DOC-TREE-CURATOR-01", content)
        self.assertIn("REALIDADE == MAPA", content)
        self.assertIn("BROKEN_LINKS == 0", content)
        self.assertIn("DUPLICATE_ACTIVE_DOCS == 0", content)

        # 2. Invariante: Zero arquivos .md soltos na raiz de hangar_v1
        loose_md_files = list(self.hangar_dir.glob("*.md"))
        self.assertEqual(len(loose_md_files), 0, f"Documentos soltos na raiz de hangar_v1: {loose_md_files}")

        # 3. Invariante: Zero arquivos soltos fora das 11 seções canônicas na raiz do Vault
        vault_entries = sorted([p.name for p in self.vault_dir.iterdir() if p.name != ".obsidian"])
        expected_vault_entries = sorted([
            "CAPABILITIES", "COCKPITS", "EXTERNAL", "GOVERNANCE", "INDEX.md",
            "INTELLIGENCE", "MACHINES", "PLANT", "PORTS", "PRODUCTS", "TRACE", "WORLD"
        ])
        self.assertEqual(vault_entries, expected_vault_entries, f"Entradas não canônicas na raiz do Vault: {vault_entries}")

        # 4. Invariante: broken_links == 0
        index_text = (self.vault_dir / "INDEX.md").read_text(encoding="utf-8")
        link_matches = re.findall(r"\[\[([^\|\]]+)(?:\|[^\|\]]+)?\]\]", index_text)
        broken = []
        for lk in link_matches:
            target_md = self.vault_dir / f"{lk}.md"
            target_dir = self.vault_dir / lk
            if not target_md.exists() and not target_dir.exists():
                broken.append(lk)
        self.assertEqual(len(broken), 0, f"Links quebrados no Vault INDEX: {broken}")



    def test_07_az000_owner_intent_depth_e2e(self):
        """Validação end-to-end do circuito funcional AZ000 OWNER_INTENT com caminhos válidos e fail-closed."""
        from hangar_v1.az000_governance.owner_intent.circuit import OwnerIntentCircuit
        from hangar_v1.az000_governance.owner_intent.contracts import OwnerRawIntent, SealedIntentContract
        from hangar_v1.az000_governance.owner_intent.ports import (
            PORT_OWNER_INTENT_INGEST,
            PORT_INTENT_HANDOFF_N01,
            PORT_PLANNER_N01_RECEIVE
        )

        # Caso 1: Caminho Válido (ACCEPT -> SEAL -> HANDOFF)
        valid_raw = {
            "call_id": "CALL-E2E-TEST-001",
            "owner_id": "OWNER",
            "action": "CREATE_FEATURE",
            "scope": "hangar_v1/az000_governance/owner_intent",
            "directives": ["SPEC_FIRST", "FAIL_CLOSED"],
            "mode": "LOCAL_CHAR_SLM_ONLY; ANTIGRAVITY_OBSERVE_ONLY",
            "route": "N01>N02>HERMES>N03>N10>N09>N08>N07",
        }
        res_ok = OwnerIntentCircuit.execute_full_pipeline(valid_raw)
        self.assertEqual(res_ok["status"], "SUCCESS")
        self.assertEqual(res_ok["stage"], "HANDOFF_COMPLETED")
        self.assertTrue(res_ok["validation"]["is_valid"])
        self.assertEqual(res_ok["validation"]["verdict"], "ACCEPT")
        self.assertIsNotNone(res_ok["sealed_contract"])
        self.assertIsNotNone(res_ok["handoff_envelope"])
        self.assertEqual(res_ok["handoff_envelope"]["source_port"], PORT_INTENT_HANDOFF_N01)
        self.assertEqual(res_ok["handoff_envelope"]["target_port"], PORT_PLANNER_N01_RECEIVE)

        # Caso 2: Falha por Campos Críticos Ausentes (REJECT_INVALID_SCHEMA)
        invalid_raw = {"call_id": "CALL-FAIL-001"}
        res_inv = OwnerIntentCircuit.execute_full_pipeline(invalid_raw)
        self.assertEqual(res_inv["status"], "FAILED")
        self.assertEqual(res_inv["stage"], "NORMALIZATION")
        self.assertEqual(res_inv["validation"]["verdict"], "REJECT_INVALID_SCHEMA")
        self.assertIsNone(res_inv["handoff_envelope"])

        # Caso 3: Falha por Emissor Não Autorizado (REJECT_UNAUTHORIZED)
        unauth_raw = {
            "call_id": "CALL-UNAUTH-001",
            "owner_id": "MALICIOUS_AGENT",
            "action": "MUTATE_CODE",
            "scope": "hangar_v1/az000_governance",
        }
        res_unauth = OwnerIntentCircuit.execute_full_pipeline(unauth_raw)
        self.assertEqual(res_unauth["status"], "BLOCKED")
        self.assertEqual(res_unauth["stage"], "VALIDATION")
        self.assertEqual(res_unauth["validation"]["verdict"], "REJECT_UNAUTHORIZED")
        self.assertIsNone(res_unauth["handoff_envelope"])

        # Caso 4: Bloqueio por Diretiva Ambígua (HOLD_INCONCLUSIVE)
        ambiguous_raw = {
            "call_id": "CALL-AMBIGUOUS-001",
            "owner_id": "OWNER",
            "action": "EXPLORE_OPTIONS",
            "scope": "hangar_v1/az000_governance",
            "directives": ["Talvez possamos mudar a arquitetura se possível."],
        }
        res_amb = OwnerIntentCircuit.execute_full_pipeline(ambiguous_raw)
        self.assertEqual(res_amb["status"], "BLOCKED")
        self.assertEqual(res_amb["stage"], "VALIDATION")
        self.assertEqual(res_amb["validation"]["verdict"], "HOLD_INCONCLUSIVE")
        self.assertIsNone(res_amb["handoff_envelope"])

        # Caso 5: Detecção de Adulteração de Contrato (TAMPER_DETECTED)
        contract_obj = SealedIntentContract(
            schema="AZ000-OWNER-INTENT-SEALED-CONTRACT-1",
            contract_id="CONTRACT-TAMPER-001",
            call_id="CALL-TAMPER",
            owner_id="OWNER",
            action="RUN",
            scope="hangar_v1",
            directives=["NONE"],
            mode="MODE",
            route="ROUTE",
            created_at_iso="2026-09-02T00:00:00Z",
            contract_sha256="fake_corrupted_hash_9999",
            validation_verdict="ACCEPT",
        )
        env_tamper, tamper_err = OwnerIntentCircuit.handoff_to_planner_n01(contract_obj)
        self.assertIsNone(env_tamper)
        self.assertIn("FALHA DE SEGURANÇA", tamper_err)


if __name__ == "__main__":
    unittest.main()
