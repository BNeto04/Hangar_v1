# 23. Especificação Canônica e Fechamento do Cômodo PLANT (Tier 3)

## 1. Identificação e Coordenadas Down Plant
- **Artefato:** `DOCS/23_PLANT_ROOM_SPEC.md`
- **Chamada:** `CG-000133` (`CALL-HANGAR-NEXT-ROOM-PLANT-001`)
- **Cartão Kanban:** `t_hangar_plant_room_completion_01`
- **CÔMODO:** `PLANT` (Tier 3)
- **MÓDULO:** `TOPOLOGY`
- **SUBMÓDULO:** `WORKSPACES`
- **PORTA:** `P-PLANT-TOPOLOGY-LAYOUT-01`
- **ENDEREÇO CANÔNICO:** `Hangar_v1/PLANT/TOPOLOGY/WORKSPACES:P-PLANT-TOPOLOGY-LAYOUT-01`
- **DEPENDÊNCIAS A MONTANTE:**
  - `GOVERNANCE` (Tier 1) — **COMPLETE**
  - `WORLD` (Tier 2) — **COMPLETE**

---

## 2. Topologia Física do Território
Conforme definido no modelo ontológico da ARCA (`R-DOM-005` e `R-DOM-006`):
1. **Raiz do Repositório:** `C:\Users\PICHAU\Hangar_v1`
2. **As 11 Pastas do Vault:**
   - `vault/GOVERNANCE/`, `vault/WORLD/`, `vault/PLANT/`, `vault/PORTS/`, `vault/CAPABILITIES/`
   - `vault/MACHINES/`, `vault/INTELLIGENCE/`, `vault/EXTERNAL/`, `vault/TRACE/`, `vault/COCKPITS/`, `vault/PRODUCTS/`
3. **Módulos de Código Confinados:**
   - `az000_governance/owner_intent/` (Ingestor, contratos e portas AZ000)
   - `az000_governance/arca/` (Módulo ARCA de regras de domínio imutáveis)
   - `az000_governance/plant/` (Utilitário de validação GPS Down Plant)
   - `bridge/` (Daemons de comunicação, relay, watchdog e webhook)

---

## 3. Validador de Endereçamento GPS Down Plant
Implementado no módulo `az000_governance/plant/addressing.py`:
- Validação estrita contra a gramática `TERRENO/COMODO/MODULO/SUBMODULO:PORTA`.
- Função `validate_down_plant_address(addr)` retornando veredito booleano sem levantar exceções não tratadas.
- Função `parse_down_plant_address(addr)` retornando objeto tipado e imutável `DownPlantAddress`.
- Checagem automática do cômodo contra o catálogo topológico oficial da ARCA.

---

## 4. Matriz de Critérios de Fechamento (ARCA `ROOM-03`)
| Critério Canônico | Evidência Factual | Veredito |
| :--- | :--- | :---: |
| `03_ADDRESS_SCHEMA.md validado` | Gramática validada por testes unitários e parser programático implementado. | **PASS** |
| `Workspaces de agentes confinados` | Mapeamento de pastas, portas de loopback segregadas (8765/8766) e ausência de vazamento. | **PASS** |
| `Estrutura física do Vault mapeada` | Todas as 11 seções do Vault existem fisicamente com seus respectivos `INDEX.md`. | **PASS** |
| `Dependências montantes satisfeitas` | `GOVERNANCE` e `WORLD` formalmente fechados com veredito `COMPLETE`. | **PASS** |

---

## 5. Conclusão e Habilitação do Próximo Cômodo
O cômodo **`PLANT` (Tier 3)** atinge o estado:
**`ROOM_STATUS: COMPLETE`**

O próximo cômodo elegível na ordem topológica da ARCA é:
> **`PORTS` (Tier 4)** — *Portas Tipadas, Esquemas de Endereçamento e Protocolos de Despacho*.
