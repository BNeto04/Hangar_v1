# 🎛️ COCKPITS (Tier 10)

Painéis operacionais, dashboards, interface do Teacher Mode e consoles de controle soberano.

---

## 1. Identificação Canônica
- **Cômodo:** `COCKPITS`
- **Tier:** 10 de 11
- **Módulo Técnico:** `az000_governance.cockpits`
- **Porta Principal:** `Hangar_v1/COCKPITS/CONSOLE/DISPATCH:P-COCKPIT-DISPATCH-01`
- **Referência Normativa:** `DOCS/30_COCKPITS_ROOM_SPEC.md`
- **Invariantes ARCA:** `R-DOM-001` (SOBERANIA), `R-DOM-002` (FAIL_CLOSED), `R-DOM-005` (ROOM_BY_ROOM_ORDER), `R-DOM-006` (SINGLE_SOURCE_OF_TRUTH_ARCA)

---

## 2. Capacidades do Console
- **Visualização Espacial:** Visão unificada e sem atrito dos 11 cômodos da ARCA e suas portas.
- **Teacher Mode:** Observabilidade detalhada em tempo real com telemetria live.
- **Comando Soberano:** Ingestão de ordens do Proprietário com autenticação estrita.

---

## 3. Critérios de Fechamento (ARCA)
1. **Visualização espacial sem atrito:** Implementado por `CockpitController.render_spatial_view()`.
2. **Mapeamento de comandos do Proprietário:** Validado por `CockpitController.dispatch_owner_command()`.
