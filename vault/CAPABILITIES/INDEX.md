# ⚡ CAPABILITIES (Cômodo Tier 5)

**Status do Cômodo:** `COMPLETE`  
**Tier:** 5  
**Topologia de Dependências:** `GOVERNANCE (Tier 1)` -> `PORTS (Tier 4)` -> `CAPABILITIES (Tier 5)` -> `MACHINES (Tier 6)`  
**Endereço GPS Canônico:** `Hangar_v1/CAPABILITIES/REGISTRY/CATALOG:P-CAP-REGISTRY-01`  
**Referência Canônica ARCA:** `az000_governance/arca/canonical_domain_rules.py` (Regras `R-DOM-005` e `R-DOM-006`)

---

## 1. Definição Ontológica

O cômodo **CAPABILITIES** abriga as bibliotecas e motores estruturais que conferem inteligência operativa ao Hangar V1. Cada capacidade opera como um motor determinístico com portas tipadas e contrato acíclico de dependências.

---

## 2. Catálogo Canônico de Capacidades Ativas

| Capacidade | Versão | Porta Primária Down Plant | Dependências Diretas | Descrição |
|---|---|---|---|---|
| `GRAPHIFY` | 1.0.0 | `Hangar_v1/CAPABILITIES/ENGINES/GRAPHIFY:P-CAP-GRAPHIFY-01` | *Nenhuma* | Extração e auditoria determinística de grafos e wikilinks |
| `OPEN_DESIGN` | 1.0.0 | `Hangar_v1/CAPABILITIES/ENGINES/OPEN_DESIGN:P-CAP-OPENDESIGN-01` | `GRAPHIFY` | Especificações abertas e modelagem visual/ontológica |
| `PONYTAIL` | 1.0.0 | `Hangar_v1/CAPABILITIES/ENGINES/PONYTAIL:P-CAP-PONYTAIL-01` | `GRAPHIFY` | Curadoria da árvore documental e higienização do Vault |
| `IMPROVE` | 1.0.0 | `Hangar_v1/CAPABILITIES/ENGINES/IMPROVE:P-CAP-IMPROVE-01` | `GRAPHIFY` | Motor de evolução estrutural e mitigação de débito técnico |
| `RUFLO` | 1.0.0 | `Hangar_v1/CAPABILITIES/ENGINES/RUFLO:P-CAP-RUFLO-01` | `IMPROVE`, `PONYTAIL` | Orquestração determinística de pipelines e workflows |

---

## 3. Invariantes Canônicas (ARCA)

1. **R-DOM-005 (Ordem Sequencial de Cômodos):** CAPABILITIES depende estritamente do fechamento completo de `PORTS (Tier 4)` e habilita `MACHINES (Tier 6)`.
2. **R-DOM-006 (ARCA Fonte Única da Verdade):** Todas as regras ontológicas e de aciclicidade derivam da ARCA sem duplicações locais.
3. **Aciclicidade Obrigatória:** Nenhuma capacidade pode introduzir dependência circular (grafo dirigido acíclico estrito - DAG).
