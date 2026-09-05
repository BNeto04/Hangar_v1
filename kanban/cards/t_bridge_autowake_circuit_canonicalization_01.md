# T-BRIDGE-AUTOWAKE-CIRCUIT-CANONICALIZATION-01: Reparo da Ponte, Tolerância a Envelopes Compactos e Autowake Durável

- **CARD_ID:** `t_bridge_autowake_circuit_canonicalization_01`
- **STATUS:** `in_progress`
- **PRIORITY:** `0`
- **CREATED_AT:** `2026-09-05T08:52:05.538011-03:00`
- **COMPLETED_AT:** `null`

## Descrição
Execução da Workstream A de CG-000146 e reconciliação de CG-000145:
1. Parser compatível com envelope longo e compacto.
2. Restauração do Webhook/Cloudflare e polling como fallback.
3. Estruturação canônica em runtime/bridge/ (inbox, outbox, journal, state, logs).
4. Dedupe atômico compartilhado e autowake durável.

## Metadados Fatuais
```json
{
  "call_id": "CALL-HANGAR-BRIDGE-AUTOWAKE-AND-TERRAIN-CARTOGRAPHY-001",
  "reply_to": "CG-000146",
  "dp_project": "Hangar_v1",
  "phase": "P0_BRIDGE_AUTOWAKE",
  "dp_room": "EXTERNAL",
  "dp_module": "BRIDGE",
  "dp_submodule": "CIRCUIT",
  "dp_port": "P-EXT-BRIDGE-01",
  "rules_applied": [
    "R-DOM-001",
    "R-DOM-002",
    "R-DOM-005",
    "R-DOM-006",
    "R-DOM-007"
  ]
}
```
