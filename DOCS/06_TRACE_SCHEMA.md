# HANGAR V1 — 06. TRACE SCHEMA (ESQUEMA DE TRACES & EVIDÊNCIAS)

**VERSÃO:** `1.0.0`  
**DATA:** `2026-09-01`  
**PROJETO:** `Hangar V1 / Colmeia Autônoma`  
**PADRÃO:** `Audit-Ready Cryptographic Evidence Trace`  
**CAPACIDADES:** `GRAPHIFY`, `PONYTAIL`, `OPEN_DESIGN`  

---

## 1. Estrutura Canônica de um Trace de Execução

Cada execução na esteira do Hangar V1 gera uma trilha de auditoria encadeada com a seguinte estrutura:

```json
{
  "trace_id": "TRACE-HANGAR-V1-UUID-OR-SEQ",
  "call_id": "CALL-ID-CORRELATION",
  "card_id": "KANBAN-CARD-ID",
  "timestamp_iso": "ISO_8601_UTC",
  "route_taken": "N01 -> N02 -> N03 -> N10 -> N09 -> N08 -> N05 -> N04 -> N06 -> N07",
  "actors": {
    "N01": { "actor": "CHAR-PLANNER-01", "port": "P-PLAN-01", "plan_id": "PLAN-ID" },
    "N02": { "actor": "CHAR-TASK-DECOMPOSER-01", "port": "P-DECOMPOSE-01", "task_id": "TASK-ID" },
    "N03": { "actor": "CHAR-EXECUTOR-01", "port": "P-EXECUTE-01", "status": "EXECUTED", "artifacts": ["TARGET_PATH"] },
    "N08": { "actor": "CHAR-VERIFIER-01", "port": "P-VERIFICATION-RESULT-01", "verifier_sha256": "HEX_64" },
    "N06": { "actor": "CHAR-SECURITY-01", "port": "P-SECURITY-REVIEW-01", "security_review_sha256": "HEX_64" },
    "N07": { "actor": "CHAR-QUALITY-GATE-01", "port": "P-QUALITY-GATE-DECISION-01", "decision_sha256": "HEX_64", "verdict": "QUALITY_GATE_PASS" }
  },
  "evidence_digests": {
    "artifact_sha256": "HEX_64",
    "security_sha256": "HEX_64",
    "verification_sha256": "HEX_64",
    "quality_gate_sha256": "HEX_64"
  },
  "overall_verdict": "COMPLIANT_PASS"
}
```

---

## 2. Regras de Preservação e Imutabilidade

- Um trace emitido e assinado criptograficamente **nunca pode ser editado**.
- Modificações de código geram novos traces encadeados preservando a linhagem do anterior.
