# 🌍 CÔMODO WORLD (TIER 2) — ONTOLOGIA GLOBAL & MODELO ESPACIAL

**ID DO CÔMODO:** `ROOM-02`  
**TIER:** `2`  
**ENDEREÇO DOWN PLANT:** `Hangar_v1/WORLD/MODEL/SPATIAL_CANVAS:P-WORLD-CANVAS-NAV-01`  
**DEPENDÊNCIAS A MONTANTE:** `[[GOVERNANCE/INDEX|GOVERNANCE]]` (Status: `COMPLETE`)  
**REGRAS DE DOMÍNIO APLICÁVEIS:** `[[GOVERNANCE/ARCA_DOMAIN_RULES|ARCA]]` (`R-DOM-005: ROOM_BY_ROOM_ORDER`, `R-DOM-006: SINGLE_SOURCE_OF_TRUTH_ARCA`)  
**ARTEFATO VISUAL CENTRAL:** `[[WORLD/Master_World.canvas|Master_World.canvas]]`  
**ESPECIFICAÇÕES TÉCNICAS:** `[[../DOCS/01_WORLD_MODEL.md|01_WORLD_MODEL.md]]` e `[[../DOCS/22_WORLD_ROOM_SPEC.md|22_WORLD_ROOM_SPEC.md]]`  

---

## 1. Missão do Cômodo
O cômodo **WORLD** modela o universo operacional do Hangar V1, delimitando:
1. **Ontologia do Território:** Vault Obsidian estruturado nas 11 seções top-level fundamentais.
2. **Separação em 4 Planos:** Intenção (L0), Planejamento (L1-L2), Execução (L3) e Factual/Gates (L4-L10).
3. **Navegação Espacial:** O arquivo `Master_World.canvas` contendo 17 nós interconectados por 24 arestas sem nenhum link quebrado.

---

## 2. Invariantes do Cômodo WORLD
- **I-WLD-01 (Fechamento Sequencial):** O cômodo WORLD opera sobre a fundação soberana de `GOVERNANCE` (Tier 1), já formalmente fechada e auditada (`R-DOM-005`).
- **I-WLD-02 (Confinamento Territorial):** Todo artefato, documento ou código pertence unívocamente a um dos 11 cômodos canônicos da ARCA.
- **I-WLD-03 (Navegabilidade Íntegra):** Todo wikilink `[[...]]` no Canvas e nas seções do Vault deve resolver para um arquivo existente, mantendo zero links quebrados.

---

## 3. Estrutura de Navegação do Cômodo
- [[WORLD/Master_World.canvas|Master_World.canvas]] — Mapa visual espacial navegável em grade 2D.
- [[../INDEX|Índice Mestre do Hangar V1]] — Ponto de entrada canônico do Vault.
- [[../GOVERNANCE/ARCA_DOMAIN_RULES|ARCA - Regras de Domínio]] — Referência soberana de regras.
