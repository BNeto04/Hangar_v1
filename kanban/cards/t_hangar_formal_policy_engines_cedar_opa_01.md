# T-HANGAR-FORMAL-POLICY-ENGINES-CEDAR-OPA-01: Motores Formais de Política (Cedar Authority & OPA Quality Gates)

- **CARD_ID:** `t_hangar_formal_policy_engines_cedar_opa_01`
- **STATUS:** `done`
- **PRIORITY:** `1`
- **CREATED_AT:** `2026-09-05T00:21:39.151573-03:00`
- **COMPLETED_AT:** `2026-09-05T00:23:44.332707-03:00`

## Descrição
Implementação dos motores canônicos de política declarativa formal para a Governança Plena do Hangar V1:
1. Motor Cedar de Autoridade (az000_governance/policy/cedar_engine.py): parsing declarativo permit/forbid, validação de principal/action/resource e avaliação determinística estrita fail-closed.
2. Motor OPA de Quality Gates (az000_governance/policy/opa_engine.py): avaliação determinística de regras Rego sobre envelopes tipados de evidências (TypedPortEnvelope) sem dependência de daemons de rede.
3. Resolução integral do Critério 2 do Roadtrace (GAP-001 e GAP-002).
Originado por CG-000143 (CALL-HANGAR-POST-CONVERGENCE-NEXT-001).

## Metadados Fatuais
```json
{
  "call_id": "CALL-HANGAR-POST-CONVERGENCE-NEXT-001",
  "reply_to": "CG-000143",
  "dp_project": "Hangar_v1",
  "phase": "FORMAL_POLICY_ENGINES",
  "dp_room": "GOVERNANCE",
  "dp_module": "POLICY",
  "dp_submodule": "CEDAR_OPA_ENGINES",
  "dp_port": "P-GOV-POLICY-01",
  "criterion_target": "ROADTRACE_CRITERION_2",
  "gaps_resolved": [
    "GAP-001",
    "GAP-002"
  ],
  "rules_applied": [
    "R-DOM-001",
    "R-DOM-002",
    "R-DOM-005",
    "R-DOM-006",
    "R-DOM-007"
  ],
  "phase_status": "COMPLETE",
  "completed_at": "2026-09-05T00:23:44.332707-03:00",
  "closure_criteria_met": [
    "Motor Cedar de Autoridade implementado e validado (R-DOM-001, permit/forbid, fail-closed)",
    "Motor OPA de Quality Gates implementado e validado (R-DOM-007, valida\u00e7\u00e3o SHA-256 de evid\u00eancias)",
    "Resolu\u00e7\u00e3o completa do Crit\u00e9rio 2 do Roadtrace (GAP-001 e GAP-002)"
  ],
  "tests_passed": "6/6 tests/test_policy_engines.py PASS; 92/92 full regression PASS",
  "next_phase": "SOVEREIGN_FINAL_HOMOLOGATION",
  "owner_decision_required": true
}
```
