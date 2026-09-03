# T-CHAR-QUALITY-GATE-CONTRACT-001: Contrato Canônico Reconciliado do CHAR-QUALITY-GATE-01 (Nível 07)

- **CARD_ID:** `t_char_quality_gate_contract_01`
- **STATUS:** `archived`
- **PRIORITY:** `0`
- **CREATED_AT:** `1788201381`
- **COMPLETED_AT:** `1788268531`

## Descrição
Contrato Canônico Reconciliado do Nível 07 (CHAR-QUALITY-GATE-01):
Módulo: CHAR-QUALITY-GATE-01 (Avaliador e Agregador Determinístico de Evidências)
Porta: P-QUALITY-GATE-DECISION-01 (QUALITY_GATE_INPUT-1 -> QUALITY_GATE_DECISION-1)
Recorte Inicial: Exige EXATAMENTE 1 SECURITY_REVIEW válido (N06 / P-SECURITY-REVIEW-01)
Comportamento Mínimo: 1 SECURITY_REVIEW (PASS) -> QUALITY_GATE_PASS / ADVANCE (eligible: true)
Artefato: MOCK-TERRAIN/CHAR_QUALITY_GATE_01_CONTRATO.md
Estado: done (T5 Homologado)

## Metadados Fatuais
```json
{
  "card_id": "t_char_quality_gate_contract_01",
  "contract_artifact": "MOCK-TERRAIN/CHAR_QUALITY_GATE_01_CONTRATO.md",
  "core_artifact": "MOCK-TERRAIN/bridges/char_quality_gate.py",
  "test_suite": "MOCK-TERRAIN/bridges/test_char_quality_gate_vertical.py",
  "contract_sha256": "a8b83105bff6f8c687ed887849f4b615cc3dd65b495f433011fb884a8300a7f4",
  "core_sha256": "45f1bd697ecbd2b89b7d3b322ce7c12dac6d4af52c922bab9357a1b7b38766d9",
  "test_sha256": "1e8fab397c1a340207ba6b17c7513ffb2ca008d6019c9a26cb463e0ee84dbf88",
  "trust_level": "T5",
  "audit_status": "ARCHITECTURALLY_HOMOLOGATED_T5",
  "level": "N07",
  "module": "CHAR-QUALITY-GATE-01",
  "port": "P-QUALITY-GATE-DECISION-01",
  "tests_passed": "28/28",
  "exit_code": 0,
  "state": "HOMOLOGADO EM T5 ARQUITETURAL",
  "t5_call_id": "CALL-CHAR-QUALITY-GATE-N07-T5-001",
  "t5_promoted_at": 1788268531
}
```
