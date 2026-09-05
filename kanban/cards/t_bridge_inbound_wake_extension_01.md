# T-BRIDGE-INBOUND-WAKE-EXTENSION-01: Extensao Local Manifest V3 para Inbound Wake Autonomo no ChatGPT

- **CARD_ID:** `t_bridge_inbound_wake_extension_01`
- **STATUS:** `review`
- **PRIORITY:** `1`
- **CREATED_AT:** `1788559661`
- **COMPLETED_AT:** `null`

## Descrição
Implementacao da solucao minimalista, reversivel e purpose-first para fechamento do gap RESULT -> ChatGPT:
- Decisao do Planner: EXTENSION (Manifest V3 local) > CDP/Playwright (evita matar sessao do Chrome do Owner).
- Servidor local de status/wake em 127.0.0.1:8765.
- Content script seguro em bridge/extension com dedupe idempotente anti-loop.
- Documentacao canonica em DOCS/16_CHATGPT_INBOUND_WAKE_EXTENSION.md.
- Parada estrita em Review / T4 aguardando carregamento manual pelo Owner em chrome://extensions.

## Metadados Fatuais
```json
{}
```
