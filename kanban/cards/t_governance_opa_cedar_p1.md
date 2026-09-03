# T-GOVERNANCE-OPA-CEDAR-P1: Auditoria Técnica de OPA e Cedar para Governança

- **CARD_ID:** `t_governance_opa_cedar_p1`
- **STATUS:** `done`
- **PRIORITY:** `1`
- **CREATED_AT:** `1788319981`
- **COMPLETED_AT:** `1788356527`

## Descrição
Auditoria comparativa e arquitetural de OPA e Cedar para a camada de Governança do Hangar V1:
- Avaliação de instalação, localidade, licença e modelo de execução.
- Decisão: Cedar para AUTHORITY (ADOPT) e OPA para QUALITY_GATES (COMPOSE/ADOPT).
- Definição de portas e contratos de interface.
- Target: hangar_v1/vault/GOVERNANCE
- Rota: N01 -> N02 -> Hermes -> N08 -> N07

## Metadados Fatuais
```json
{
  "card_id": "t_governance_opa_cedar_p1",
  "call_id": "CALL-GOVERNANCE-OPA-CEDAR-001-P1",
  "part": "PART_1",
  "target": "C:\\Users\\PICHAU\\syntheon_adk\\hangar_v1\\vault\\GOVERNANCE",
  "workspace_kind": "syntheon_adk",
  "status": "AUDIT_COMPLETED",
  "decisions": {
    "CEDAR": {
      "decision": "ADOPT",
      "layer": "AUTHORITY",
      "license": "Apache-2.0",
      "rationale": "Linguagem declarativa expressiva e segura para RBAC/ABAC, suporte nativo a entidades/a\u00e7\u00f5es e bindings locais em Python/Rust sem overhead de daemon.",
      "proposed_ports": [
        "P-CEDAR-AUTHORITY-01",
        "P-CEDAR-POLICY-CHECK-01"
      ]
    },
    "OPA": {
      "decision": "ADOPT",
      "layer": "QUALITY_GATES",
      "license": "Apache-2.0",
      "rationale": "Motor can\u00f4nico de delibera\u00e7\u00e3o estrutural (Rego) sobre envelopes JSON e \u00e1rvores de evid\u00eancias de gates fail-closed.",
      "proposed_ports": [
        "P-OPA-GATE-EVAL-01",
        "P-OPA-CONFORMANCE-01"
      ]
    }
  },
  "risks_and_dependencies": [
    "Isolamento: Execu\u00e7\u00e3o estritamente em processo ou bin\u00e1rio local (zero chamadas de rede externa).",
    "Compatibilidade: Bindings Python determin\u00edsticos (cedarpy / open-policy-agent CLI).",
    "Fail-Closed: Falha de parse ou indisponibilidade de pol\u00edtica resulta em BLOCK imediato."
  ],
  "quality_gate_status": "QUALITY_GATE_PASS",
  "recommendation": "ADVANCE",
  "eligible_for_promotion": true,
  "trust_level": "T5",
  "audit_status": "HOMOLOGATED_DONE_T5",
  "promoted_to_done_at": 1788356527,
  "final_status": "DONE"
}
```
