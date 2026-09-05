# 📜 ARCA — ESPECIFICAÇÃO DE REGRAS E ORDEM DE CÔMODOS

A **ARCA** é a fonte única de verdade normativa (*Single Source of Truth* — `R-DOM-006`) do Hangar V1. Nenhuma regra de negócio ou invariante de arquitetura pode divergir das definições aqui contidas.

- **Módulo Python:** [`az000_governance/arca/canonical_domain_rules.py`](file:///C:/Users/PICHAU/Hangar_v1/az000_governance/arca/canonical_domain_rules.py)
- **Hash de Integridade:** `ARCA_HASH_SHA256` verificado deterministamente por testes.

---

## 1. As 7 Regras Canônicas de Domínio

| ID da Regra | Nome | Descrição Canônica |
|---|---|---|
| `R-DOM-001` | **SOBERANIA_PROPRIETARIO** | O Proprietário detém a prerrogativa irrevogável de homologação, publicação, escopo e concessão de exceções. Nenhum agente automatizado pode se auto-aprovar. |
| `R-DOM-002` | **FAIL_CLOSED** | Qualquer divergência factual, ausência de prova ou teste falho bloqueia imediatamente o avanço do sistema em estado seguro (*deny by default*). |
| `R-DOM-003` | **AUTORIDADE_ESTRITA_PERFIL** | Lentes e pareceristas operam estritamente como *read-only* (sem terminal/escrita). Somente o Executor Operacional (`N03`) possui monopólio de escrita. |
| `R-DOM-004` | **RASTREABILIDADE_PROVA_SHA256** | Toda entrega e avanço de fase exige envelope com hash criptográfico SHA-256 de 64 caracteres hexadecimais auditável. |
| `R-DOM-005` | **ORDEM_ESTRITA_COMODOS** | A progressão na planta física deve seguir estritamente a ordem cômodo por cômodo do Tier 1 ao Tier 11, sem saltos. |
| `R-DOM-006` | **FONTE_UNICA_VERDADE_ARCA** | É expressamente proibido duplicar regras de domínio em módulos locais. Todos devem importar exclusivamente de `canonical_domain_rules.py`. |
| `R-DOM-007` | **PROIBICAO_AUTO_HOMOLOGACAO** | É terminantemente vedado a qualquer agente técnico declarar estado homologado sem despacho explícito do Proprietário. |

---

## 2. Ordem Canônica dos 11 Cômodos Territoriais

1. **Tier 1 — `GOVERNANCE`:** Regras canônicas de domínio, invariantes e matriz de autoridade.
2. **Tier 2 — `WORLD`:** Ontologia global, modelo de mundo e canvas espacial mestre.
3. **Tier 3 — `PLANT`:** Endereçamento formal GPS Down Plant (`TERRENO/COMODO/MODULO/SUBMODULO:PORTA`).
4. **Tier 4 — `PORTS`:** Registro central de portas tipadas e envelopes de mensagem.
5. **Tier 5 — `CAPABILITIES`:** Motores de capacitação (Graphify, Improve, Ponytail, Ruflo, Open Design).
6. **Tier 6 — `MACHINES`:** Máquinas de estados determinísticas (FSM) e isolamento `NM-OBS-01` e `NM-EXEC-01`.
7. **Tier 7 — `INTELLIGENCE`:** Agentes cognitivos confinados (CHARs N01..N10) com prova matemática anti-alucinação.
8. **Tier 8 — `EXTERNAL`:** Gateway com verificação HMAC SHA-256 em tempo constante e deduplicação.
9. **Tier 9 — `TRACE`:** Motor de trilhas criptográficas e ledger imutável append-only.
10. **Tier 10 — `COCKPITS`:** Painéis de controle centralizados e telemetria de Teacher Mode.
11. **Tier 11 — `PRODUCTS`:** Gestão de releases homologadas, release notes e manifesto de integridade.

---

## 3. Navegação Interna
- [[GOVERNANCE/INDEX|Voltar ao Dashboard de Governança]]
- [[GOVERNANCE/CEDAR_AUTHORITY_ENGINE|Ver Motor Cedar de Autoridade]]
- [[GOVERNANCE/OPA_QUALITY_GATES|Ver Motor OPA de Quality Gates]]
