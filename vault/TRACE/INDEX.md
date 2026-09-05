# 📜 TRACE (Tier 9)

Traces de execução imutáveis, digests criptográficos SHA-256, evidências de auditoria e conformidade N08.

---

## 1. Identificação Canônica
- **Cômodo:** `TRACE`
- **Tier:** 9 de 11
- **Módulo Técnico:** `az000_governance.trace`
- **Porta Principal:** `Hangar_v1/TRACE/AUDIT/EVIDENCE_CHAIN:P-TRACE-AUDIT-01`
- **Referência Normativa:** `DOCS/29_TRACE_ROOM_SPEC.md` e `DOCS/06_TRACE_SCHEMA.md`
- **Invariantes ARCA:** `R-DOM-002` (FAIL_CLOSED), `R-DOM-005` (ROOM_BY_ROOM_ORDER), `R-DOM-006` (SINGLE_SOURCE_OF_TRUTH_ARCA)

---

## 2. Estrutura do Ledger Criptográfico
- **Localização:** `runtime/traces/trace_ledger.jsonl`
- **Formato:** Append-only JSON Lines encadeadas por SHA-256.
- **Campos Obrigatórios:** `trace_id`, `call_id`, `card_id`, `timestamp_iso`, `route_taken`, `actors`, `evidence_digests`, `overall_verdict`, `parent_trace_hash`, `trace_sha256`.

---

## 3. Critérios de Fechamento (ARCA)
1. **06_TRACE_SCHEMA.md em conformidade:** Validado estruturalmente por `TraceRecord`.
2. **Hashes SHA-256 verificáveis:** Auditado dinamicamente por `CryptographicTraceEngine.verify_chain()`.
