# T-CHAR-CURATOR-HARNESS-001: Implementar e Provar o Harness de Ligação Modelo -> Curator Determinístico (Rev A)

- **CARD_ID:** `t_char_curator_harness_01`
- **STATUS:** `archived`
- **PRIORITY:** `high`
- **CREATED_AT:** `1788169340`
- **COMPLETED_AT:** `1788261958`

## Descrição
Implementação e homologação da fronteira determinística do CHAR-CURATOR-01 (Nível 09).
Superfície Pública: estritamente {intent, target_artifact, terrain_root} via Porta P-CHAR-CURATOR-TOOL-01.
Adaptador de Harness: bridges/char_curator_harness.py
Suíte de Testes: bridges/test_char_curator_harness.py (4/4 testes passando, rejeição de envelope_dir comprovada)
Dependência Downstream: CharCuratorAgent -> CharObsidianAgent -> Graphify
Auditoria: audit_char_curator_harness_result.json (T4 Homologado Tecnicamente)

## Metadados Fatuais
```json
{
  "card_id": "t_char_curator_harness_01",
  "contract_artifact": "MOCK-TERRAIN/CHAR_CURATOR_01_CONTRATO.md",
  "adapter_file": "MOCK-TERRAIN/bridges/char_curator_harness.py",
  "test_suites": [
    "MOCK-TERRAIN/bridges/test_char_curator_graphify_vertical.py",
    "MOCK-TERRAIN/bridges/test_char_curator_harness.py",
    "MOCK-TERRAIN/bridges/test_char_verifier_curator_vertical.py"
  ],
  "trust_level": "T5",
  "audit_status": "ARCHITECTURALLY_HOMOLOGATED_T5",
  "level": "N09",
  "module": "CHAR-CURATOR-01",
  "submodule": "Harness de Liga\u00e7\u00e3o Modelo -> Curator Determin\u00edstico",
  "port": "P-CHAR-CURATOR-TOOL-01",
  "tests_passed": "12/12 (graphify + harness + verifier-curator)",
  "exit_code": 0,
  "state": "HOMOLOGADO EM T5 ARQUITETURAL",
  "t5_call_id": "CALL-CHAR-N09-HARNESS-T5-PROMOTION-001",
  "t5_promoted_at": 1788261958
}
```
