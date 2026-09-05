# T-HANGAR-EXTERNAL-ROOM-COMPLETION-01: Pontes Autenticadas, Fronteiras Periféricas e Fechamento do Cômodo EXTERNAL (Tier 8)

- **CARD_ID:** `t_hangar_external_room_completion_01`
- **STATUS:** `done`
- **PRIORITY:** `1`
- **CREATED_AT:** `2026-09-05T00:00:02.417491-03:00`
- **COMPLETED_AT:** `2026-09-05T00:02:11.306587-03:00`

## Descrição
Consolidação canônica do cômodo EXTERNAL (Tier 8): pontes externas com autenticação (GitHub Webhook HMAC SHA-256, PR Relay, Telegram Bot, Cloudflare Tunnel), protocolo fail-closed em indisponibilidade e isolamento de fronteiras.
Originado por CG-000138 (CALL-HANGAR-NEXT-ROOM-EXTERNAL-001).

Diretrizes:
1. Trabalhar estritamente no cômodo EXTERNAL (Tier 8).
2. Mapear dependências a montante (GOVERNANCE, WORLD, PLANT, PORTS, CAPABILITIES, MACHINES, INTELLIGENCE), todas COMPLETE.
3. Consolidar especificação canônica em DOCS/28_EXTERNAL_ROOM_SPEC.md.
4. Implementar módulo az000_governance/external/ (gateway unificado, modelos tipados e fail-closed).
5. Manter Vault (vault/EXTERNAL/INDEX.md) sincronizado e referenciando a ARCA sem duplicação.
6. Executar testes N08/N06/N07 e fechar cômodo com ROOM_STATUS=COMPLETE.

## Metadados Fatuais
```json
{
  "call_id": "CALL-HANGAR-NEXT-ROOM-EXTERNAL-001",
  "reply_to": "CG-000138",
  "dp_project": "Hangar_v1",
  "dp_room": "EXTERNAL",
  "dp_module": "INTEGRATIONS",
  "dp_submodule": "GATEWAY",
  "dp_port": "P-EXT-GATEWAY-01",
  "tier": 8,
  "dependencies": [
    "GOVERNANCE",
    "WORLD",
    "PLANT",
    "PORTS",
    "CAPABILITIES",
    "MACHINES",
    "INTELLIGENCE"
  ],
  "upstream_status": "COMPLETE",
  "room_status": "COMPLETE",
  "rules_applied": [
    "R-DOM-002",
    "R-DOM-005",
    "R-DOM-006"
  ],
  "completed_at": "2026-09-05T00:02:11.306587-03:00",
  "closure_criteria_met": [
    "Transportes orientados a eventos comprovados",
    "Deduplica\u00e7\u00e3o e HMAC SHA-256 ativos"
  ],
  "tests_passed": "6/6 tests/test_external_room.py PASS; 61/61 full regression PASS",
  "next_eligible_room": "TRACE (Tier 9)"
}
```
