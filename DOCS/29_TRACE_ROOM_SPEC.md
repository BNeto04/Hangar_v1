# HANGAR V1 — 29. ESPECIFICAÇÃO DO CÔMODO TRACE (TIER 9)

**STATUS:** `COMPLETE`  
**DATA:** `2026-09-04`  
**AUTOR:** `Down Plant Technical Executor`  
**AUDITORIA:** `Codex / ChatGPT (CG-000139 / CALL-HANGAR-NEXT-ROOM-TRACE-001)`  
**ORDEM DE CÔMODOS:** Tier 9 de 11  

---

## 1. Propósito e Fronteiras

O cômodo **TRACE** estabelece a esteira de auditoria criptográfica e imutabilidade probatória do Hangar V1. Ele implementa o `CryptographicTraceEngine`, que registra trilhas de execução em formato append-only estruturadas estritamente de acordo com o esquema canônico `DOCS/06_TRACE_SCHEMA.md`. Cada trace consolida as evidências dos agentes (N01 a N10), digests SHA-256 de artefatos e decisões de qualidade (N08/N06/N07), mantendo uma cadeia contínua de blocos com hashing encadeado imutável.

---

## 2. Reconciliação Topológica e Invariantes ARCA

- **Invariante R-DOM-005 (ROOM_BY_ROOM_ORDER):**
  - Upstream concluído e validado: `GOVERNANCE (Tier 1)`, `WORLD (Tier 2)`, `PLANT (Tier 3)`, `PORTS (Tier 4)`, `CAPABILITIES (Tier 5)`, `MACHINES (Tier 6)`, `INTELLIGENCE (Tier 7)` e `EXTERNAL (Tier 8)` estão com `ROOM_STATUS: COMPLETE`.
  - Cômodo ativo: `TRACE (Tier 9)` concluído com motor criptográfico append-only, esquema de traces em conformidade e testes unitários aprovados.
  - Downstream habilitado: `COCKPITS (Tier 10)` torna-se o próximo cômodo elegível na ordem linear da ARCA.

- **Invariante R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA):**
  - Os critérios canônicos de fechamento derivam da tabela `_CANONICAL_ROOMS` em `az000_governance/arca/canonical_domain_rules.py`:
    1. *"06_TRACE_SCHEMA.md em conformidade"*
    2. *"Hashes SHA-256 verificáveis"*

- **Invariante R-DOM-002 (FAIL_CLOSED_SYSTEMIC):**
  - Qualquer tentativa de persistência com evidence digest corrompido, quebra de encadeamento de hash ou trace modificado retroativamente aborta e bloqueia a cadeia de auditoria imediatamente.

---

## 3. Implementação Técnica (`az000_governance/trace/`)

1. **Modelos Canônicos (`models.py`):**
   - `TraceRecord`: Dataclass normativo contendo `trace_id`, `call_id`, `card_id`, `timestamp_iso`, `route_taken`, `actors`, `evidence_digests`, `overall_verdict`, `parent_trace_hash` e `trace_sha256`.
   - `compute_hash()`: Serialização JSON canônica (ordenada e compacta) com hashing SHA-256.
   - `verify_integrity()`: Validação estrita da assinatura matemática do trace.

2. **Motor Criptográfico (`engine.py`):**
   - `CryptographicTraceEngine`:
     - Armazenamento em ledger append-only (`runtime/traces/trace_ledger.jsonl`).
     - Encadeamento de bloco (bloco gênese apontando para hash nulo de 64 zeros, blocos subsequentes apontando para o `trace_sha256` anterior).
     - Validação estrita de expressões regulares SHA-256 (64 hexadecimais) para todos os evidence digests.
     - Método `verify_chain()` para auditoria em tempo de execução de ponta a ponta.

---

## 4. Evidências de Validação (Gates N08 / N06 / N07)

- `tests/test_trace_room.py`: 6 testes unitários aprovados (conformidade com esquema, encadeamento criptográfico, fail-closed, integridade do ledger e ordem topológica).
- Regressão do repositório: 67/67 testes aprovados com código de saída 0.
- Cartão Hermes: `t_hangar_trace_room_completion_01` promovido para DONE (T5).
- Mirror de governança: `kanban_mirror.json` sincronizado.
