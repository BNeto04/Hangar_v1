# Suíte Canônica de Testes Playwright E2E — Hangar V1

## Objetivo
Framework oficial de testes ponta a ponta para validação da extensão Manifest V3 (`bridge/extension`) e do circuito de Inbound Wake do ChatGPT, em conformidade com o chamado `CG-000119` (`CALL-BRIDGE-INBOUND-WAKE-TEST-FRAMEWORK-001`).

## Estrutura
- `playwright.config.ts`: Configuração canônica do Playwright Test com persistent context e flags `--load-extension`.
- `test_inbound_wake_playwright.py`: Suíte de 7 casos de teste que cobrem isolamento, ciclo de sinal, injeção no DOM, ACK/dedupe, resiliência e ausência de duplicidade.
- `evidence/`: Diretório de artefatos de teste (screenshots de injeção, relatórios de execução).

## Como Executar
```bash
# Execução direta via unittest (sem dependências adicionais):
python -m unittest tests/e2e/test_inbound_wake_playwright.py

# Ou via pytest:
pytest tests/e2e/test_inbound_wake_playwright.py
```
