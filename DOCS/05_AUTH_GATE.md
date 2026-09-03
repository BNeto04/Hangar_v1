# HANGAR V1 — 05. AUTH GATE (PORTAS DE AUTORIZAÇÃO & GATES)

**VERSÃO:** `1.0.0`  
**DATA:** `2026-09-01`  
**PROJETO:** `Hangar V1 / Colmeia Autônoma`  
**PORTAS ENVOLVIDAS:** `P-SECURITY-REVIEW-01`, `P-QUALITY-GATE-DECISION-01`  
**CAPACIDADES:** `RUFLO`, `IMPROVE`  

---

## 1. Matriz de Autoridades e Concessão de Privilégios

| Nível / Componente | Autoridade Concedida | O que NÃO Tem Autoridade para Fazer |
| :--- | :--- | :--- |
| **`Proprietário`** | Intenção soberana, homologação final, concessão de escopo e deploy. | Não executa código manual sem registrar a evidência. |
| **`N01 Planner`** | Criação e encadeamento de planos de alto nível (`P-PLAN-01`). | Não escreve código, não executa shell, não muta arquivos. |
| **`N02 Decomposer`** | Fragmentação em tarefas atômicas executáveis (`P-DECOMPOSE-01`). | Não executa código, não muta arquivos. |
| **`N03 Executor`** | **Monopólio de mutação de código** no workspace autorizado (`P-EXECUTE-01`). | Não emite planos, não aprova a própria qualidade. |
| **`N04/N05/N06 Lentes`**| Análise estrutural de código, domínio e segurança (`cli: []`). | Não alteram código, não aprovam promoção. |
| **`N07 Quality Gate`** | **Árbitro de elegibilidade lógica** (`eligible_for_promotion: True/False`). | Não executa git push, deploy físico ou merge. |
| **`N08 Verifier`** | Verificação factual de claims contra evidências curadas. | Não muta código. |
| **`N09 Curator`** | Curadoria de contexto e coerência territorial (`P-CURATOR-CONTEXT-01`). | Não muta código sem ordem de N03. |
| **`N10 Obsidian`** | Sincronização e sensoriamento de Vault/Cartografia (`P-OBSIDIAN-STATE-01`). | Não altera regras de segurança. |

---

## 2. Critérios de Aprovação no Quality Gate (N07)

1. **Segurança Mandatória:** Presença de `SECURITY_REVIEW` com `verdict == SECURITY_PASS` emitido por N06.
2. **Integridade de Hashes:** Todos os hashes `security_review_sha256` e `verifier_sha256` devem constar em `evidence_refs`.
3. **Consistência Lógica:** Zero contradições entre revisores (ex: Code Reviewer PASS + Security FAIL resulta em `REJECT`).
