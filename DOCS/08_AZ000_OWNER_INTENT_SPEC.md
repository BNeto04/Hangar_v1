# 08_AZ000_OWNER_INTENT_SPEC.md — Especificação de Aprofundamento do Cômodo OWNER-INTENT (AZ000)

## 1. Identificação Topológica Canônica
- **TERRITÓRIO:** `HANGAR_V1/AZ000_GOVERNANCA_SOBERANIA`
- **CÔMODO:** `OWNER_INTENT`
- **MÓDULO:** `INTENT_INGESTION`
- **SUBMÓDULO:** `SEALED_CONTRACT_EMITTER`
- **CIRCUITO:** `CIRCUIT_OWNER_INTENT_TO_PLANNER`

---

## 2. Portas Canônicas e Assinaturas

| Porta | Função | Tipo Entrada | Tipo Saída | Comportamento em Falha |
| :--- | :--- | :--- | :--- | :--- |
| `P-OWNER-INTENT-INGEST-01` | Ingestão bruta | Dict / Payload JSON | `OwnerRawIntent` | Rejeição imediata por schema |
| `P-INTENT-NORMALIZATION-01` | Normalização | `OwnerRawIntent` | `NormalizedIntentDraft` | Erro de tipagem / normalização |
| `P-INTENT-VALIDATION-01` | Validação determinística | `NormalizedIntentDraft` | `ValidatedIntent` | Fail-Closed: `REJECT` ou `HOLD` |
| `P-INTENT-SEAL-01` | Selagem criptográfica | `ValidatedIntent` | `SealedIntentContract` | Falha de integridade SHA256 |
| `P-INTENT-HANDOFF-N01-01` | Entrega ao Planner N01 | `SealedIntentContract` | `HandoffEnvelope` | Bloqueio total se selo inválido |

---

## 3. Invariantes do Circuito
1. **`NO_UNSEALED_PASS`:** Nenhuma intenção sem selo SHA256 e validação determinística pode ser recebida pelo Planner N01.
2. **`FAIL_CLOSED`:** Intenções ambíguas recebem veredito `HOLD_INCONCLUSIVE`; intenções não autorizadas ou com campos faltantes recebem `REJECT_FAIL_CLOSED`.
3. **`IMMUTABILITY`:** O contrato selado possui `contract_sha256` imutável que vincula autor, escopo, timestamp e diretivas.
