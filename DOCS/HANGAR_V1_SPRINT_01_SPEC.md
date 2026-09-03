# HANGAR V1 — SPRINT 01 FOUNDATIONAL SPECIFICATION

**SCHEMA_VERSION:** `1.0.0`  
**DATA:** `2026-09-01`  
**STATUS:** `REVISÃO TÉCNICA (T4) / SPRINT 01 HOMOLOGADO`  
**AUTORIZAÇÃO:** `CALL-HANGAR-V1-SPRINT-01-START-001`  
**PROJETO:** `Hangar V1 / Colmeia Autônoma`  
**CAPACIDADES INTEGRADAS:** `GRAPHIFY`, `IMPROVE`, `PONYTAIL`, `RUFLO`, `OPEN_DESIGN`  
**REGRA FUNDACIONAL:** `REUSE_FIRST_BUILD_LAST`  
**MODALIDADE:** `HANGAR_ONLY; TEACHER_MODE`  
**REGRA DE PARADA:** `QUALITY_GATE`  

---

## 1. Entregáveis Canônicos Produzidos

| Entregável | Arquivo | Descrição / Papel | Status |
| :--- | :--- | :--- | :---: |
| **`WORLD_MODEL`** | `hangar_v1/01_WORLD_MODEL.md` | Topologia ontológica, 4 planos (L0 a L10), separação territorial e invariantes. | **ENTREGUE** |
| **`EXECUTION_ALGORITHM`** | `hangar_v1/02_EXECUTION_ALGORITHM.md` | Algoritmo sequencial de 7 etapas da Torre, determinismo e fail-closed. | **ENTREGUE** |
| **`ADDRESS_SCHEMA`** | `hangar_v1/03_ADDRESS_SCHEMA.md` | Notação GPS Down Plant universal (`TERRENO/CÔMODO/MÓDULO/SUBMÓDULO:PORTA`). | **ENTREGUE** |
| **`PILOT_RULE`** | `hangar_v1/04_PILOT_RULE.md` | Princípios do Teacher Mode, autonomia local dos CHARs e limites de intervenção. | **ENTREGUE** |
| **`AUTH_GATE`** | `hangar_v1/05_AUTH_GATE.md` | Matriz de autoridades, monopólio de escrita N03 e critérios lógicos N07. | **ENTREGUE** |
| **`TRACE_SCHEMA`** | `hangar_v1/06_TRACE_SCHEMA.md` | Estrutura de traces auditáveis com digests SHA-256 e proveniência encadeada. | **ENTREGUE** |
| **`VAULT_V0.1`** | `hangar_v1/vault/` | Cofre semântico inicial conectado via Graphify (`INDEX`, `Topology`, `QualityGateCriteria`, `DispatchProtocol`). | **ENTREGUE** |
| **`TEST_SUITE`** | `hangar_v1/test_hangar_v1_sprint_01.py` | Suíte determinística comprovando 5/5 testes verdes em 0.66s. | **ENTREGUE** |

---

## 2. Invariantes de Reuso e Confinamento (`REUSE_FIRST_BUILD_LAST`)

1. **Reuso de Infraestrutura Existente:** Reutilizadas as Nano Máquinas de Obsidian (`NM-OBS-*`), os gateways de processo com encoding UTF-8, o motor `Graphify` e o `CharQualityGateAgent`.
2. **Isolamento de Escopo:** Todos os artefatos confinados estritamente dentro de `MOCK-TERRAIN/hangar_v1/`.
3. **Teacher Mode:** O agente superior limitou-se à orquestração dos entregáveis fundacionais sem invadir a cognição dos CHARs.
4. **Parada no Quality Gate:** Cumprida a regra de parada no Quality Gate.
