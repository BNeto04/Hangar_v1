# T-HANGAR-INTELLIGENCE-ROOM-COMPLETION-01: Orquestrador Tipado de Agentes e Fechamento do Cômodo INTELLIGENCE (Tier 7)

- **CARD_ID:** `t_hangar_intelligence_room_completion_01`
- **STATUS:** `in_progress`
- **PRIORITY:** `1`
- **CREATED_AT:** `2026-09-04T23:56:08.878605-03:00`
- **COMPLETED_AT:** `null`

## Descrição
Consolidação canônica do cômodo INTELLIGENCE (Tier 7): orquestrador tipado de agentes cognitivos (CHARs N01 a N10), raciocínio estruturado sem alucinação e verificação formal de premissas.
Originado por CG-000137 (CALL-HANGAR-NEXT-ROOM-INTELLIGENCE-001).

Diretrizes:
1. Trabalhar estritamente no cômodo INTELLIGENCE (Tier 7).
2. Mapear dependências a montante (GOVERNANCE, WORLD, PLANT, PORTS, CAPABILITIES, MACHINES), todas COMPLETE.
3. Consolidar especificação canônica em DOCS/27_INTELLIGENCE_ROOM_SPEC.md.
4. Implementar módulo az000_governance/intelligence/ (modelos, orquestrador tipado e validação anti-alucinação).
5. Manter Vault (vault/INTELLIGENCE/INDEX.md) sincronizado e referenciando a ARCA sem duplicação.
6. Executar testes N08/N06/N07 e fechar cômodo com ROOM_STATUS=COMPLETE.

## Metadados Fatuais
```json
{
  "call_id": "CALL-HANGAR-NEXT-ROOM-INTELLIGENCE-001",
  "reply_to": "CG-000137",
  "dp_project": "Hangar_v1",
  "dp_room": "INTELLIGENCE",
  "dp_module": "ORCHESTRATION",
  "dp_submodule": "COGNITIVE_AGENTS",
  "dp_port": "P-INTEL-ORCHESTRATOR-01",
  "tier": 7,
  "dependencies": [
    "GOVERNANCE",
    "WORLD",
    "PLANT",
    "PORTS",
    "CAPABILITIES",
    "MACHINES"
  ],
  "upstream_status": "COMPLETE",
  "room_status": "IN_PROGRESS",
  "rules_applied": [
    "R-DOM-005",
    "R-DOM-006"
  ]
}
```
