# T-CHAR-PLANNER-CONTRACT-001: Contrato Canônico e Vertical Mínima do CHAR-PLANNER-01 (Nível 01)

- **CARD_ID:** `t_char_planner_contract_01`
- **STATUS:** `archived`
- **PRIORITY:** `1`
- **CREATED_AT:** `1788262714`
- **COMPLETED_AT:** `1788262836`

## Descrição
Contrato Canônico e Primeira Vertical Mínima do Nível 01 (CHAR-PLANNER-01):
Módulo: CHAR-PLANNER-01 (Planejador Determinístico de Intenções Autorizadas)
Porta: P-PLAN-01 (PLANNING-REQUEST-1 -> PLAN-INPUT-1)
Downstream: OWNER (P-PLANNING-REQUEST-01)
Upstream: CHAR-TASK-DECOMPOSER-01 (Nível 02 / P-DECOMPOSE-01)
Artefato Contrato: MOCK-TERRAIN/CHAR_PLANNER_01_CONTRATO.md
Artefato Núcleo: MOCK-TERRAIN/bridges/char_planner.py
Suíte de Testes: MOCK-TERRAIN/bridges/test_char_planner_vertical.py
Estado: review (T4 Técnico / Vertical Implementada e Testada)

## Metadados Fatuais
```json
{
  "card_id": "t_char_planner_contract_01",
  "contract_artifact": "MOCK-TERRAIN/CHAR_PLANNER_01_CONTRATO.md",
  "core_artifact": "MOCK-TERRAIN/bridges/char_planner.py",
  "test_suite": "MOCK-TERRAIN/bridges/test_char_planner_vertical.py",
  "contract_sha256": "19cea35b01a05e3d27be2128d5c677746b56d9b8963edd428d2cd6b443e85e96",
  "core_sha256": "49fc075c9f57563958decdb54de961eb671afc46649f3eb86d02986073293810",
  "test_sha256": "5a13616697e3370d37b095e3dff6e054008c6949479761560f43616146cd8cf4",
  "trust_level": "T5",
  "audit_status": "ARCHITECTURALLY_HOMOLOGATED_T5",
  "level": "N01",
  "module": "CHAR-PLANNER-01",
  "port": "P-PLAN-01",
  "tests_passed": "10/10",
  "exit_code": 0,
  "state": "HOMOLOGADO EM T5 ARQUITETURAL",
  "t5_call_id": "CALL-CHAR-N01-T5-PROMOTION-001",
  "t5_promoted_at": 1788262836
}
```
