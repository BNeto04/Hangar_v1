# T-BRIDGE-GITHUB-WEBHOOK-SENTINELA-01: Entrega Orientada a Eventos via GitHub Webhook e Túnel Local Seguro

- **CARD_ID:** `t_bridge_github_webhook_sentinela_01`
- **STATUS:** `in_progress`
- **PRIORITY:** `1`
- **CREATED_AT:** `1788572083`
- **COMPLETED_AT:** `null`

## Descrição
DP_PROJECT: Hangar_v1
DP_TERRAIN: Hangar_v1
DP_ROOM: BRIDGE
DP_MODULE: WEBHOOK_INBOUND
DP_SUBMODULE: GITHUB_WEBHOOK_ADAPTER
DP_PORT: P-BRIDGE-GITHUB-WEBHOOK-SENTINELA-01
DP_CIRCUIT: CIRCUIT_GITHUB_PR1_TO_SENTINELA
DP_ARTIFACT: bridge/github_webhook_server.py + bridge/tunnel_manager.py + bridge/sentinela_telegram.py
DP_ACTION: Implementar endpoint HTTP local com validação HMAC SHA-256 e túnel seguro reverso para entrega orientada a evento no Sentinela.
DP_TARGET: Eventos issue_comment da PR #1 no repositório BNeto04/Hangar_v1.
DP_IMPACT_DIRECT: Substitui o wake manual/polling primário no sentido GitHub -> Sentinela por entrega direta orientada a eventos.
DP_IMPACT_INDIRECT: Polling mantido como fallback de resiliência. Sem impacto em CronosEdu ou nós de IA externos.
DP_AXIS_DOCUMENTATION: DOCS/18_GITHUB_WEBHOOK_EVENT_DRIVEN_BRIDGE.md
DP_AXIS_CODE: bridge/github_webhook_server.py, bridge/tunnel_manager.py
DP_AXIS_TEST: tests/test_github_webhook_server.py (unitário com HMAC, dedupe, filtragem de TYPE: CALL e fallback)
DP_OUT_OF_SCOPE: Alteração na extensão de retorno RESULT -> ChatGPT; alteração nos cards em T5; redesign da arquitetura da ponte.
DP_ACCEPTANCE:
  1. Endpoint local valida assinatura HMAC SHA-256 (X-Hub-Signature-256) fail-closed (rejeita payloads inválidos com HTTP 401).
  2. Filtra estritamente comentários da PR #1 que contenham TYPE: CALL.
  3. Deduplicação por delivery_id (X-GitHub-Delivery) e comment_id.
  4. Dispara o processamento do Antigravity exatamente 1x.
  5. Resposta HTTP rápida (200 OK / 202 Accepted) em < 500ms.
  6. Nenhuma credencial em log.
  7. Rollback claro e reversibilidade total.
DP_ROLLBACK: Parar o túnel e microserviço, deletar o webhook via API do GitHub (DELETE /repos/BNeto04/Hangar_v1/hooks/{id}) e manter o github_pr_relay.py em polling contínuo.


## Metadados Fatuais
```json
{}
```
