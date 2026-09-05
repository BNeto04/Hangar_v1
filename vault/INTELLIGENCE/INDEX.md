# 🧠 INTELLIGENCE (Cômodo Tier 7)

**Status do Cômodo:** `COMPLETE`  
**Tier:** 7  
**Topologia de Dependências:** `GOVERNANCE (Tier 1)` + `PORTS (Tier 4)` + `MACHINES (Tier 6)` -> `INTELLIGENCE (Tier 7)` -> `EXTERNAL (Tier 8)`  
**Endereço GPS Canônico:** `Hangar_v1/INTELLIGENCE/ORCHESTRATION/COGNITIVE_AGENTS:P-INTEL-ORCHESTRATOR-01`  
**Referência Canônica ARCA:** `az000_governance/arca/canonical_domain_rules.py` (Regras `R-DOM-005` e `R-DOM-006`)

---

## 1. Definição Ontológica

O cômodo **INTELLIGENCE** estrutura os agentes cognitivos confinados (CHARs N01 a N10), seus papéis e protocolos de raciocínio. O orquestrador tipado (`TypedAgentOrchestrator`) garante que qualquer dedução ou conclusão gerada por um modelo de linguagem seja formalmente ancorada em premissas factuais comprovadas, impedindo alucinações cognitivas sob a invariante `FAIL_CLOSED`.

---

## 2. Catálogo Canônico de Agentes Cognitivos (CHARs)

| Agente / Nível | Porta Primária Down Plant | Capacidades Permitidas | Papel Operacional |
|---|---|---|---|
| `CHAR-PLANNER-01` (N01) | `Hangar_v1/INTELLIGENCE/CHAR/CHAR_PLANNER_01:P-INTEL-PLAN-01` | `RUFLO`, `OPEN_DESIGN` | Planejamento estratégico e alinhamento de intenção |
| `CHAR-EXECUTOR-01` (N03) | `Hangar_v1/INTELLIGENCE/CHAR/CHAR_EXECUTOR_01:P-INTEL-EXEC-01` | `IMPROVE` | Execução técnica cirúrgica Down Plant |
| `CHAR-VERIFIER-01` (N08) | `Hangar_v1/INTELLIGENCE/CHAR/CHAR_VERIFIER_01:P-INTEL-VERIFY-01` | `GRAPHIFY` | Auditoria matemática e emissão de provas SHA-256 |
| `CHAR-CURATOR-01` (N09) | `Hangar_v1/INTELLIGENCE/CHAR/CHAR_CURATOR_01:P-INTEL-CURATOR-01` | `PONYTAIL` | Custódia e reconciliação contínua da árvore documental |
| `CHAR-OBSIDIAN-01` (N10) | `Hangar_v1/INTELLIGENCE/CHAR/CHAR_OBSIDIAN_01:P-INTEL-OBSIDIAN-01` | `GRAPHIFY`, `OPEN_DESIGN` | Indexação espacial e grafos do Vault |

---

## 3. Invariantes Canônicas (ARCA)

1. **R-DOM-005 (Ordem Sequencial de Cômodos):** INTELLIGENCE depende estritamente do fechamento completo de `GOVERNANCE (Tier 1)`, `PORTS (Tier 4)` e `MACHINES (Tier 6)` e habilita `EXTERNAL (Tier 8)`.
2. **R-DOM-006 (ARCA Fonte Única da Verdade):** Os critérios de encerramento ("Orquestrador de agentes tipado", "Raciocínio estruturado sem alucinação") derivam da ARCA sem duplicações locais.
3. **Anti-Alucinação Estrita:** Nenhuma ação cognitiva pode ser promovida sem que suas premissas sejam factualmente comprovadas no repositório.
