# T-HANGAR-ARCA-GOVERNANCE-DOMAIN-RULES-01: Módulo ARCA em Governança e Ordem Canônica de Cômodos

- **CARD_ID:** `t_hangar_arca_governance_domain_rules_01`
- **STATUS:** `done`
- **PRIORITY:** `high`
- **CREATED_AT:** `2026-09-04T23:19:59.245417-03:00`
- **COMPLETED_AT:** `2026-09-04T23:29:07.797631-03:00`

## Descrição
Módulo ARCA em Governança (AZ000) e Política de Ordem de Cômodos.
Originado por CG-000129 (CALL-HANGAR-ROOM-SPECS-ARCA-DOMAIN-RULES-001).

Diretrizes:
1. SPECs passam a ser por CÔMODO.
2. Fechar completamente um cômodo antes de seguir ao próximo, respeitando dependências.
3. Antes de avançar, conferir dependências e manter documentação no Vault.
4. Em GOVERNANCA criar módulo ARCA.
5. ARCA contém UM arquivo canônico somente-leitura com TODAS as regras de domínio do projeto.
6. Módulos cobertos referenciam ARCA, sem duplicação de regras locais.

## Metadados Fatuais
```json
{
  "call_id": "CALL-HANGAR-ROOM-SPECS-ARCA-DOMAIN-RULES-001",
  "reply_to": "CG-000129",
  "dp_project": "Hangar_v1",
  "dp_room": "AZ000_GOVERNANCA_SOBERANIA",
  "dp_module": "ARCA",
  "dp_submodule": "DOMAIN_RULES",
  "dp_port": "P-GOV-ARCA-RULES-01",
  "rules_count": 7,
  "room_order_count": 11,
  "arca_sha256": "b44cc173dde350c195c38ef14533c141cbaf017f4006287400447b6dce893683",
  "final_state": "DONE",
  "pending_items": [
    "Homologa\u00e7\u00e3o formal do Propriet\u00e1rio para promo\u00e7\u00e3o definitiva em T5 (Done)",
    "Auditoria independente do Codex das regras e grafo de depend\u00eancias"
  ],
  "owner_directive_applied": "N\u00c3O PARAR O TRABALHO; registrar pend\u00eancia no cart\u00e3o e deixar em review",
  "closed_at": "2026-09-04T23:29:07.797631-03:00",
  "room_status": "COMPLETE",
  "closure_evidence": "30/30 unit & regression tests passing; SHA-256 contracts verified; zero gaps."
}
```
