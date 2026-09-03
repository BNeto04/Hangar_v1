# T-CHAR-TASK-DECOMPOSER-CONTRACT-001: Contrato Canônico e Vertical Mínima do CHAR-TASK-DECOMPOSER-01 (Nível 02)

- **CARD_ID:** `t_char_task_decomposer_contract_01`
- **STATUS:** `archived`
- **PRIORITY:** `1`
- **CREATED_AT:** `1788262405`
- **COMPLETED_AT:** `1788262526`

## Descrição
Contrato Canônico e Primeira Vertical Mínima do Nível 02 (CHAR-TASK-DECOMPOSER-01):
Módulo: CHAR-TASK-DECOMPOSER-01 (Decompositor Determinístico de Tarefas Autorizadas)
Porta: P-DECOMPOSE-01 (PLAN-INPUT-1 -> TASK-INPUT-1)
Downstream: CHAR-PLANNER-01 (Nível 01 / P-PLAN-01)
Upstream: CHAR-EXECUTOR-01 (Nível 03 / P-EXECUTE-01)
Artefato Contrato: MOCK-TERRAIN/CHAR_TASK_DECOMPOSER_01_CONTRATO.md
Artefato Núcleo: MOCK-TERRAIN/bridges/char_task_decomposer.py
Suíte de Testes: MOCK-TERRAIN/bridges/test_char_task_decomposer_vertical.py
Estado: review (T4 Técnico / Vertical Implementada e Testada)

## Metadados Fatuais
```json
{
  "card_id": "t_char_task_decomposer_contract_01",
  "contract_artifact": "MOCK-TERRAIN/CHAR_TASK_DECOMPOSER_01_CONTRATO.md",
  "core_artifact": "MOCK-TERRAIN/bridges/char_task_decomposer.py",
  "test_suite": "MOCK-TERRAIN/bridges/test_char_task_decomposer_vertical.py",
  "contract_sha256": "68ed9ec19178ff29131d2d3ca3f9d636477207d7bf5d4c51bfe9d8de486b0c30",
  "core_sha256": "b75e08da0481f36e53e1b0d96eaaf292164de5538a38ff3bccddc7d6e88f2b45",
  "test_sha256": "ef2345578ed73b9be18792ee270dd5af8dbfffdb1c7133b9b7c1294bae206a77",
  "trust_level": "T5",
  "audit_status": "ARCHITECTURALLY_HOMOLOGATED_T5",
  "level": "N02",
  "module": "CHAR-TASK-DECOMPOSER-01",
  "port": "P-DECOMPOSE-01",
  "tests_passed": "9/9",
  "exit_code": 0,
  "state": "HOMOLOGADO EM T5 ARQUITETURAL",
  "t5_call_id": "CALL-CHAR-N02-T5-PROMOTION-001",
  "t5_promoted_at": 1788262526
}
```
