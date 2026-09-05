# ⚖️ GOVERNANCE MONOLITH - HANGAR V1

Documento canônico, integral e monolítico de governança soberana, matriz de autoridade, diretrizes de modelagem espacial, princípios fail-closed, contratos de artefatos e homologação de produtos no ecossistema Hangar V1.

---

## 📑 ÍNDICE GERAL DE NAVEGAÇÃO
- [[#1-soberania-do-proprietário--papel-do-codex|1. Soberania do Proprietário & Papel do Codex]]
- [[#2-matriz-de-autoridade--perfis-down-plant|2. Matriz de Autoridade & Perfis Down Plant]]
- [[#3-quality-gates--árbitros-lógicos-fail-closed|3. Quality Gates & Árbitros Lógicos Fail-Closed]]
- [[#4-princípios-estritos-fail-closed|4. Princípios Estritos Fail-Closed]]
- [[#5-sistema-de-auditoria-provas--trilhas-sha-256|5. Sistema de Auditoria, Provas & Trilhas SHA-256]]
- [[#6-políticas-formais--policy-registry|6. Políticas Formais & Policy Registry]]
- [[#7-diretriz-spec_first--no_spec_no_code|7. Diretriz SPEC_FIRST & NO_SPEC_NO_CODE]]
- [[#8-hierarquia-espacial-do-ecossistema|8. Hierarquia Espacial do Ecossistema]]
- [[#9-aprofundamento-progressivo--estados-ontológicos|9. Aprofundamento Progressivo & Estados Ontológicos]]
- [[#10-contrato-mínimo-do-artefato-ativo-10-campos|10. Contrato Mínimo do Artefato Ativo (10 Campos)]]
- [[#11-política-de-frontend--slots-de-design-de-ui|11. Política de Frontend & Slots de Design de UI]]
- [[#12-política-de-conclusão-de-produto--azimutes-obrigatórios|12. Política de Conclusão de Produto & Azimutes Obrigatórios]]
- [[#13-referências-normativas-opa--cedar-enforcement-futuro|13. Referências Normativas OPA & Cedar (Enforcement Futuro)]]
- [[#14-rastreabilidade-bidirecional-doc-script--implementation-gaps|14. Rastreabilidade Bidirecional Doc-Script & Implementation Gaps]]

---

## 1. Soberania do Proprietário & Papel do Codex
- **Autoridade Soberana (L0):** O Proprietário detém a prerrogativa soberana e irrevogável de definir intenção, prioridade, escopo, regras de parada, homologação de fatias, concessão de exceções e autorização de publicação/deploy.
- **Papel do Codex (Auditor & Planejador):** O Codex atua como planejador estratégico e auditor independente. É responsável por decompor tarefas em rotas formais, verificar conformidade com o modelo de mundo e auditar as evidências geradas antes de submeter ao Proprietário.
- **Monopólio de Decisão Humana:** Nenhuma máquina ou agente de SLM pode deliberar sobre publicação final ou aprovação de exceções metodológicas sem decisão explícita do Proprietário.
- **Regra de Mutação Pré-Autorizada:** Nenhuma mutação de código, documentação ou estado de arquivos pode ocorrer sem um CARD previamente registrado e visível no Hermes Kanban.

---

## 2. Matriz de Autoridade & Perfis Down Plant
O ecossistema Hangar V1 adota separação estrita de privilégios e isolamento de contexto (princípio do menor privilégio):

1. **Lentes e Pareceristas (N04 Reviewer, N05 DDD, N06 Security):**
   - Modo de operação: *payload-in / parecer-out*.
   - Ferramentas autorizadas no `config.yaml`: `platform_toolsets.cli: []` (zero ferramentas de terminal ou escrita).
   - Função: Análise pura de evidências e emissão de parecer assinado.
2. **Orquestrador / Planejador (N01 Planner, N02 Coordinator):**
   - Ferramentas autorizadas: `platform_toolsets.cli: [kanban, skills]` (gestão de filas e rotas).
3. **Executor Operacional (N03 Executor / Builder):**
   - Ferramentas autorizadas: `platform_toolsets.cli: [file, terminal]`.
   - Detém o monopólio físico exclusivo de mutação de código e execução de comandos.
4. **Agente Obsidian & Curador (N10 Obsidian, N09 Curator, N08 Verifier):**
   - Ferramentas autorizadas: Leitura estruturada, travessia de grafo Graphify e checagem determinística de evidências no Vault.

---

## 3. Quality Gates & Árbitros Lógicos Fail-Closed
O Quality Gate (N07) atua como árbitro lógico central e agregador determinístico de todas as lentes:

- **Critério de Elegibilidade:** O avanço (`ADVANCE`) só é deliberado se:
  1. O relatório do Verifier (N08) atestar `VERIFICATION_PASSED`.
  2. O relatório de Segurança (N06) atestar `SECURITY_PASS`.
  3. A lista de bloqueios (`blocking_reasons`) for rigorosamente vazia (`count == 0`).
- **Estado HOLD:** Na ausência de qualquer evidência ou divergência factual, o veredito emitido é obrigatoriamente `HOLD` com `eligible_for_promotion = False`.
- **Independência:** O Quality Gate opera sobre provas imutáveis (envelopes tipados), não sobre relatos textuais não verificados.

---

## 4. Princípios Estritos Fail-Closed
- **Princípio da Dúvida Sistemática:** Se uma prova for ambígua, nula, ilegível, corrompida ou inacessível, o sistema deve abortar preventivamente a transição de estado.
- **Proibição de Fallbacks Falsos:** É expressamente vedado criar fallbacks silenciosos, credenciais fictícias ou dados simulados em fluxos reais de execução.
- **Proibição de Ajustes Ocultos:** É vedado alterar suítes de teste ou parâmetros de validação para mascarar defeitos do comportamento real do sistema.
- **Produção Não é Bancada:** Ambientes de produção ou homologação nunca devem ser utilizados para experimentação sem autorização soberana.

---

## 5. Sistema de Auditoria, Provas & Trilhas SHA-256
- **Assinatura Criptográfica:** Todo envelope de despacho (`CALL`), parecer de lente (`REVIEW`), verificação (`VERIFICATION`) e decisão (`QUALITY_GATE`) deve gerar um hash SHA-256 canônico sobre seu payload JSON imutável.
- **Repositório de Envelopes:** Os envelopes são persistidos na pasta canônica `syntheon_adk/hangar_v1/envelopes`.
- **Seção de Traces:** Os registros definitivos são consolidados na seção `hangar_v1/vault/TRACE` em formato append-only.

---

## 6. Políticas Formais & Policy Registry
Catálogo unificado de políticas normativas ativas no Hangar V1:
1. `POL-SOVEREIGN-OWNER-01`: Soberania decisória irrestrita do Proprietário e auditoria do Codex.
2. `POL-CEDAR-AUTH-01`: Monopólio exclusivo de mutação para N03 e confinamento estrito de lentes read-only.
3. `POL-OPA-GATE-01`: Regras de agregação de segurança e verificação factual para deliberação fail-closed.
4. `POL-SPEC-FIRST-01`: Proibição de código sem especificação arquitetural homologada.
5. `POL-SPATIAL-HIERARCHY-01`: Conformidade obrigatória com a hierarquia espacial Hangar->Artefato.
6. `POL-UI-FRONTEND-SLOT-01`: Exigência de slot em FRONTEND antes da implementação de funções de UI.
7. `POL-AZIMUTH-COMPLETION-01`: Conclusão de produtos vinculada ao percurso de azimutes obrigatórios.

8. `POL-ARCA-DOMAIN-RULES-01`: Unicidade e imutabilidade de regras de domínio centralizadas no módulo [[ARCA_DOMAIN_RULES|ARCA]].
9. `POL-ROOM-ORDER-EXECUTION-01`: Execução e fechamento integral de SPECs por cômodo antes do avanço topológico.

---

## 7. Diretriz SPEC_FIRST & NO_SPEC_NO_CODE
- **Regra Fundamental:** *Nenhum código sem especificação; nenhuma mutação física sem documento arquitetural aprovado.*
- **Ciclo Obrigatório:**
  1. `DOCUMENTAR & ESPECIFICAR`: Criar especificação formal no Vault (`DOCS/` ou `vault/`).
  2. `HOMOLOGAR ESPECIFICAÇÃO`: Submeter a especificação às lentes e ao Quality Gate.
  3. `CRIAR CARD NO KANBAN`: Registrar a tarefa vinculada à especificação homologada.
  4. `IMPLEMENTAR CÓDIGO / SCRIPTS`: Somente após o card estar ativo e a spec homologada.

---

## 8. Hierarquia Espacial do Ecossistema
A organização territorial do Hangar V1 segue uma cadeia topológica decrescente rigorosa:

$$	ext{Hangar} \longrightarrow 	ext{Território} \longrightarrow 	ext{Cômodo} \longrightarrow 	ext{Andar / Face} \longrightarrow 	ext{Módulo} \longrightarrow 	ext{Submódulo} \longrightarrow 	ext{Circuito} \longrightarrow 	ext{Porta} \longrightarrow 	ext{Artefato}$$

- **Hangar:** O ecossistema soberano global (`hangar_v1`).
- **Território:** O repositório real ou partição física (`syntheon_adk`).
- **Cômodo:** As seções canônicas de alto nível do Vault (`WORLD`, `PLANT`, `GOVERNANCE`, etc.).
- **Andar / Face:** A dimensão técnica vertical ou face operacional (ex: `L0 Governança`, `L1 Execução`, `L2 Lentes`).
- **Módulo:** O subsistema autônomo delimitado (ex: `Authority`, `Quality_Gates`).
- **Submódulo:** Componente funcional interno ao módulo.
- **Circuito:** Fluxo encadeado de processamento e comunicação assíncrona.
- **Porta:** Interface contratual tipada de entrada ou saída (`P-*`).
- **Artefato:** O arquivo atômico, script, política ou documento concreto.

---

## 9. Aprofundamento Progressivo & Estados Ontológicos
- **Mapeamento Gradual:** É proibido tentar decompor toda a árvore de uma só vez sem necessidade operacional imediata.
- **Estados Ontológicos Formais:**
  * `KNOWN_BUT_NOT_DECOMPOSED`: O nó é reconhecido no modelo de mundo, mas seus submódulos ainda não foram detalhados.
  * `IMPLEMENT_LATER`: O componente está formalmente especificado, mas sua mutação física está agendada para fatias posteriores.
- **Faces Técnicas:** Os andares representam perspectivas analíticas (Engenharia, Segurança, Governança, Grafo) aplicadas sobre o mesmo território.

---

## 10. Contrato Mínimo do Artefato Ativo (10 Campos)
Todo artefato executável, agente, rotina ou máquina ativa deve responder obrigatoriamente a 10 metadados padronizados:

1. **O QUE SOU:** Identidade ontológica, classe e responsabilidade principal.
2. **ONDE ESTOU:** Endereço canônico absoluto e relativo no repositório.
3. **INTENÇÃO:** Propósito de negócio ou diretriz técnica que justifica sua existência.
4. **QUEM ACIONA:** Agentes, usuários ou chamadas upstream autorizados a invocar.
5. **PORTA:** Contrato de interface formal (`P-*`) e formato de payload.
6. **CAMINHO ESPERADO:** Sequência nominal de execução passo a passo.
7. **SUCESSO:** Critério determinístico que atesta a conclusão bem-sucedida.
8. **FALHA:** Condições de erro, exceções mapeadas e comportamento de parada.
9. **RESULTADO:** Formato do envelope ou retorno gerado para o consumidor.
10. **EVIDÊNCIA:** Digest SHA-256, log, teste ou registro auditável que comprova a ação.

---

## 11. Política de Frontend & Slots de Design de UI
- **Exigência de Slot de Design:** Para qualquer funcionalidade que gere impacto de interface do usuário, tela, visualização ou cockpit, é obrigatório definir previamente sua localização em `COCKPITS/` ou `FRONTEND` e seu respectivo slot de design antes de iniciar a codificação de backend.
- **Cadeia Mínima Relevante:** É permitida a implementação parcial da cadeia (ex: backend inicial), desde que a cadeia mínima ponta a ponta (do dado ao slot de UI) esteja explicitamente especificada no modelo.
- **Regra de N/A:** A declaração `FRONTEND = N/A` só é aceita mediante justificativa formal (ex: rotinas exclusivas de infraestrutura ou bridges atômicas sem contato humano).

---

## 12. Política de Conclusão de Produto & Azimutes Obrigatórios
Para que um produto ou fatia atinja o estado `DONE / T5`, ele deve obrigatoriamente percorrer os azimutes canônicos do Master World Canvas aplicáveis à sua classe:

- **Azimutes Canônicos:**
  * `AZ-000° GOVERNANÇA`: Autorização soberana e conformidade com políticas.
  * `AZ-045° GATES`: Deliberação formal fail-closed do Quality Gate.
  * `AZ-090° EXECUÇÃO`: Compilação, testes e mutação física autorizada.
  * `AZ-135° PRODUTOS`: Registro e empacotamento do entregável homologado.
  * `AZ-180° TRACE`: Emissão de digests criptográficos SHA-256 e trilha imutável.
  * `AZ-225° TERRITÓRIO`: Persistência factual e integridade de arquivos no disco.
  * `AZ-315° CONHECIMENTO`: Indexação semântica e conectividade no Grafo Graphify.
- **Declaração de N/A:** Qualquer azimute não percorrido deve possuir justificativa formal aprovada pelo Quality Gate.

---

## 13. Referências Normativas OPA & Cedar (Enforcement Futuro)
- **Cedar Policy Engine:**
  * Alocação: Camada de `AUTHORITY`.
  * Função: Validação estática e declarativa de permissões de agentes (`permit`/`forbid`), garantindo isolamento estrito sem abertura de portas de rede.
- **Open Policy Agent (OPA / Rego):**
  * Alocação: Camada de `QUALITY_GATES`.
  * Função: Avaliação estrutural de envelopes JSON e regras lógicas de agregação de evidências.
- **Diretriz de Não-Instalação Imediata:** Ambos os motores servem como referências normativas e arquiteturais de padrão; a execução atual é intermediada por bridges locais em Python/Rust sem dependência de daemons externos ou pacotes não autorizados.

---

## 14. Rastreabilidade Bidirecional Doc-Script & Implementation Gaps
Mapeamento formal entre as regras de governança e suas implementações no ecossistema:

| Seção Normativa | Regra de Governança | Implementação Real Validada no Disco |
| :--- | :--- | :--- |
| **`1. OWNER DIRECTIVES`** | Registro em Kanban & Despacho | `C:\Users\PICHAU\AppData\Local\hermes\kanban.db`<br>`C:\Users\PICHAU\Downloads\circuito\export_kanban_mirror.py`<br>`C:\Users\PICHAU\.gemini\antigravity\scratch\MOCK-TERRAIN\bridges\char_planner.py`<br>`C:\Users\PICHAU\Downloads\circuito\github_pr_relay.py` |
| **`2. AUTHORITY MATRIX`** | Monopólio N03 & Lentes Read-Only | `C:\Users\PICHAU\.gemini\antigravity\scratch\MOCK-TERRAIN\bridges\char_executor.py`<br>`C:\Users\PICHAU\.gemini\antigravity\scratch\MOCK-TERRAIN\bridges\char_code_reviewer.py`<br>`C:\Users\PICHAU\.gemini\antigravity\scratch\MOCK-TERRAIN\bridges\char_ddd.py`<br>`C:\Users\PICHAU\.gemini\antigravity\scratch\MOCK-TERRAIN\bridges\char_security.py`<br>`C:\Users\PICHAU\.gemini\antigravity\scratch\MOCK-TERRAIN\nanomachines\NM-OBS-READ\nm_obs_read.py`<br>`C:\Users\PICHAU\.gemini\antigravity\scratch\MOCK-TERRAIN\nanomachines\NM-OBS-WRITE\nm_obs_write.py`<br>`C:\Users\PICHAU\.gemini\antigravity\scratch\MOCK-TERRAIN\nanomachines\NM-OBS-PATCH\nm_obs_patch.py` |
| **`3. QUALITY GATES`** | Árbitro Lógico Fail-Closed | `C:\Users\PICHAU\.gemini\antigravity\scratch\MOCK-TERRAIN\bridges\char_quality_gate.py`<br>`C:\Users\PICHAU\syntheon_adk\hangar_v1\test_hangar_v1_sprint_01.py` |
| **`4. FAIL_CLOSED`** | Bloqueio Preventivo Estrito | `C:\Users\PICHAU\.gemini\antigravity\scratch\MOCK-TERRAIN\bridges\char_quality_gate.py`<br>`C:\Users\PICHAU\syntheon_adk\hangar_v1\test_hangar_v1_sprint_01.py` |
| **`5. AUDIT & PROOFS`** | Envelopes e Traces SHA-256 | `C:\Users\PICHAU\.gemini\antigravity\scratch\MOCK-TERRAIN\bridges\char_verifier.py`<br>`C:\Users\PICHAU\syntheon_adk\hangar_v1\envelopes`<br>`C:\Users\PICHAU\syntheon_adk\hangar_v1\vault\TRACE` |
| **`6. POLICY REGISTRY`** | Esquemas JSON Padronizados | `QUALITY-GATE-INPUT-1` em `bridges/char_quality_gate.py`<br>`VERIFICATION-EVIDENCE-1` em `bridges/char_verifier.py`<br>`SECURITY-REVIEW-1` em `bridges/char_security.py` |
| **`7. PRODUCT COMPLETION`** | Homologação Cumulativa T5 | `C:\Users\PICHAU\syntheon_adk\hangar_v1\test_hangar_v1_sprint_01.py`<br>`C:\Users\PICHAU\.gemini\antigravity\scratch\MOCK-TERRAIN\bridges\char_curator.py`<br>`C:\Users\PICHAU\AppData\Local\hermes\kanban.db` |

### ⚠️ Lacunas Reais Mapeadas (IMPLEMENTATION_GAP):
1. **`GAP-01 (Cedar Standalone Engine):`** A avaliação de políticas Cedar é atualmente executada de forma determinística in-process nas bridges; o empacotamento do binário nativo de CLI `cedar-policy` está programado para ciclo futuro de infraestrutura.
2. **`GAP-02 (OPA HTTP Daemon):`** O servidor OPA daemon HTTP está deliberadamente desabilitado localmente em observância ao princípio de isolamento de rede, sendo substituído pela rotina determinística `CharQualityGateAgent`.
3. **`GAP-03 (UI Design Slot Automation):`** A verificação de slots de design em `COCKPITS/` é atualmente realizada via inspeção e validação do Grafo Graphify, com automação completa de validação de layout visual agendada para a Sprint de Cockpits.
