# HANGAR V1 — 25. ESPECIFICAÇÃO DO CÔMODO CAPABILITIES (TIER 5)

**STATUS:** `COMPLETE`  
**DATA:** `2026-09-04`  
**AUTOR:** `Down Plant Technical Executor`  
**AUDITORIA:** `Codex / ChatGPT (CG-000135 / CALL-HANGAR-NEXT-ROOM-CAPABILITIES-001)`  
**ORDEM DE CÔMODOS:** Tier 5 de 11  

---

## 1. Propósito e Fronteiras

O cômodo **CAPABILITIES** fornece os motores operacionais fundamentais da colmeia Hangar V1. Ele define o catálogo canônico de competências (`CapabilityDefinition`), assegura que todas as relações de dependência entre motores formem um DAG estritamente acíclico, e disponibiliza o motor `Graphify` para inspeção e garantia de integridade espacial do Vault.

---

## 2. Reconciliação Topológica e Invariantes ARCA

- **Invariante R-DOM-005 (ROOM_BY_ROOM_ORDER):**
  - Upstream concluído e validado: `GOVERNANCE (Tier 1)`, `WORLD (Tier 2)`, `PLANT (Tier 3)` e `PORTS (Tier 4)` estão com `ROOM_STATUS: COMPLETE`.
  - Cômodo ativo: `CAPABILITIES (Tier 5)` concluído com 100% dos motores mapeados, curadoria determinística verificada e testes passando.
  - Downstream habilitado: `MACHINES (Tier 6)` torna-se o próximo cômodo elegível.

- **Invariante R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA):**
  - As definições e critérios de encerramento seguem rigorosamente a tabela canônica `_CANONICAL_ROOMS` em `az000_governance/arca/canonical_domain_rules.py`.

---

## 3. Implementação Técnica (`az000_governance/capabilities/`)

1. **`CapabilityDefinition` & `CapabilityExecutionResult` (`models.py`):**
   - Estruturas imutáveis e auditáveis com rastreamento por hash SHA-256 e endereço GPS Down Plant.
2. **`CapabilityRegistry` (`registry.py`):**
   - Catálogo das 5 capacidades canônicas (`GRAPHIFY`, `OPEN_DESIGN`, `PONYTAIL`, `IMPROVE`, `RUFLO`).
   - Algoritmo DFS com stack de recursão para detecção e proibição automática de ciclos direcionados.
3. **`GraphifyEngine` (`graphify_engine.py`):**
   - Auditor determinístico de nós e arestas baseado na extração de wikilinks (`[[...]]`) e contagem de links órfãos no Vault.

---

## 4. Evidências de Validação (Gates N08 / N06 / N07)

- `tests/test_capabilities_room.py`: 6 testes unitários aprovados.
- Regressão do repositório: 43+ testes aprovados com código de saída 0.
- Cartão Hermes: `t_hangar_capabilities_room_completion_01` promovido para DONE (T5).
- Mirror de governança sincronizado em `kanban_mirror.json`.
