# HANGAR V1 — 26. ESPECIFICAÇÃO DO CÔMODO MACHINES (TIER 6)

**STATUS:** `COMPLETE`  
**DATA:** `2026-09-04`  
**AUTOR:** `Down Plant Technical Executor`  
**AUDITORIA:** `Codex / ChatGPT (CG-000136 / CALL-HANGAR-NEXT-ROOM-MACHINES-001)`  
**ORDEM DE CÔMODOS:** Tier 6 de 11  

---

## 1. Propósito e Fronteiras

O cômodo **MACHINES** estabelece a camada de execução mecânica determinística do Hangar V1. Ele isola os autômatos de estado finito (`FiniteStateMachine`) e as Nano Máquinas (`NanoMachine`), garantindo que transições ocorram sem efeitos colaterais ocultos e com tratamento estrito de erro.

---

## 2. Reconciliação Topológica e Invariantes ARCA

- **Invariante R-DOM-005 (ROOM_BY_ROOM_ORDER):**
  - Upstream concluído e validado: `GOVERNANCE (Tier 1)`, `WORLD (Tier 2)`, `PLANT (Tier 3)`, `PORTS (Tier 4)` e `CAPABILITIES (Tier 5)` estão com `ROOM_STATUS: COMPLETE`.
  - Cômodo ativo: `MACHINES (Tier 6)` concluído com transições de estado puras, tratamento de erro estrito e testes aprovados.
  - Downstream habilitado: `INTELLIGENCE (Tier 7)` torna-se o próximo cômodo elegível.

- **Invariante R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA):**
  - Os critérios canônicos de fechamento derivam da tabela `_CANONICAL_ROOMS` em `az000_governance/arca/canonical_domain_rules.py`.

---

## 3. Implementação Técnica (`az000_governance/machines/`)

1. **`FiniteStateMachine` (`fsm.py`):**
   - Transições puras `(Estado, Evento) -> NovoEstado`.
   - Suporte a guardas condicionais.
   - Rejeição `FAIL_CLOSED` imediata para eventos ilegais ou falhas de guarda (trava em `HOLD`).
   - Registro de histórico completo de transições auditável.
2. **`NanoMachine` & Implementações Canônicas (`nano_machines.py`):**
   - `NM_OBS_01_VaultAuditor`: Valida nós e integridade de grafos do Vault acoplado ao motor `GraphifyEngine`.
   - `NM_EXEC_01_TaskAutomata`: Controla o ciclo de vida e transições de tarefas (`INITIAL`, `READY`, `RUNNING`, `DONE`, `HOLD`).

---

## 4. Evidências de Validação (Gates N08 / N06 / N07)

- `tests/test_machines_room.py`: 6 testes unitários aprovados.
- Regressão do repositório: 49+ testes aprovados com código de saída 0.
- Cartão Hermes: `t_hangar_machines_room_completion_01` promovido para DONE (T5).
- Mirror de governança sincronizado em `kanban_mirror.json`.
