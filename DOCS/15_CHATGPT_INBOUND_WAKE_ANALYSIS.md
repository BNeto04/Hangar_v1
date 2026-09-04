# 15. Mapeamento de Mecanismos e Análise Factual de Gap Inbound (ChatGPT)

**Data:** 2026-09-04  
**Card ID:** `t_bridge_chatgpt_inbound_wake_01`  
**CALL ID:** `CALL-BRIDGE-CHATGPT-INBOUND-WAKE-001` (`CG-000116`)  
**Status do Gate:** `QUALITY_GATE_PASS` (com `IMPLEMENTATION_GAP / HOLD` legítimo)  
**Fase:** Review / T4  

---

## 1. Contexto e Objetivo
Atender ao requisito de fechar o ciclo operacional `RESULT -> ChatGPT` sem intervenção humana do Proprietário (sem digitação manual de `v` na interface web do ChatGPT).

---

## 2. Matriz de Mecanismos Reais Disponíveis

| Mecanismo | Descrição Técnica | Suportado Oficialmente? | Seguro / Viável no Ambiente Atual? | Veredito |
|---|---|---|---|---|
| **1. OpenAI Public Inbound Webhook** | API oficial que injeta mensagem em chat web ativo. | **Não** (OpenAI não expõe endpoints push para Web SPA). | Não aplicável. | **INVIÁVEL** |
| **2. GitHub Webhook / Event Stream** | Webhook do PR #1 disparando notificação direta ao ChatGPT. | **Não** (ChatGPT Web não possui listener inbound HTTP aberto). | Não aplicável. | **INVIÁVEL** |
| **3. Extensão de Browser / Web Request Listener** | Extensão Chrome local que escuta relay SSE e injeta texto no DOM do chat. | Parcial (viável via desenvolvimento de extensão unpackaged no Chrome). | Exige permissões de extensão e Developer Mode ativo no Chrome. | **VIÁVEL COM DESENVOLVIMENTO DEDICADO** |
| **4. Conector Local via Chrome DevTools Protocol (CDP)** | Script Playwright/Python conectando via `--remote-debugging-port` na porta 9222 do Chrome existente. | Sim (padrão CDP para automação). | **Bloqueio Factual:** O Chrome atual do Owner não está rodando com a porta de depuração habilitada. Exige restart do navegador com flag específica. | **BLOQUEIO FACTUAL ATUAL** |

---

## 3. Deliberação de Fechamento do Gap
Conforme a regra estrita de governança e segurança:
> *"Se não houver mecanismo inbound suportado/seguro, retornar HOLD/IMPLEMENTATION_GAP com o menor bloqueio factual. Não simular PASS com Git/log/Telegram."*

1. **Estado do Requisito:** **`IMPLEMENTATION_GAP / HOLD LEGÍTIMO`**.
2. **Menor Bloqueio Factual Identificado:**
   - Ausência de inicialização do navegador Chrome com a flag `--remote-debugging-port=9222` e ausência de extensão local autorizada pelo Owner para manipulação do DOM da página `chatgpt.com`.
3. **Recomendação de Próximo Passo Arquitetural (se autorizado pelo Owner):**
   - Criar um script inicializador de Chrome com debugging port ou uma extensão lightweight (`hangar-bridge-extension`) em `manifest v3` que se comunique com o relay local `http://127.0.0.1:8080/stream` e envie o pulso de sincronização diretamente no chat.
   - Até que o Owner autorize explicitamente essa intervenção no navegador, o ciclo permanece seguro com o envio de `v` via Telegram ou via terminal.

---

## 4. Invariantes Preservados
- **Soberania do Owner:** Nenhuma automação intrusiva de browser é executada sem homologação prévia do Proprietário.
- **Fail-Closed:** Proibido simular sucesso de automação de UI sem a respectiva porta ou extensão ativa.
- **Dedupe e Anti-Loop:** Qualquer automação futura deverá respeitar chave idempotente por `MESSAGE_ID` do RESULT para evitar envio duplicado.
