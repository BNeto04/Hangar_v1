# HANGAR V1 — 04. PILOT RULE (REGRAS DE PILOTAGEM & TEACHER MODE)

**VERSÃO:** `1.0.0`  
**DATA:** `2026-09-01`  
**PROJETO:** `Hangar V1 / Colmeia Autônoma`  
**MODALIDADE:** `HANGAR_ONLY; TEACHER_MODE`  
**CAPACIDADES:** `IMPROVE`, `OPEN_DESIGN`  

---

## 1. Princípios do Teacher Mode

No modo **Teacher Mode (Professor/Observador Ativo)**, o agente superior (Antigravity):
1. **Prioridade de Execução Local:** Os CHARs locais e seus motores determinísticos executam autonomamente todas as etapas.
2. **Intervenção Mínima Justificada:** O Antigravity apenas observa a execução. Intervenções técnicas ocorrem estritamente quando há falha de baixo nível (ex: incompatibilidade de encoding de sistema operacional ou I/O) e são registradas com transparência.
3. **Preservação da Lógica dos CHARs:** Nenhuma intervenção altera a cognição, os critérios de aceitação ou a autonomia dos CHARs.
4. **Sem Mutações Fora de Escopo:** Não amplia tarefas, não executa passos futuros antecipadamente e não remove evidências históricas.

---

## 2. Regras de Parada e Fail-Closed

- Se um CHAR emitir veredito `FAIL` ou `INCONCLUSIVE`, a esteira para imediatamente.
- Não é permitido ajustar testes ou fabricar saídas para mascarar falhas legítimas.
- A promoção para níveis superiores de confiança (T4/T5) exige evidência material comprovada e homologação pelo Proprietário.
