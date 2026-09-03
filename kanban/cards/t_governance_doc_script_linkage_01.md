# T-GOVERNANCE-DOC-SCRIPT-LINKAGE-01: Rastreabilidade Bidirecional Doc-Script em GOVERNANCE.md

- **CARD_ID:** `t_governance_doc_script_linkage_01`
- **STATUS:** `done`
- **PRIORITY:** `1`
- **CREATED_AT:** `1788322405`
- **COMPLETED_AT:** `1788356527`

## Descrição
Rastreabilidade bidirecional entre regras de governança e implementações reais:
- Adição de referências canônicas a scripts, bridges, nanomaquinas e testes em cada seção.
- Registro de IMPLEMENTATION_GAP onde aplicável sem invenção de caminhos.
- Preservação estrita da estrutura monolítica de GOVERNANCE.md e da navegação Obsidian.
- Target: hangar_v1/vault/GOVERNANCE/GOVERNANCE.md
- Rota: N01 -> N02 -> Hermes -> N03 -> N10 -> N08 -> N07

## Metadados Fatuais
```json
{
  "card_id": "t_governance_doc_script_linkage_01",
  "call_id": "CALL-GOVERNANCE-DOC-SCRIPT-LINKAGE-001",
  "target": "C:\\Users\\PICHAU\\syntheon_adk\\hangar_v1\\vault\\GOVERNANCE\\GOVERNANCE.md",
  "workspace_kind": "syntheon_adk",
  "status": "GOVERNANCE_DOC_SCRIPT_LINKAGE_DONE",
  "trust_level": "T5",
  "quality_gate_status": "QUALITY_GATE_PASS",
  "recommendation": "ADVANCE",
  "eligible_for_promotion": true,
  "verifier_sha256": "bfe8d6b8d57ac6d372e11e8dcfcad16ff8697960a88aabcf45aa8a086c0ba3b8",
  "security_sha256": "a4b470a16a41c7336295b4e534f6b83223b5dfe3c9accef0de656ac1b282815f",
  "verified_paths_count": 18,
  "implementation_gaps": [
    "Cedar standalone daemon is executed in-process via Python/Rust bridge contracts.",
    "OPA HTTP daemon is intentionally disabled locally in favor of deterministic CharQualityGateAgent in-process evaluation."
  ],
  "audit_status": "HOMOLOGATED_DONE_T5",
  "promoted_to_done_at": 1788356527,
  "final_status": "DONE"
}
```
