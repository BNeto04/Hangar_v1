# 🚦 QUALITY GATES & ENFORCEMENT DETERMINÍSTICO DE CI/CD

A barreira de automação do Hangar V1 intercepta commits, pushes e laudos, validando três pilares fundamentais antes de permitir qualquer promoção de estado.

- **Script de Enforcement:** [`scripts/git_enforcement.py`](file:///C:/Users/PICHAU/Hangar_v1/scripts/git_enforcement.py)
- **Status do Gate:** `100% PASS` (Código de Saída: 0)

---

## 1. Os 3 Pilares do Enforcement

1. **Pilar 1: Suíte de Testes Determinísticos (92 Testes 100% PASS)**
   - 7 testes fundacionais do Sprint 01 (`test_hangar_v1_sprint_01.py`).
   - 85 testes em `tests/` cobrindo todos os 11 cômodos da ARCA e os motores de política:
     - `test_arca_domain_rules.py` (6 testes)
     - `test_world_room.py` (4 testes)
     - `test_plant_room.py` (6 testes)
     - `test_ports_room.py` (6 testes)
     - `test_capabilities_room.py` (6 testes)
     - `test_machines_room.py` (6 testes)
     - `test_intelligence_room.py` (6 testes)
     - `test_external_room.py` (6 testes)
     - `test_trace_room.py` (6 testes)
     - `test_cockpits_room.py` (6 testes)
     - `test_products_room.py` (6 testes)
     - `test_policy_engines.py` (6 testes)
2. **Pilar 2: Integridade da Árvore Documental**
   - Proibição de arquivos `.md` soltos na raiz do repositório.
   - Preservação estrita das 11 pastas top-level canônicas no Vault.
3. **Pilar 3: Integridade do Espelho Kanban**
   - Sincronização matemática entre o SQLite local (`kanban.db`) e o espelho Git (`kanban_state.json` com 148 cartões).

---

## 2. Como Executar o Enforcement Localmente
```powershell
python scripts/git_enforcement.py check-all
```
Saída esperada:
```json
{
  "status": "PASS",
  "eligible_for_merge": true,
  "doc_tree": { "passed": true, "errors": [] },
  "kanban": { "passed": true, "detail": "Espelho Kanban integro com 148 cards." },
  "tests": { "passed": true, "detail": "Suíte completa de testes determinísticos: 92 testes 100% PASS." }
}
```

---

## 3. Navegação Interna
- [[GOVERNANCE/INDEX|Voltar ao Dashboard de Governança]]
- [[GOVERNANCE/ROADTRACE_CONVERGENCIA|Ver Roadtrace de Convergência]]
