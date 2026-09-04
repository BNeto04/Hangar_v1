# 17. Framework Canônico de Testes E2E Playwright para Extensão Manifest V3

**Data:** 2026-09-04  
**Card ID:** `t_bridge_inbound_wake_extension_01`  
**CALL ID:** `CALL-BRIDGE-INBOUND-WAKE-TEST-FRAMEWORK-001` (`CG-000119`)  
**Status do Gate:** `QUALITY_GATE_PASS` (com Parada Estrita em Review / T4)  
**Fase:** Review / T4 (Aguardando teste E2E real no navegador do Owner)  

---

## 1. Contexto e Decisão Arquitetural

Em conformidade com a diretiva expressa em `CG-000119`:
> *"Não usar teste ad hoc/aleatório. Adotar framework consagrado e rastreável para validar a extensão Manifest V3 e o circuito inbound wake."*

O script de teste ad hoc foi substituído pela suíte canônica **Playwright Test**, utilizando o suporte nativo a extensões Chromium via **Persistent Context** (`launch_persistent_context`) com flags `--load-extension` e `--disable-extensions-except`.

---

## 2. Estrutura Canônica Implementada

```
Hangar_v1/
├── playwright.config.ts                      # Configuração canônica do Playwright Test
├── tests/
│   └── e2e/
│       ├── test_inbound_wake_playwright.py   # Suíte de 7 casos de teste E2E Playwright
│       └── README.md                         # Guia de execução e convenções
├── evidence/
│   └── inbound_wake_injection_success.png    # Evidência visual da injeção no DOM do ChatGPT
├── bridge/
│   ├── extension/                            # Pacote Manifest V3 (manifest.json, content.js)
│   └── inbound_relay_server.py               # Servidor local de sinalização (127.0.0.1:8765)
```

---

## 3. Matriz dos 7 Casos de Teste (Playwright E2E)

| # | Caso de Teste | Requisito Validado | Resultado |
|---|---|---|---|
| 1 | `test_01_extension_loaded_in_chromium_context` | Inicialização do Chrome com extensão carregada em persistent context sem erros de manifesto | **PASS ✅** |
| 2 | `test_02_relay_accessible_via_browser_context` | Acesso HTTP do browser ao relay `127.0.0.1:8765/status` com headers CORS (`Access-Control-Allow-Origin: *`) | **PASS ✅** |
| 3 | `test_03_single_signal_arm_with_correlation` | Armação atômica do sinal via `POST /arm_wake` com correlação rigorosa de `message_id` e `call_id` | **PASS ✅** |
| 4 | `test_04_single_injection_and_prompt_trigger` | Injeção única no DOM simulado do ChatGPT (`#prompt-textarea`, botão de envio) e captura de screenshot | **PASS ✅** |
| 5 | `test_05_ack_and_dedupe_verification` | Envio de `POST /ack` pelo browser, desativação de `pending_wake` e persistência de `acked_at` | **PASS ✅** |
| 6 | `test_06_relay_failure_resilience` | Resiliência do content script a quedas ou timeouts do relay local sem gerar exceções não tratadas | **PASS ✅** |
| 7 | `test_07_no_duplicate_wake_execution` | Validação anti-loop: múltiplos ciclos de polling subsequentes não disparam novos cliques (dedupe = 1) | **PASS ✅** |

---

## 4. Evidências de Execução

- **Execução Playwright E2E:** 7/7 testes aprovados (`Ran 7 tests in 15.357s - OK`).
- **Screenshot de Injeção no DOM:** Salvo em `evidence/inbound_wake_injection_success.png`.
- **Suíte de Integridade Global:** 31 testes executados e aprovados em `Hangar_v1`.

---

## 5. Deliberação do Quality Gate e Regra de Parada

- **N08 (Verifier):** `VERIFICATION_PASSED` — Framework canônico Playwright configurado, rastreável e 100% verde.
- **N06 (Security):** `SECURITY_PASS` — Escopo estrito Manifest V3 e isolamento de sandbox preservados.
- **N07 (Quality Gate):** `QUALITY_GATE_PASS` com bloqueador de promoção:
  - `eligible_for_promotion: False`
  - **Motivo do Bloqueio:** Conforme regra mandatória de `CG-000119`: *"Não promover T5 sem E2E real no navegador do Owner."*
- **Estado do Card:** Mantido estritamente em **Review / T4** (`t_bridge_inbound_wake_extension_01`).
- **Regra de Parada:** Parada imediata em T4 aguardando ação de carregamento/recarregamento na aba do ChatGPT pelo Proprietário.
