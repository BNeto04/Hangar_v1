# 🚀 HANGAR V1 — BRIEFING DE TRANSIÇÃO E INSIGHTS PARA A NOVA CONVERSA

Este documento consolida a memória viva, a arquitetura, os aprendizados e o estado factual do **Hangar V1**. Cole este texto no início da sua próxima conversa para carregar instantaneamente todo o contexto operacional, estratégico e técnico sem qualquer perda de alinhamento.

---

## 1. O QUE É O HANGAR V1 & QUEM É QUEM

O **Hangar V1** é a plataforma de governança e engenharia autônoma multiagente da Syntheon ADK. Ele opera sob o modelo rigoroso **Down Plant**, com estrita separação de papéis:

1. **Manoel (O Proprietário Soberano — L0):** Detém autoridade irrevogável e exclusiva sobre escopo, prioridade, publicação, exceções e homologação final (Regra `R-DOM-001`). Nenhuma máquina decide por ele.
2. **Codex / ChatGPT (Planejador Estratégico & Auditor Independente):** Analisa requisitos, decompõe planos em rotas formais, audita evidências e despacha chamadas via GitHub PR #1 bridge. Opera em modo *payload-in / parecer-out*.
3. **Antigravity (Executor Técnico Down Plant — N03):** Detém o monopólio físico exclusivo de mutação de código e execução no terminal. Não amplia escopo, segue ordens canônicas e **nunca se auto-homologa** (Regra `R-DOM-007`).

---

## 2. A ARQUITETURA DA ARCA (OS 11 CÔMODOS CONCLUÍDOS)

O sistema é modelado como uma planta espacial contínua dividida em 11 cômodos (Tiers 1 a 11), todos **100% implementados, testados e comitados na branch main**:

| Tier | Cômodo | Módulo no Repositório | Papel e Invariante Central |
|---|---|---|---|
| **01** | `GOVERNANCE` | `az000_governance/arca/` | 7 Regras Canônicas de Domínio (`R-DOM-001..007`) e invariantes imutáveis. |
| **02** | `WORLD` | `vault/WORLD/Master_World.canvas` | Ontologia global com 17 nós e 24 arestas mapeando os azimutes espaciais. |
| **03** | `PLANT` | `az000_governance/plant/` | Endereçamento formal GPS Down Plant (`TERRENO/COMODO/MODULO/SUBMODULO:PORTA`). |
| **04** | `PORTS` | `az000_governance/ports/` | Registro central de portas tipadas e envelopes canônicos de mensagem. |
| **05** | `CAPABILITIES` | `az000_governance/capabilities/` | Motores de automação (Graphify, Improve, Ponytail, Ruflo e Open Design). |
| **06** | `MACHINES` | `az000_governance/machines/` | FSM determinística e isolamento estrito entre observador e executor. |
| **07** | `INTELLIGENCE` | `az000_governance/intelligence/` | Orquestrador de agentes cognitivos confinados (CHARs N01..N10) com prova anti-alucinação. |
| **08** | `EXTERNAL` | `az000_governance/external/` | Gateway de fronteira com verificação HMAC SHA-256 constant-time e dedupe. |
| **09** | `TRACE` | `az000_governance/trace/` | Motor criptográfico e ledger append-only encadeado por SHA-256. |
| **10** | `COCKPITS` | `az000_governance/cockpits/` | Painéis centrais dos 11 cômodos, telemetria e Teacher Mode. |
| **11** | `PRODUCTS` | `az000_governance/products/` | Compilação de releases canônicas e manifesto com hash raiz. |

---

## 3. OS MOTORES FORMAIS DE POLÍTICA (CEDAR & OPA)

Um dos maiores saltos conceituais do projeto:
- **Insight Crucial:** Jamais tente controlar ferramentas de agentes ou permissões apenas por prompt (`SOUL.md`). O controle de ferramentas deve ser estrutural no `config.yaml` e validado por motores formais de autoridade.
- **Motor Cedar (`az000_governance/policy/cedar_engine.py`):**
  - Implementa controle de acesso RBAC/ABAC com semântica estrita *permit / forbid* e *fail-closed default-deny*.
  - Garante o privilégio supremo do Proprietário, o monopólio de escrita do Executor N03 e o confinamento das Lentes (N04/N05/N06) a zero ferramentas de escrita/terminal.
- **Motor OPA (`az000_governance/policy/opa_engine.py`):**
  - Avaliador de Quality Gates em Rego: só aprova envelopes com consenso entre Verifier e Security, lista de bloqueios rigorosamente vazia e hashes SHA-256 de 64 caracteres válidos.

---

## 4. APRENDIZADOS DA PONTE ASSÍNCRONA & AUTOMAÇÃO

1. **GitHub PR #1 como Barramento Universal:** A comunicação entre ChatGPT (nuvem) e Antigravity (máquina local) estabilizou-se através de envelopes tipados (`CALL` e `RESULT`) postados no PR #1.
2. **O Desafio do Inbound Wake no ChatGPT Web:** Modelos na web não acordam sozinhos após a postagem no GitHub. Desenvolvemos uma **Extensão Manifest V3 local** (`bridge/extension`) conectada a um microservidor de sinalização (`127.0.0.1:8765`), injetando pulsos `v` automaticamente.
3. **Decisão do Proprietário:** O envio contínuo do pulso `v` foi desativado a pedido de Manoel, garantindo que o Proprietário assuma o comando direto e dite o ritmo de trabalho sem automações atropeladas.

---

## 5. O ESTADO DO VAULT NO OBSIDIAN (`vault/GOVERNANCE/`)

Para garantir transparência visual completa, a pasta `vault/GOVERNANCE/` foi estruturada com:
- `Governance.canvas`: Canvas interativo representando graficamente todo o território de governança, regras da ARCA, motores de política, quality gates e roadtrace.
- `INDEX.md`: Dashboard Mestre com links bidirecionais (`[[...]]`), tabelas de status dos 11 cômodos e dossiê probatório.
- Notas dedicadas para cada subdomínio (`ARCA_SPEC_AND_ROOM_ORDER.md`, `CEDAR_AUTHORITY_ENGINE.md`, `OPA_QUALITY_GATES.md`, `OWNER_INTENT_CIRCUIT.md`, `QUALITY_GATES_AND_ENFORCEMENT.md`, `ROADTRACE_CONVERGENCIA.md`).

---

## 6. STATUS FACTUAL NO GIT E ENFORCEMENT DE CI/CD

- **Repositório:** `C:\Users\PICHAU\Hangar_v1`
- **Branch:** `main` (100% sincronizada com `origin/main` no GitHub).
- **Último Commit:** `69c0bb9` — *feat(governance): consolidar documentacao e canvas no Vault e gerar dossie executivo para GPT*.
- **CI/CD Enforcement (`scripts/git_enforcement.py`):** **92 testes determinísticos 100% PASS** (código de saída 0).
- **Kanban Hermes:** 148 cartões sincronizados entre a base SQLite (`kanban.db`) e o espelho Git (`kanban_state.json`): 36 concluídos, 109 arquivados e 3 em revisão para análise do Proprietário.

---

## 7. PONTO DE PARTIDA PARA A NOVA CONVERSA

A infraestrutura técnica do Hangar V1 atingiu sua maturidade plena. Todos os 5 primeiros critérios técnicos do Roadtrace de Governança estão 100% exauridos e auditados.

**O que está em pauta agora sob comando direto de Manoel:**
1. **Homologação Soberana do Hangar V1 (Critério 6):** Avaliar o momento de emitir o despacho soberano de "Governança Plena".
2. **Organização da Abordagem de Trabalho:** Definir os próximos passos de engenharia com calma, passo a passo, definindo se o foco será novos produtos, cockpits visuais ou novas fatias práticas.
