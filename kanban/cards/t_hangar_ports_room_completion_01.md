# T-HANGAR-PORTS-ROOM-COMPLETION-01: Registro de Portas, Contratos de Interface e Fechamento do Cômodo PORTS (Tier 4)

- **CARD_ID:** `t_hangar_ports_room_completion_01`
- **STATUS:** `in_progress`
- **PRIORITY:** `1`
- **CREATED_AT:** `2026-09-04T23:40:38.346755-03:00`
- **COMPLETED_AT:** `null`

## Descrição
Consolidação canônica do cômodo PORTS (Tier 4): catálogo de portas, contratos tipados de envelope e protocolos de despacho assíncrono.
Originado por CG-000134 (CALL-HANGAR-NEXT-ROOM-PORTS-001).

Diretrizes:
1. Trabalhar estritamente no cômodo PORTS (Tier 4).
2. Mapear dependências a montante (GOVERNANCE, WORLD, PLANT), todas COMPLETE.
3. Consolidar especificação canônica em DOCS/24_PORTS_ROOM_SPEC.md.
4. Implementar módulo az000_governance/ports/ (envelope tipado e registro de portas com resolução GPS).
5. Manter Vault (vault/PORTS/INDEX.md) sincronizado e referenciando a ARCA sem duplicação.
6. Executar testes N08/N06/N07 e fechar cômodo com ROOM_STATUS=COMPLETE.

## Metadados Fatuais
```json
{
  "call_id": "CALL-HANGAR-NEXT-ROOM-PORTS-001",
  "reply_to": "CG-000134",
  "dp_project": "Hangar_v1",
  "dp_room": "PORTS",
  "dp_module": "REGISTRY",
  "dp_submodule": "DISPATCHER",
  "dp_port": "P-PORTS-ROUTER-01",
  "tier": 4,
  "dependencies": [
    "GOVERNANCE",
    "WORLD",
    "PLANT"
  ],
  "upstream_status": "COMPLETE",
  "room_status": "IN_PROGRESS",
  "rules_applied": [
    "R-DOM-005",
    "R-DOM-006"
  ]
}
```
