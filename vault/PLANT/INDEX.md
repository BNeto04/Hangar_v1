# 🏭 CÔMODO PLANT (TIER 3) — TOPOLOGIA FÍSICA & INFRAESTRUTURA DE WORKSPACES

**ID DO CÔMODO:** `ROOM-03`  
**TIER:** `3`  
**ENDEREÇO DOWN PLANT:** `Hangar_v1/PLANT/TOPOLOGY/WORKSPACES:P-PLANT-TOPOLOGY-LAYOUT-01`  
**DEPENDÊNCIAS A MONTANTE:** `[[GOVERNANCE/INDEX|GOVERNANCE]]` (Status: `COMPLETE`) e `[[WORLD/INDEX|WORLD]]` (Status: `COMPLETE`)  
**REGRAS DE DOMÍNIO APLICÁVEIS:** `[[GOVERNANCE/ARCA_DOMAIN_RULES|ARCA]]` (`R-DOM-005: ROOM_BY_ROOM_ORDER`, `R-DOM-006: SINGLE_SOURCE_OF_TRUTH_ARCA`)  
**ESPECIFICAÇÕES TÉCNICAS:** `[[../DOCS/03_ADDRESS_SCHEMA.md|03_ADDRESS_SCHEMA.md]]` e `[[../DOCS/23_PLANT_ROOM_SPEC.md|23_PLANT_ROOM_SPEC.md]]`  
**UTILITÁRIO CANÔNICO:** `az000_governance/plant/addressing.py`  

---

## 1. Missão do Cômodo
O cômodo **PLANT** estabelece a infraestrutura física, organização territorial de pastas, confinamento de agentes e convenções de endereçamento GPS Down Plant (`TERRENO/COMODO/MODULO/SUBMODULO:PORTA`).

---

## 2. Estrutura Física do Vault e Workspaces
O território `Hangar_v1` organiza-se em diretórios estritamente segregados:
- `vault/`: Repositório de documentação canônica (11 seções top-level fundamentais).
- `DOCS/`: Especificações normativas e arquiteturais por cômodo.
- `az000_governance/`: Módulos de código soberano (`owner_intent`, `arca`, `plant`).
- `bridge/`: Adaptadores de borda e conectores (Relay :8765, Webhook :8766, Watchdog, Sentinela Telegram).
- `runtime/`: Armazenamento de contratos selados (`sealed_contracts/`) e estados voláteis.
- `tests/`: Suítes de testes determinísticas (N08/N06/N07).
- `kanban/`: Espelho versionado do Hermes Kanban (`kanban_state.json` e `cards/*.md`).

---

## 3. Confinamento de Workspaces & Permissões
- **N03 Executor:** Monopólio físico exclusivo de mutação no produto (`write_tools` ativas).
- **Lentes (N04/N05/N06/N08):** Confinamento estrito somente-leitura (`platform_toolsets.cli: []`).
- **Daemons de Loopback:** Portas `8765` (inbound wake) e `8766` (webhook receiver) isoladas em `127.0.0.1`.
