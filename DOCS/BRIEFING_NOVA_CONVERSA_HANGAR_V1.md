# 🚀 HANGAR V1 — DOSSIÊ COMPLETO DE TRANSIÇÃO E MAPA DE AMBIENTE

> **Instrução:** Cole este documento na primeira mensagem de uma nova conversa com o assistente/agente para retomar o trabalho com 100% de precisão factual, sem necessidade de pesquisa prévia ou reexplicações.

---

## 1. O QUE É O HANGAR V1 & MATRIZ DE AUTORIDADE (DOWN PLANT)

O **Hangar V1** é o ecossistema soberano de engenharia de software autônoma e orquestração multiagente da Syntheon ADK. Ele opera sob o modelo estrito **Down Plant**, com separação inegociável de autoridades:

1. **Manoel (O Proprietário Soberano — L0):**
   - Detém autoridade exclusiva e irrevogável sobre escopo, prioridade, homologação final, concessão de exceções e publicação em produção (Regra `R-DOM-001`).
   - Nenhuma máquina, SLM ou agente de IA tem poder de deliberação ou auto-aprovação.
2. **Codex / ChatGPT (Planejador Estratégico & Auditor Independente):**
   - Decompõe planos em rotas formais, audita evidências e despacha chamadas via barramento do GitHub PR #1.
   - Opera estritamente no modo *payload-in / parecer-out* (sem ferramentas de escrita ou execução direta).
3. **Antigravity (Executor Técnico Down Plant — N03):**
   - Detém o monopólio físico de mutação de arquivos no repositório e execução de comandos no terminal local.
   - Opera sob escopo autorizado, preserva alterações pré-existentes, gera testes e evidências determinísticas e **nunca se auto-homologa** (Regra `R-DOM-007`).

---

## 2. MAPA FÍSICO DE CAMINHOS E AMBIENTE LOCAL

| Entidade / Recurso | Caminho Físico no Windows | Finalidade Factual |
|---|---|---|
| **Repositório Central** | `C:\Users\PICHAU\Hangar_v1` | Checkout Git principal (`origin/main`). |
| **Workspace Default / Scratch** | `C:\Users\PICHAU\.gemini\antigravity\scratch` | Diretório de rascunhos e scripts temporários. |
| **App Data Antigravity** | `C:\Users\PICHAU\.gemini\antigravity` | Dados de runtime, logs e artefatos. |
| **Banco SQLite Hermes Kanban** | `C:\Users\PICHAU\AppData\Local\hermes\kanban.db` | Base viva dos 148 cartões da esteira de trabalho. |
| **Espelho Git do Kanban** | `C:\Users\PICHAU\Hangar_v1\kanban\kanban_state.json` | Sincronismo do Kanban versionado em Git. |
| **Cartões Individuais Kanban** | `C:\Users\PICHAU\Hangar_v1\kanban\cards\` | 148 arquivos Markdown (`<card_id>.md`). |
| **Vault Obsidian (Base)** | `C:\Users\PICHAU\Hangar_v1\vault` | Cofre de conhecimento vivo e modelo de mundo. |
| **Dashboard de Governança (Vault)** | `C:\Users\PICHAU\Hangar_v1\vault\GOVERNANCE\INDEX.md` | Painel mestre interativo de navegação. |
| **Canvas de Governança (Vault)** | `C:\Users\PICHAU\Hangar_v1\vault\GOVERNANCE\Governance.canvas` | Mapa visual nativo da Governança e Regras. |
| **Master World Canvas (Vault)** | `C:\Users\PICHAU\Hangar_v1\vault\WORLD\Master_World.canvas` | Ontologia espacial mestre (17 nós, 24 arestas). |
| **Pasta de Documentação Técnica** | `C:\Users\PICHAU\Hangar_v1\DOCS\` | 31 especificações normativas (`DOCS/01` a `DOCS/31`). |
| **Roadtrace de Governança** | `C:\Users\PICHAU\Hangar_v1\DOCS\09_HANGAR_GOVERNANCE_ROADTRACE.md` | Matriz de maturidade dos 6 Critérios. |
| **Circuito de Comunicação (Legado)** | `C:\Users\PICHAU\Downloads\circuito` | Arquivos `conversa de ia.txt` e `resposta do executor.txt`. |
| **Binário Codex CLI** | `C:\Users\PICHAU\AppData\Local\OpenAI\Codex\bin\d5f4c71927a04589\codex.exe` | Executável oficial da CLI do Codex. |
| **Sessões Locais do Codex** | `C:\Users\PICHAU\.codex\sessions\` | Rollouts e transcrições de sessões do Codex. |
| **Binário Cloudflared** | `C:\Users\PICHAU\Hangar_v1\bin\cloudflared.exe` | Túnel seguro para webhook do GitHub. |
| **Extensão Inbound Wake (Chrome)** | `C:\Users\PICHAU\Hangar_v1\bridge\extension` | Extensão Manifest V3 carregada em `chrome://extensions`. |
| **Ledger Criptográfico de Trace** | `C:\Users\PICHAU\Hangar_v1\runtime\traces\trace_ledger.jsonl` | Livro-razão append-only encadeado por SHA-256. |

---

## 3. MAPA DE REPOSITÓRIO REMOTO & BARRAMENTOS EXTERNOS

- **Repositório GitHub:** `https://github.com/BNeto04/Hangar_v1`
- **Branch Principal:** `main` (rastreada com `origin/main`).
- **Barramento de PR:** [Pull Request #1 (BNeto04/Hangar_v1)](https://github.com/BNeto04/Hangar_v1/pull/1) — Canal assíncrono onde ChatGPT/Codex posta `CALL` e Antigravity responde `RESULT`.
- **Canal Telegram Soberano:** Bot `@Sentinela_PC_CasaBot` (notificações de término e canal de emergência do Proprietário).
- **Token GitHub:** Carregado automaticamente via `bridge/tunnel_manager.py` (via arquivo `.env` ou variável de ambiente `GITHUB_TOKEN`).

---

## 4. TOPOLOGIA DA PLANTA FÍSICA: OS 11 CÔMODOS DA ARCA (100% FECHADOS)

A arquitetura da ARCA organiza o Hangar V1 em 11 Tiers ordenados cômodo por cômodo, todos com módulos de código, testes determinísticos e notas no Vault:

1. **Tier 1 — `GOVERNANCE`:**
   - Código: `az000_governance/arca/canonical_domain_rules.py`
   - Teste: `tests/test_arca_domain_rules.py` (6/6 PASS)
   - Vault: `vault/GOVERNANCE/` (`INDEX.md`, `Governance.canvas`, `ARCA_SPEC_AND_ROOM_ORDER.md`)
   - Regras: `R-DOM-001` (Soberania) a `R-DOM-007` (Sem Auto-Homologação), seladas por hash SHA-256.
2. **Tier 2 — `WORLD`:**
   - Código/Modelo: `vault/WORLD/Master_World.canvas` (17 nós, 24 arestas)
   - Teste: `tests/test_world_room.py` (4/4 PASS)
   - Vault: `vault/WORLD/INDEX.md`
3. **Tier 3 — `PLANT`:**
   - Código: `az000_governance/plant/addressing.py` (`DownPlantAddress`, gramática de 4 barras e 5 segmentos)
   - Teste: `tests/test_plant_room.py` (6/6 PASS)
   - Vault: `vault/PLANT/INDEX.md`
4. **Tier 4 — `PORTS`:**
   - Código: `az000_governance/ports/registry.py` e `envelope.py` (`TypedPortEnvelope`)
   - Teste: `tests/test_ports_room.py` (6/6 PASS)
   - Vault: `vault/PORTS/INDEX.md`
5. **Tier 5 — `CAPABILITIES`:**
   - Código: `az000_governance/capabilities/graphify_engine.py` (Graphify, Improve, Ponytail, Ruflo, Open Design)
   - Teste: `tests/test_capabilities_room.py` (6/6 PASS)
   - Vault: `vault/CAPABILITIES/INDEX.md`
6. **Tier 6 — `MACHINES`:**
   - Código: `az000_governance/machines/fsm.py` e `nano_machines.py` (FSM determinística, isolamento `NM-OBS-01` e `NM-EXEC-01`)
   - Teste: `tests/test_machines_room.py` (6/6 PASS)
   - Vault: `vault/MACHINES/INDEX.md`
7. **Tier 7 — `INTELLIGENCE`:**
   - Código: `az000_governance/intelligence/orchestrator.py` (10 papéis CHARs N01..N10 confinados com prova anti-alucinação)
   - Teste: `tests/test_intelligence_room.py` (6/6 PASS)
   - Vault: `vault/INTELLIGENCE/INDEX.md`
8. **Tier 8 — `EXTERNAL`:**
   - Código: `az000_governance/external/gateway.py` (HMAC SHA-256 constant-time, deduplicação anti-replay, fail-closed)
   - Teste: `tests/test_external_room.py` (6/6 PASS)
   - Vault: `vault/EXTERNAL/INDEX.md`
9. **Tier 9 — `TRACE`:**
   - Código: `az000_governance/trace/engine.py` (Ledger append-only encadeado por SHA-256)
   - Teste: `tests/test_trace_room.py` (6/6 PASS)
   - Vault: `vault/TRACE/INDEX.md`
10. **Tier 10 — `COCKPITS`:**
    - Código: `az000_governance/cockpits/controller.py` (Snapshot espacial unificado dos 11 cômodos e Teacher Mode)
    - Teste: `tests/test_cockpits_room.py` (6/6 PASS)
    - Vault: `vault/COCKPITS/INDEX.md`
11. **Tier 11 — `PRODUCTS`:**
    - Código: `az000_governance/products/manager.py` (Release notes dos 11 tiers v1.0.0 e manifesto com hash raiz)
    - Teste: `tests/test_products_room.py` (6/6 PASS)
    - Vault: `vault/PRODUCTS/INDEX.md`

---

## 5. MOTORES FORMAIS DE POLÍTICA (CEDAR & OPA)

Implementados no commit `91ab681` para erradicar o controle frágil por prompt de texto:
- **Motor Cedar (`az000_governance/policy/cedar_engine.py`):**
  - Modelo formal RBAC/ABAC com semântica estrita *permit / forbid* e *fail-closed default-deny*.
  - Regra: Soberania irrestrita ao Proprietário, monopólio de escrita para o Executor (`N03`) e modo estrito *read-only* para Pareceristas (`N04/N05/N06`).
- **Motor OPA (`az000_governance/policy/opa_engine.py`):**
  - Quality gates estilo Rego avaliando envelopes de evidência, hashes SHA-256 válidos de 64 caracteres e consenso entre pareceres.
- **Testes Unitários:** `tests/test_policy_engines.py` (6/6 PASS).

---

## 6. BARREIRAS DE CI/CD & COMANDOS DETERMINÍSTICOS

Para verificar o estado de integridade de todo o Hangar V1, execute no terminal PowerShell:

```powershell
# Executar a suíte completa de 92 testes determinísticos, árvore documental e espelho Kanban:
python scripts/git_enforcement.py check-all

# Verificar estado do Git:
git status
```

**Resultado Canônico Atual:**
- `status`: `PASS`
- `eligible_for_merge`: `true`
- `tests`: `92 testes determinísticos 100% PASS` (7 Sprint 01 + 85 em `tests/`)
- `kanban`: `Espelho Kanban integro com 148 cards`
- `doc_tree`: `Íntegra, zero arquivos soltos`
- `git`: `nothing to commit, working tree clean` no commit `cef4977`.

---

## 7. A PONTE INBOUND & DECISÃO DE SUSPENSÃO DO PULSO 'V'

- Para contornar a dormência do ChatGPT na web, foi implementada uma extensão Manifest V3 em `bridge/extension` e um servidor em `http://127.0.0.1:8765`.
- **Decisão Atual do Proprietário:** O watchdog e os pulsos automáticos `v` foram **completamente desligados** a pedido de Manoel.
- O controle de ritmo e fluxo está 100% manual e soberano. O novo agente **NÃO DEVE** rearmar daemons ou disparar pulsos `v` sem ordem direta de Manoel.

---

## 8. PONTO ATUAL DE TRABALHO & PRÓXIMA ETAPA

1. **Estado do Roadtrace:** Critérios 1 a 5 estão 100% cumpridos e auditados.
2. **Critério 6 Pendente:** **Homologação Soberana Final do Proprietário**.
3. **Missão da Nova Sessão:** Auxiliar Manoel na organização da nova abordagem de trabalho (seja emitir a homologação soberana da Governança Plena, iniciar novas fatias práticas de produtos ou refinar os Cockpits).
