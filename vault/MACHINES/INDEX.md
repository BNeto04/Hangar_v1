# ⚙️ MACHINES (Cômodo Tier 6)

**Status do Cômodo:** `COMPLETE`  
**Tier:** 6  
**Topologia de Dependências:** `PORTS (Tier 4)` + `CAPABILITIES (Tier 5)` -> `MACHINES (Tier 6)` -> `INTELLIGENCE (Tier 7)`  
**Endereço GPS Canônico:** `Hangar_v1/MACHINES/AUTOMATA/FINITE_STATE_MACHINE:P-MACH-FSM-RUNNER-01`  
**Referência Canônica ARCA:** `az000_governance/arca/canonical_domain_rules.py` (Regras `R-DOM-005` e `R-DOM-006`)

---

## 1. Definição Ontológica

O cômodo **MACHINES** abriga os autômatos determinísticos de estado finito (FSM) e as Nano Máquinas operacionais do Hangar V1. Toda execução é governada por transições puras `(EstadoAtual, Evento) -> NovoEstado`, com tratamento estrito sob a invariante soberana `FAIL_CLOSED` (R-DOM-002).

---

## 2. Catálogo Canônico de Nano Máquinas

| Nano Máquina | Porta Primária Down Plant | Propósito Operacional | Invariante de Estado |
|---|---|---|---|
| `NM-OBS-01` | `Hangar_v1/MACHINES/NANO/NM_OBS_01:P-MACH-OBS-AUDIT-01` | Auditoria determinística e validação de nós do Vault Obsidian | INITIAL -> READY -> RUNNING -> DONE / FAILED |
| `NM-EXEC-01` | `Hangar_v1/MACHINES/NANO/NM_EXEC_01:P-MACH-TASK-EXEC-01` | Autômato de transições do ciclo de vida de tarefas da colmeia | INITIAL -> READY -> RUNNING -> DONE / HOLD |

---

## 3. Invariantes Canônicas (ARCA)

1. **R-DOM-005 (Ordem Sequencial de Cômodos):** MACHINES depende estritamente do fechamento completo de `PORTS (Tier 4)` e `CAPABILITIES (Tier 5)` e habilita `INTELLIGENCE (Tier 7)`.
2. **R-DOM-006 (ARCA Fonte Única da Verdade):** Os critérios de encerramento ("Transições de estado puras", "Tratamento estrito de erros") derivam da ARCA sem duplicações locais.
3. **FAIL_CLOSED Sistêmico (R-DOM-002):** Diante de evento ilegal ou falha de condição de guarda, a máquina transita imediatamente para `HOLD` ou `FAILED`, proibindo estados espúrios.
