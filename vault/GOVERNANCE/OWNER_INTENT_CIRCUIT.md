# ⚡ CIRCUITO DE INTENÇÃO DO PROPRIETÁRIO (OWNER INTENT)

O Circuito de Intenção do Proprietário garante que toda ação de relevância arquitetural ou impacto em produção tenha origem direta, inequívoca e auditável na vontade do Proprietário.

- **Módulos Python:**
  - [`az000_governance/owner_intent/circuit.py`](file:///C:/Users/PICHAU/Hangar_v1/az000_governance/owner_intent/circuit.py)
  - [`az000_governance/owner_intent/contracts.py`](file:///C:/Users/PICHAU/Hangar_v1/az000_governance/owner_intent/contracts.py)
  - [`az000_governance/owner_intent/ingestor.py`](file:///C:/Users/PICHAU/Hangar_v1/az000_governance/owner_intent/ingestor.py)
- **Script CLI:** [`scripts/owner_sovereignty.py`](file:///C:/Users/PICHAU/Hangar_v1/scripts/owner_sovereignty.py)

---

## 1. Canais Autorizados de Ingestão
1. **Canal Telegram Soberano:** Mensagens diretas para `@Sentinela_PC_CasaBot` validadas por Chat ID.
2. **Canal GitHub PR #1:** Despachos com identificador soberano no Pull Request oficial.
3. **Canal Local (CLI / Down Plant):** Invocação direta de scripts autorizados pelo terminal do Proprietário.

---

## 2. Invariantes de Proteção
- **Anti-Hallucination & Anti-Bypass:** Nenhum agente de IA (Codex, Antigravity, ChatGPT) pode gerar um token soberano simulando a aprovação do Proprietário.
- **Fail-Closed em Autenticação:** Se a assinatura ou origem não bater com os registros de autoridade, a operação é rejeitada e registrada em log de segurança.

---

## 3. Navegação Interna
- [[GOVERNANCE/INDEX|Voltar ao Dashboard de Governança]]
- [[GOVERNANCE/ARCA_SPEC_AND_ROOM_ORDER|Ver Regras Canônicas ARCA]]
