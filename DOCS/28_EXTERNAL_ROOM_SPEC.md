# HANGAR V1 — 28. ESPECIFICAÇÃO DO CÔMODO EXTERNAL (TIER 8)

**STATUS:** `COMPLETE`  
**DATA:** `2026-09-04`  
**AUTOR:** `Down Plant Technical Executor`  
**AUDITORIA:** `Codex / ChatGPT (CG-000138 / CALL-HANGAR-NEXT-ROOM-EXTERNAL-001)`  
**ORDEM DE CÔMODOS:** Tier 8 de 11  

---

## 1. Propósito e Fronteiras

O cômodo **EXTERNAL** consolida os adaptadores de borda periféricos, canais de transporte orientados a eventos e pontes de comunicação com agentes e sistemas externos ao Hangar V1. Ele isola o monólito interno contra payloads maliciosos, injeções de prompt e requisições não autenticadas através do `ExternalBridgeGateway`, aplicando validação criptográfica HMAC SHA-256, deduplicação em janela temporal e invariante estrita `FAIL_CLOSED`.

---

## 2. Reconciliação Topológica e Invariantes ARCA

- **Invariante R-DOM-005 (ROOM_BY_ROOM_ORDER):**
  - Upstream concluído e auditado: `GOVERNANCE (Tier 1)`, `WORLD (Tier 2)`, `PLANT (Tier 3)`, `PORTS (Tier 4)`, `CAPABILITIES (Tier 5)`, `MACHINES (Tier 6)` e `INTELLIGENCE (Tier 7)` com `ROOM_STATUS: COMPLETE`.
  - Cômodo ativo: `EXTERNAL (Tier 8)` concluído com gateway autenticado, deduplicação ativa e testes unitários aprovados.
  - Downstream habilitado: `TRACE (Tier 9)` torna-se o próximo cômodo elegível na ordem topológica da ARCA.

- **Invariante R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA):**
  - Os critérios canônicos de fechamento derivam da tabela `_CANONICAL_ROOMS` em `az000_governance/arca/canonical_domain_rules.py`:
    1. *"Transportes orientados a eventos comprovados"*
    2. *"Deduplicação e HMAC SHA-256 ativos"*

- **Invariante R-DOM-002 (FAIL_CLOSED_SYSTEMIC):**
  - Assinatura ausente ou mismatch HMAC SHA-256 resulta em rejeição imediata (`accepted=False`).
  - Canais não homologados ou não registrados são sumariamente descartados.

---

## 3. Implementação Técnica (`az000_governance/external/`)

1. **Modelos Canônicos (`models.py`):**
   - `ExternalChannel`: Enum tipado com canais homologados (`GITHUB_WEBHOOK`, `GITHUB_PR_RELAY`, `TELEGRAM_BOT`, `CLOUDFLARE_TUNNEL`, `BROWSER_BRIDGE`).
   - `ExternalAuthPolicy`: Políticas imutáveis por canal definindo esquemas de autenticação (`HMAC_SHA256`, `TOKEN_BEARER`, etc.) e segredos criptográficos.
   - `ExternalEventPayload`: Estrutura de eventos recebidos na borda com metadados e corpo serializável.
   - `ExternalTransmissionResult`: Veredito imutável de aceitação, causa de rejeição e hash SHA-256.

2. **Gateway de Borda (`gateway.py`):**
   - `ExternalBridgeGateway`:
     - Verificação HMAC SHA-256 com tempo constante (`hmac.compare_digest`).
     - Deduplicação de eventos por ID e hash SHA-256 do corpo serializado.
     - Transformação de eventos aprovados em `TypedPortEnvelope` Down Plant direcionados ao despachante de governança (`Hangar_v1/GOVERNANCE/INGESTION/DISPATCHER:P-GOV-INGEST-01`).

---

## 4. Evidências de Validação (Gates N08 / N06 / N07)

- `tests/test_external_room.py`: 6 testes unitários cobrindo autenticação, integridade, fail-closed, deduplicação e dependências upstream.
- Regressão do repositório: 61/61 testes aprovados com código de saída 0.
- Cartão Hermes: `t_hangar_external_room_completion_01` promovido para DONE (T5).
- Sincronização do mirror: `kanban_mirror.json` atualizado.
