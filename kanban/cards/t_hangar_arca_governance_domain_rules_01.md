# T-HANGAR-ARCA-GOVERNANCE-DOMAIN-RULES-01: Módulo ARCA em Governança e Ordem Canônica de Cômodos

- **CARD_ID:** `t_hangar_arca_governance_domain_rules_01`
- **STATUS:** `in_progress`
- **PRIORITY:** `high`
- **CREATED_AT:** `2026-09-04T23:19:59.245417-03:00`
- **COMPLETED_AT:** `null`

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
  "room_order_policy": "STRICT_SEQUENTIAL_CLOSED_BEFORE_NEXT"
}
```
