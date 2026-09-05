# HANGAR V1 — 30. ESPECIFICAÇÃO DO CÔMODO COCKPITS (TIER 10)

**STATUS:** `COMPLETE`  
**DATA:** `2026-09-04`  
**AUTOR:** `Down Plant Technical Executor`  
**AUDITORIA:** `Codex / ChatGPT (CG-000140 / CALL-HANGAR-NEXT-ROOM-COCKPITS-001)`  
**ORDEM DE CÔMODOS:** Tier 10 de 11  

---

## 1. Propósito e Fronteiras

O cômodo **COCKPITS** é o centro nevrálgico de observabilidade, supervisão e soberania humana do Hangar V1. Ele provê painéis de visualização espacial sem atrito e o console do Teacher Mode, garantindo que o Proprietário exerça controle total sobre a esteira de execução sem interferência intermediária. Ele implementa o `CockpitController`, conectando os dados topológicos da ARCA, o estado do kanban e os traces criptográficos às interfaces de comando soberano (`R-DOM-001`), com isolamento estrito `FAIL_CLOSED` (`R-DOM-002`).

---

## 2. Reconciliação Topológica e Invariantes ARCA

- **Invariante R-DOM-005 (ROOM_BY_ROOM_ORDER):**
  - Upstream concluído e validado: `GOVERNANCE (Tier 1)`, `WORLD (Tier 2)`, `PLANT (Tier 3)`, `PORTS (Tier 4)`, `CAPABILITIES (Tier 5)`, `MACHINES (Tier 6)`, `INTELLIGENCE (Tier 7)`, `EXTERNAL (Tier 8)` e `TRACE (Tier 9)` estão com `ROOM_STATUS: COMPLETE`.
  - Cômodo ativo: `COCKPITS (Tier 10)` concluído com console de controle soberano, Teacher Mode ativo e testes unitários aprovados.
  - Downstream habilitado: `PRODUCTS (Tier 11)` torna-se o próximo cômodo elegível na ordem topológica da ARCA (cômodo final).

- **Invariante R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA):**
  - Os critérios canônicos de fechamento derivam da tabela `_CANONICAL_ROOMS` em `az000_governance/arca/canonical_domain_rules.py`:
    1. *"Visualização espacial sem atrito"*
    2. *"Mapeamento de comandos do Proprietário"*

- **Invariante R-DOM-001 (SOBERANIA_PROPRIETARIO):**
  - Todo comando despachado via console exige emissor soberano ("PROPRIETARIO" ou "OWNER") e chave de autoridade válida. Comandos forjados ou não autorizados travam em fail-closed.

---

## 3. Implementação Técnica (`az000_governance/cockpits/`)

1. **Modelos Canônicos (`models.py`):**
   - `RoomSnapshot`: Visão sintética e sem atrito do estado de cada cômodo da ARCA.
   - `CockpitView`: Modelo de visão espacial agregada (cômodos, contagem de agentes, tamanho do ledger de traces e saúde do sistema).
   - `OwnerCommand`: Envelope imutável de ordens do Proprietário (`PAUSE_PIPELINE`, `RESUME_PIPELINE`, `APPROVE_ROOM`, etc.).
   - `TeacherModeState`: Telemetria ao vivo e níveis de inspeção de auditoria (`FULL_AUDIT`).

2. **Controlador Central (`controller.py`):**
   - `CockpitController`:
     - `render_spatial_view()`: Mapeamento em tempo real dos 11 cômodos da ARCA sem atrito de navegação.
     - `dispatch_owner_command()`: Validação soberana (`R-DOM-001`) e geração de `TypedPortEnvelope` Down Plant direcionado à porta de autoridade da governança (`Hangar_v1/GOVERNANCE/AUTHORITY/SOVEREIGN:P-GOV-AUTH-01`).
     - Gestão determinística do estado do Teacher Mode.

---

## 4. Evidências de Validação (Gates N08 / N06 / N07)

- `tests/test_cockpits_room.py`: 6 testes unitários aprovados cobrindo visão espacial, comandos soberanos, fail-closed, dependências upstream e próximo cômodo elegível.
- Regressão do repositório: 73/73 testes aprovados com código de saída 0.
- Cartão Hermes: `t_hangar_cockpits_room_completion_01` promovido para DONE (T5).
- Mirror de governança: `kanban_mirror.json` sincronizado.
