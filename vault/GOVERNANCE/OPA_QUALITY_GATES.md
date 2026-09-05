# 🔍 MOTOR FORMAL OPA DE QUALITY GATES

O motor de Quality Gates do Hangar V1 avalia envelopes de evidência e relatórios de auditoria através de regras inspiradas em Rego (Open Policy Agent), garantindo verificação determinística e criptográfica.

- **Módulo Python:** [`az000_governance/policy/opa_engine.py`](file:///C:/Users/PICHAU/Hangar_v1/az000_governance/policy/opa_engine.py)
- **Testes Unitários:** [`tests/test_policy_engines.py`](file:///C:/Users/PICHAU/Hangar_v1/tests/test_policy_engines.py)
- **Commit:** [`91ab681`](https://github.com/BNeto04/Hangar_v1/commit/91ab681)

---

## 1. Regras de Avaliação Rego

O motor avalia 4 predicados mandatórios para aprovação de qualquer gate de qualidade:

1. **Validade Estrutural do Envelope:** Todos os campos canônicos (`gate_id`, `card_id`, `verifier_status`, `security_status`, `evidence_sha256`) devem estar preenchidos.
2. **Verificação de Hash SHA-256:** O campo `evidence_sha256` deve ser rigorosamente uma string hexadecimal de 64 caracteres.
3. **Consenso de Pareceristas:**
   - `verifier_status == "VERIFICATION_PASSED"`
   - `security_status == "SECURITY_PASS"`
4. **Ausência de Bloqueios:**
   - `blocking_reasons` deve ter comprimento 0.
   - Qualquer bloqueio força o veredito para `HOLD` com `fail-closed`.

---

## 2. API de Execução

```python
from az000_governance.policy.opa_engine import OpaQualityGateEngine, QualityGateEnvelope

engine = OpaQualityGateEngine()
envelope = QualityGateEnvelope(
    gate_id="GATE-ROOM-PRODUCTS-01",
    card_id="t_products_room_01",
    verifier_status="VERIFICATION_PASSED",
    security_status="SECURITY_PASS",
    evidence_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    blocking_reasons=[]
)
result = engine.evaluate(envelope)
# result.allowed == True, result.verdict == "PASS"
```

---

## 3. Navegação Interna
- [[GOVERNANCE/INDEX|Voltar ao Dashboard de Governança]]
- [[GOVERNANCE/CEDAR_AUTHORITY_ENGINE|Ver Motor Cedar de Autoridade]]
- [[GOVERNANCE/QUALITY_GATES_AND_ENFORCEMENT|Ver Barreira de CI/CD]]
