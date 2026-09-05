# 🛡️ MOTOR FORMAL CEDAR DE AUTORIDADE

O motor de autoridade Cedar do Hangar V1 implementa controle de acesso granular baseado em papéis e atributos (RBAC/ABAC) com semântica estrita *permit / forbid* e princípio *fail-closed default-deny*.

- **Módulo Python:** [`az000_governance/policy/cedar_engine.py`](file:///C:/Users/PICHAU/Hangar_v1/az000_governance/policy/cedar_engine.py)
- **Testes Unitários:** [`tests/test_policy_engines.py`](file:///C:/Users/PICHAU/Hangar_v1/tests/test_policy_engines.py)
- **Commit:** [`91ab681`](https://github.com/BNeto04/Hangar_v1/commit/91ab681)

---

## 1. Princípios e Políticas Ativas

1. **Soberania do Proprietário (Regra `R-DOM-001`):**
   - Política: `permit(principal == Owner, action, resource);`
   - O Proprietário detém permissão irrestrita para qualquer ação em qualquer recurso do Hangar.
2. **Monopólio de Escrita do Executor (`N03`):**
   - Política: `permit(principal == N03_Executor, action in [write_code, run_command], resource);`
   - Somente o Executor tem autoridade de escrita no repositório e execução de terminal.
3. **Isolamento Read-Only das Lentes (`N04`, `N05`, `N06`):**
   - Política: `forbid(principal in [N04, N05, N06], action in [write_code, run_command, git_push]);`
   - Pareceristas operam exclusivamente no modo *payload-in / parecer-out*.
4. **Fail-Closed Default Deny:**
   - Se nenhuma política explícita de `permit` cobrir a solicitação, ou se houver qualquer `forbid` concorrente, o acesso é sumariamente negado (`DENY`).

---

## 2. API de Execução

```python
from az000_governance.policy.cedar_engine import CedarAuthorityEngine, CedarRequest

engine = CedarAuthorityEngine()
request = CedarRequest(
    principal="N04_Reviewer",
    action="write_code",
    resource="az000_governance/plant"
)
decision = engine.evaluate(request)
# decision.allowed == False (FORBIDDEN_POLICY_OVERRIDE)
```

---

## 3. Navegação Interna
- [[GOVERNANCE/INDEX|Voltar ao Dashboard de Governança]]
- [[GOVERNANCE/OPA_QUALITY_GATES|Ver Motor OPA de Quality Gates]]
- [[GOVERNANCE/ARCA_SPEC_AND_ROOM_ORDER|Ver Regras Canônicas ARCA]]
