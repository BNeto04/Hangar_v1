# 16. Extensão Local Manifest V3 para Inbound Wake Autônomo no ChatGPT

**Data:** 2026-09-04  
**Card ID:** `t_bridge_inbound_wake_extension_01`  
**CALL ID:** `CALL-BRIDGE-INBOUND-WAKE-IMPLEMENTATION-001` (`CG-000117`)  
**Status do Gate:** `QUALITY_GATE_PASS`  
**Fase:** Review / T4 (Parada Estrita aguardando carregamento pelo Owner)  

---

## 1. Decisão do Planner: EXTENSION vs CDP/Playwright

| Dimensão | Opção 1: Extensão Manifest V3 (`EXTENSION`) | Opção 2: CDP / Playwright (`CDP`) |
|---|---|---|
| **Impacto no Browser** | **Zero.** Não interfere nas abas abertas ou processos existentes do Chrome. | **Crítico.** Exige encerrar todas as instâncias do Chrome para relançar com `--remote-debugging-port=9222`. |
| **Isolamento de Segurança** | Escopo restrito via `host_permissions` a `chatgpt.com` e `127.0.0.1:8765`. | Acesso total irrestrito ao navegador via depuração remota. |
| **Reversibilidade** | 100% reversível via `chrome://extensions` com um clique. | Requer reversão de atalhos e flags no sistema operacional. |
| **Complexidade e Peso** | Minimalista (~150 linhas de JS/JSON puros, sem dependências). | Exige binários pesados de browser automation. |
| **Veredito do Planner** | **ESCOLHIDA (MENOR IMPLEMENTAÇÃO FACTUAL)** | Rejeitada pelo risco operacional ao ambiente do Owner. |

---

## 2. Arquitetura Implementada

### Componentes:
1. **Pacote da Extensão (`bridge/extension/`):**
   - `manifest.json`: Manifest V3 declarando permissões estritas para `https://chatgpt.com/*` e `http://127.0.0.1:8765/*`.
   - `content.js`: Script executado em document_idle que realiza polling a cada 4 segundos no relay local.
     - Ao detectar `pending_wake: true` com `message_id` inédito, localiza o campo `#prompt-textarea`, insere `"v"` e dispara o botão de envio.
     - Envia ACK imediato para `POST /ack`, desarmando o wake e impedindo duplicação (anti-loop / dedupe).
2. **Micro-servidor de Sinalização Local (`bridge/inbound_relay_server.py`):**
   - Roda em `http://127.0.0.1:8765` com CORS habilitado.
   - Endpoint `GET /status`: Retorna estado de wake para a extensão.
   - Endpoint `POST /ack`: Confirma o consumo do wake.
   - Endpoint `POST /arm_wake`: Armado automaticamente após postagem de RESULT no PR #1.

---

## 3. Instruções de Ativação pelo Proprietário (10 segundos)

Para ativar a injeção automática no ChatGPT Web:
1. No Google Chrome, acesse: `chrome://extensions`
2. No canto superior direito, ative a chave **"Modo do desenvolvedor"** (*Developer mode*).
3. No canto superior esquerdo, clique no botão **"Carregar sem compactação"** (*Load unpacked*).
4. Selecione a pasta:
   `C:\Users\PICHAU\Hangar_v1\bridge\extension`
5. Pronto! A extensão ficará ativa e sincronizará automaticamente os turnos do ChatGPT.

---

## 4. Regra de Parada e Status do Gate
- Conforme instrução expressa da chamada `CG-000117`:
  > *"STOP em T4/Review se ainda depender de passo manual do Owner."*
- Como a instalação da extensão exige a ação física do Owner em `chrome://extensions`, o card `t_bridge_inbound_wake_extension_01` é mantido estritamente em **Review / T4**, aguardando homologação do Proprietário.
