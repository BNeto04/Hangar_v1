# T-HANGAR-DOCS-MOVE-CURATOR-DOWN-01: Movimentação de Documentos do Curator para hangar_v1/DOCS

- **CARD_ID:** `t_hangar_docs_move_curator_down_01`
- **STATUS:** `done`
- **PRIORITY:** `1`
- **CREATED_AT:** `1788357399`
- **COMPLETED_AT:** `1788424811`

## Descrição
Movimentação de artefatos documentais do Curator para a pasta DOCS existente no Hangar V1:
- Movimentação de curator_downplant.canvas, curator_downplant_graph.json e curator_graph.json para hangar_v1/DOCS.
- Preservação integral do conteúdo e integridade dos arquivos.
- Limpeza da raiz do Vault preservando estritamente as 11 seções top-level e o INDEX.md mestre.
- Validação determinística de zero links quebrados (fail-closed).
- Target: hangar_v1/DOCS
- Rota: N01 -> N02 -> Hermes -> N03 -> N10 -> N08 -> N07

## Metadados Fatuais
```json
{
  "card_id": "t_hangar_docs_move_curator_down_01",
  "call_id": "CALL-HANGAR-DOCS-MOVE-CURATOR-DOWN-001",
  "target": "C:\\Users\\PICHAU\\syntheon_adk\\hangar_v1\\DOCS",
  "workspace_kind": "syntheon_adk",
  "status": "DONE",
  "trust_level": "T5",
  "quality_gate_status": "QUALITY_GATE_PASS",
  "recommendation": "ADVANCE",
  "eligible_for_promotion": true,
  "verifier_sha256": "9abc26c29c67d8e70493eeca2137cde7347360ef135bcf6a03d1775ea7150746",
  "security_sha256": "d0325f0b7fef72fed8c293eaffc2329263063a6102f052cb2134271de064024f",
  "inventory": [],
  "broken_links": 0,
  "promoted_at": 1788424811
}
```
