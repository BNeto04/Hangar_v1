# 📜 MÓDULO ARCA — REGRAS DE DOMÍNIO CANÔNICAS & SOMENTE-LEITURA

**ID DO ARTEFATO:** `ARCA-DOMAIN-RULES`  
**VERSÃO DO ESQUEMA:** `AZ000-ARCA-DOMAIN-RULES-1`  
**CÔMODO:** `GOVERNANCE` (ou `AZ000_GOVERNANCA_SOBERANIA`)  
**MÓDULO:** `ARCA`  
**SUBMÓDULO:** `DOMAIN_RULES`  
**PORTA:** `P-GOV-ARCA-RULES-01`  
**ESTADO:** `READ_ONLY / CANÔNICO / IMUTÁVEL`  

---

## 1. Princípio Fundamental
> **`R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA)`**: Todas as regras de domínio do projeto Hangar V1 residem exclusivamente neste módulo ARCA. Módulos satélites (circuitos, lentes, executores, robôs) referenciam a ARCA e nunca duplicam regras localmente.

---

## 2. Catálogo Oficial de Regras de Domínio

| ID Regra | Nome Canônico | Categoria | Descrição Normativa | Enforcement |
| :--- | :--- | :--- | :--- | :--- |
| **`R-DOM-001`** | `SOBERANIA_PROPRIETARIO` | `GOVERNANCE_AUTHORITY` | O Proprietário detém autoridade máxima irrevogável sobre intenção, escopo, paradas, homologações e exceções. | `SOVEREIGN_DECISION` |
| **`R-DOM-002`** | `FAIL_CLOSED_SYSTEMIC` | `SAFETY_INVARIANT` | Dúvida sistemática, ambiguidade, corrupção ou falta de prova trava preventivamente a esteira (`HOLD`/`REJECT`). | `FAIL_CLOSED` |
| **`R-DOM-003`** | `NO_UNSEALED_PASS` | `INGESTION_INTEGRITY` | Nenhuma instrução externa transita sem validação fail-closed e selagem criptográfica SHA-256 (`SealedIntentContract`) no AZ000. | `GATE_ARBITER` |
| **`R-DOM-004`** | `NO_SPEC_NO_CODE` | `DEVELOPMENT_LIFECYCLE` | Nenhuma mutação de produto ocorre sem especificação prévia e card visível no Hermes Kanban. | `STATIC_CHECK` |
| **`R-DOM-005`** | `ROOM_BY_ROOM_ORDER` | `TOPOLOGICAL_DISCIPLINE` | SPECs e desenvolvimento são estritamente por CÔMODO. Fechar 100% o cômodo e dependências antes de avançar. | `GATE_ARBITER` |
| **`R-DOM-006`** | `SINGLE_SOURCE_OF_TRUTH_ARCA` | `ARCHITECTURAL_COHERENCE` | Regras de domínio residem única e exclusivamente na ARCA; proibido duplicar regras em submódulos. | `STATIC_CHECK` |
| **`R-DOM-007`** | `EVIDENCE_FIRST_PROMOTION` | `QUALITY_GATE` | Promoção para T5 (Done) exige prova material auditada; auto-declaração pelo executor é proibida. | `FAIL_CLOSED` |

---

## 3. Ordem Canônica de Cômodos (Room-Order) & Dependências

Conforme diretriz soberana, o avanço entre cômodos segue estritamente a topologia de dependências:

1. **`GOVERNANCE`** (Tier 1): Fundação de autoridade, ARCA e regras. *(Deps: Nenhuma - Primeiro a fechar)*
2. **`WORLD`** (Tier 2): Modelo de mundo e Master World Canvas. *(Deps: GOVERNANCE)*
3. **`PLANT`** (Tier 3): Topologia física e confinamento de workspaces. *(Deps: GOVERNANCE, WORLD)*
4. **`PORTS`** (Tier 4): Portas tipadas e envelopes imutáveis. *(Deps: GOVERNANCE, PLANT)*
5. **`CAPABILITIES`** (Tier 5): Motores estruturais (Graphify, Improve, Ruflo). *(Deps: GOVERNANCE, PORTS)*
6. **`MACHINES`** (Tier 6): Nano Máquinas determinísticas. *(Deps: PORTS, CAPABILITIES)*
7. **`INTELLIGENCE`** (Tier 7): Agentes confinados (CHARs N01 a N10). *(Deps: GOVERNANCE, PORTS, MACHINES)*
8. **`EXTERNAL`** (Tier 8): Adaptadores de borda e bridges (PR #1, Webhook, Telegram). *(Deps: PORTS, INTELLIGENCE)*
9. **`TRACE`** (Tier 9): Trilhas de auditoria e hashes SHA-256. *(Deps: GOVERNANCE, INTELLIGENCE, EXTERNAL)*
10. **`COCKPITS`** (Tier 10): Painéis e Teacher Mode. *(Deps: INTELLIGENCE, TRACE)*
11. **`PRODUCTS`** (Tier 11): Entregáveis e releases homologados. *(Deps: Todos os cômodos precedentes)*

---

## 4. Política de Fechamento de Cômodo
Um cômodo só pode ser considerado fechado se satisfizer cumulativamente:
1. Todas as SPECs do cômodo implementadas e aprovadas;
2. Todas as dependências a montante formalmente concluídas;
3. Documentação no Vault sem links quebrados;
4. Suítes de testes determinísticas executadas com êxito (N08/N06/N07).
