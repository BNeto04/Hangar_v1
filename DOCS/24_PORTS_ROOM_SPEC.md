# HANGAR V1 — 24. ESPECIFICAÇÃO DO CÔMODO PORTS (TIER 4)

**STATUS:** `COMPLETE`  
**DATA:** `2026-09-04`  
**AUTOR:** `Down Plant Technical Executor`  
**AUDITORIA:** `Codex / ChatGPT (CG-000134 / CALL-HANGAR-NEXT-ROOM-PORTS-001)`  
**ORDEM DE CÔMODOS:** Tier 4 de 11  

---

## 1. Propósito e Fronteiras

O cômodo **PORTS** é a infraestrutura de enlace e comunicação canônica do Hangar V1. Ele define como os cômodos e submódulos da planta baixa (`PLANT`) trocam intenções, comandos e evidências através de portas tipadas (`PortDefinition`), validando envelopes com assinatura SHA-256 e garantindo entrega sem efeitos colaterais ocultos.

---

## 2. Reconciliação Topológica e Invariantes ARCA

- **Invariante R-DOM-005 (ROOM_BY_ROOM_ORDER):**
  - Execução estritamente sequencial.
  - Upstream concluído e validado: `GOVERNANCE (Tier 1)`, `WORLD (Tier 2)` e `PLANT (Tier 3)` estão todos em `COMPLETE`.
  - Cômodo ativo: `PORTS (Tier 4)` fechado com 100% de escopo funcional e testes unitários.
  - Downstream destravado: `CAPABILITIES (Tier 5)` torna-se o próximo cômodo elegível.

- **Invariante R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA):**
  - Todas as regras e contratos derivam da ARCA (`az000_governance/arca/canonical_domain_rules.py`) e de `DOCS/03_ADDRESS_SCHEMA.md`.
  - Nenhuma regra de domínio é duplicada ou redefinida localmente.

---

## 3. Implementação Técnica (`az000_governance/ports/`)

1. **`TypedPortEnvelope` (`envelope.py`):**
   - Campos: `schema`, `source_id`, `target`, `timestamp_iso`, `payload`, `evidence_refs`, `payload_sha256`.
   - Valida endereços de origem e destino contra o parser canônico Down Plant (`validate_down_plant_address`).
   - Calcula e confere SHA-256 determinístico sobre o payload JSON canonicalizado.
2. **`PortRegistry` (`registry.py`):**
   - Registra portas tipadas (`PortDefinition`) com checagem de direção (`IN`, `OUT`, `INOUT`) e schemas permitidos.
   - Suporte a rotas e subscrições de eventos (`subscribe` / `dispatch`).
   - Barramento de rastreamento com histórico de despachos (`get_history`).

---

## 4. Evidências de Validação (Gates N08 / N06 / N07)

- `tests/test_ports_room.py`: 6 testes unitários aprovados.
- Regressão do repositório: 37+ testes aprovados com código de saída 0.
- Cartão Hermes: `t_hangar_ports_room_completion_01` promovido para DONE (T5).
- Mirror de governança sincronizado em `kanban_mirror.json`.
