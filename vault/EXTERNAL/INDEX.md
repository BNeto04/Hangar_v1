# 🌐 EXTERNAL (Tier 8)

Mundo externo, integrações externas, relays, APIs, webhooks e fronteiras periféricas.

---

## 1. Identificação Canônica
- **Cômodo:** `EXTERNAL`
- **Tier:** 8 de 11
- **Módulo Técnico:** `az000_governance.external`
- **Porta Principal:** `Hangar_v1/EXTERNAL/GATEWAY/INBOUND:P-EXT-INBOUND-01`
- **Referência Normativa:** `DOCS/28_EXTERNAL_ROOM_SPEC.md`
- **Invariantes ARCA:** `R-DOM-002` (FAIL_CLOSED), `R-DOM-005` (ROOM_BY_ROOM_ORDER), `R-DOM-006` (SINGLE_SOURCE_OF_TRUTH_ARCA)

---

## 2. Canais Homologados
- `GITHUB_WEBHOOK`: Eventos de push, issues e PRs com autenticação HMAC SHA-256.
- `GITHUB_PR_RELAY`: Sincronização bidirecional do PR #1 com ChatGPT/Codex.
- `TELEGRAM_BOT`: Sentinela de monitoramento e alertas operacionais.
- `CLOUDFLARE_TUNNEL`: Borda de tráfego seguro HTTP/WebSocket.
- `BROWSER_BRIDGE`: Bridge de extensão Chrome / interface web.

---

## 3. Critérios de Fechamento (ARCA)
1. **Transportes orientados a eventos comprovados:** Ativo via `ExternalBridgeGateway`.
2. **Deduplicação e HMAC SHA-256 ativos:** Implementado e validado por testes unitários e de integração.
