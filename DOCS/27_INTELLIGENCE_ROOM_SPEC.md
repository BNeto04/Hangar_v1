# HANGAR V1 — 27. ESPECIFICAÇÃO DO CÔMODO INTELLIGENCE (TIER 7)

**STATUS:** `COMPLETE`  
**DATA:** `2026-09-04`  
**AUTOR:** `Down Plant Technical Executor`  
**AUDITORIA:** `Codex / ChatGPT (CG-000137 / CALL-HANGAR-NEXT-ROOM-INTELLIGENCE-001)`  
**ORDEM DE CÔMODOS:** Tier 7 de 11  

---

## 1. Propósito e Fronteiras

O cômodo **INTELLIGENCE** rege os agentes cognitivos autônomos e os processos de deliberação estruturada do Hangar V1. Ele estabelece o `TypedAgentOrchestrator`, assegurando contratos de personas imutáveis (CHARs N01 a N10) e impedindo que raciocínios especulativos ou alucinações de LLMs afetem o código de produção.

---

## 2. Reconciliação Topológica e Invariantes ARCA

- **Invariante R-DOM-005 (ROOM_BY_ROOM_ORDER):**
  - Upstream concluído e validado: `GOVERNANCE (Tier 1)`, `WORLD (Tier 2)`, `PLANT (Tier 3)`, `PORTS (Tier 4)`, `CAPABILITIES (Tier 5)` e `MACHINES (Tier 6)` estão com `ROOM_STATUS: COMPLETE`.
  - Cômodo ativo: `INTELLIGENCE (Tier 7)` concluído com orquestrador tipado, motor anti-alucinação e testes aprovados.
  - Downstream habilitado: `EXTERNAL (Tier 8)` torna-se o próximo cômodo elegível.

- **Invariante R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA):**
  - Os critérios canônicos de fechamento derivam da tabela `_CANONICAL_ROOMS` em `az000_governance/arca/canonical_domain_rules.py`.

---

## 3. Implementação Técnica (`az000_governance/intelligence/`)

1. **`CognitiveAgentDefinition` & `AgentThoughtChain` (`models.py`):**
   - Agentes cognitivos com níveis operacionais formais (N01 a N10) e portas Down Plant tipadas.
   - Cadeias de raciocínio com hash criptográfico SHA-256 e lista estrita de premissas factuais.
2. **`TypedAgentOrchestrator` (`orchestrator.py`):**
   - Catálogo de agentes cognitivos canônicos.
   - Validador anti-alucinação: checagem matemática de premissas contra fatos conhecidos.
   - Invariante FAIL_CLOSED: premissa não comprovada trava o veredito imediatamente em `HOLD`.

---

## 4. Evidências de Validação (Gates N08 / N06 / N07)

- `tests/test_intelligence_room.py`: 6 testes unitários aprovados.
- Regressão do repositório: 55+ testes aprovados com código de saída 0.
- Cartão Hermes: `t_hangar_intelligence_room_completion_01` promovido para DONE (T5).
- Mirror de governança sincronizado em `kanban_mirror.json`.
