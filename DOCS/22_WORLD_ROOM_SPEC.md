# 22. Especificação Canônica e Fechamento do Cômodo WORLD (Tier 2)

## 1. Identificação e Coordenadas Down Plant
- **Artefato:** `DOCS/22_WORLD_ROOM_SPEC.md`
- **Chamada:** `CG-000132` (`CALL-HANGAR-NEXT-ROOM-WORLD-001`)
- **Cartão Kanban:** `t_hangar_world_room_completion_01`
- **CÔMODO:** `WORLD` (Tier 2)
- **MÓDULO:** `MODEL`
- **SUBMÓDULO:** `SPATIAL_CANVAS`
- **PORTA:** `P-WORLD-CANVAS-NAV-01`
- **ENDEREÇO CANÔNICO:** `Hangar_v1/WORLD/MODEL/SPATIAL_CANVAS:P-WORLD-CANVAS-NAV-01`
- **DEPENDÊNCIA A MONTANTE:** `GOVERNANCE` (Tier 1) — **FECHADA E AUDITADA (`ROOM_STATUS: COMPLETE`)**.

---

## 2. Ontologia de Mundo & Alinhamento com a ARCA
O cômodo WORLD implementa a representação espacial e relacional do sistema segundo as regras de domínio da **ARCA** (`az000_governance/arca/canonical_domain_rules.py`):
1. **`R-DOM-005 (ROOM_BY_ROOM_ORDER)`:** Execução estritamente delimitada ao cômodo WORLD (Tier 2), sem invasão de cômodos posteriores (`PLANT`, `PORTS`, etc.).
2. **`R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA)`:** As definições de papéis e regras não são duplicadas aqui; apontam diretamente para o módulo ARCA e para o monólito `GOVERNANCE.md`.

---

## 3. O Canvas Espacial Mestre (`Master_World.canvas`)
O arquivo `vault/WORLD/Master_World.canvas` atua como a projeção visual 2D oficial do território:
- **Nós Totais:** 17 nós temáticos delimitando os 4 planos ontológicos.
- **Arestas Totais:** 24 arestas direcionadas modelando fluxos de comando, despacho, auditoria e trânsito de envelopes.
- **Integridade de Wikilinks:** 100% dos wikilinks `[[...]]` no canvas resolvem estritamente para arquivos existentes em `vault/` (zero links quebrados).

---

## 4. Matriz de Critérios de Fechamento (ARCA `ROOM-02`)
| Critério Canônico | Evidência Factual | Veredito |
| :--- | :--- | :---: |
| `01_WORLD_MODEL.md validado` | Existente, integrado ao Graphify e sem violação de invariantes. | **PASS** |
| `Master_World.canvas com zero links quebrados` | Validado via `tests/test_world_room.py` (17/17 links resolvidos). | **PASS** |
| `Ontologia de entidades consolidada` | 5 entidades e 4 planos alinhados à ARCA e documentados em `vault/WORLD/INDEX.md`. | **PASS** |
| `Dependência montante satisfeita` | Cômodo `GOVERNANCE` (Tier 1) formalmente fechado (`ROOM_STATUS: COMPLETE`). | **PASS** |

---

## 5. Conclusão e Habilitação do Próximo Cômodo
Com a consolidação documental, visual e teste automatizado, o cômodo **`WORLD` (Tier 2)** atinge o estado:
**`ROOM_STATUS: COMPLETE`**

O próximo cômodo elegível na ordem topológica da ARCA é:
> **`PLANT` (Tier 3)** — *Topologia Física, Workspaces de Execução e Confinamento de Pastas*.
