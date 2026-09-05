# 🔌 PORTS (Cômodo Tier 4)

**Status do Cômodo:** `COMPLETE`  
**Tier:** 4  
**Topologia de Dependências:** `GOVERNANCE (Tier 1)` -> `WORLD (Tier 2)` -> `PLANT (Tier 3)` -> `PORTS (Tier 4)` -> `CAPABILITIES (Tier 5)`  
**Endereço GPS Canônico:** `Hangar_v1/PORTS/REGISTRY/DISPATCHER:P-PORTS-ROUTER-01`  
**Referência Canônica ARCA:** `az000_governance/arca/canonical_domain_rules.py` (Regras `R-DOM-005` e `R-DOM-006`)

---

## 1. Definição Ontológica

O cômodo **PORTS** estabelece o barramento determinístico de comunicação inter-módulos e inter-cômodos do Hangar V1. Toda interação entre agentes, robôs ou componentes é mediada por portas canônicas tipadas, proibindo acessos laterais ou acoplamentos diretos não mapeados.

---

## 2. Catálogo Canônico de Portas Primárias

| Endereço Down Plant | Direção | Schema Permitido | Descrição |
|---|---|---|---|
| `Hangar_v1/GOVERNANCE/OWNER_INTENT/INGESTOR:P-GOV-INTENT-IN-01` | IN | `CALL_ENVELOPE_V1` | Ingestão e selagem criptográfica de diretivas do Proprietário |
| `Hangar_v1/WORLD/MODEL/SPATIAL_CANVAS:P-WORLD-CANVAS-NAV-01` | INOUT | `CANVAS_QUERY_V1` | Navegação e auditoria espacial do grafo de mundo |
| `Hangar_v1/PLANT/ADDRESSING/GPS_PARSER:P-PLANT-ADDR-RESOLVER-01` | INOUT | `ADDR_RESOLVE_V1` | Resolução e validação de endereços Down Plant |
| `Hangar_v1/PORTS/REGISTRY/DISPATCHER:P-PORTS-ROUTER-01` | INOUT | `PORT_ENVELOPE_V1` | Roteamento e despacho determinístico de envelopes |

---

## 3. Invariantes Canônicas (ARCA)

1. **R-DOM-005 (Ordem Sequencial de Cômodos):** PORTS só atua sobre cômodos a montante que já estejam no estado `COMPLETE` (`GOVERNANCE`, `WORLD`, `PLANT`).
2. **R-DOM-006 (ARCA Fonte Única da Verdade):** Os contratos de envelope e regras de validação derivam diretamente da especificação ARCA e de `DOCS/03_ADDRESS_SCHEMA.md`.
3. **Imutabilidade e Integridade de Carga:** Todo envelope transitado possui digest SHA-256 de payload verificado no momento do despacho.
