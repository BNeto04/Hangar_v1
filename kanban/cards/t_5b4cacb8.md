# MOCK-PLAN-01-DECOMPOR-ATOMIC-WRITE

- **CARD_ID:** `t_5b4cacb8`
- **STATUS:** `archived`
- **PRIORITY:** `0`
- **CREATED_AT:** `1787532447`
- **COMPLETED_AT:** `null`

## Descrição
# MISSAO DE PLANEJAMENTO: S-ALG-NANOTASK-01 (CHAR-PLANNER-01)

Voce e o CHAR-PLANNER-01 (Orquestrador e Arquiteto de Decomposicao da Colmeia).
Sua missao e decompor a correcao do runtime para execucao de Nano Tasks com operacao atomica estrita (Funcao -> Algoritmo -> Subfuncao -> Passo -> Operacao), SEM implementar nada e SEM ampliar escopo.

## 1. ENTRADAS DO DIAGNOSTICO
- Limitacao comprovada: O profile obsidian dispoe de [file, terminal, todo] e o Hermes atual nao restringe tools por Nano Task individualmente.
- O modelo 3B executou tool calls nativas, mas na passagem de argumentos de write_file confundiu path e content.
- Requisitos:
  1. path e content devem chegar como campos estruturados distintos e validados.
  2. Chamadas administrativas do Hermes (kanban_show, kanban_complete) nao contam como operacao do CHAR.
  3. O CHAR deve ver somente a capability necessaria ao Passo (max_calls: 1).

## 2. SAIDA OBRIGATORIA EXIGIDA NO SUMMARY / RESULTADO:
Produza o plano formal cobrindo estritamente as 10 secoes (A ate J):
A. FUNCAO: ID e objetivo unico da capacidade de escrita atomica.
B. ALGORITMO: Sequencia completa da correcao do runtime ate novo piloto.
C. SUBFUNCOES: Separar descoberta do runtime, definicao da capability, montagem do envelope, despacho, verificacao e rollback.
D. PASSOS: Passos curtos de 1 turno com dependencias, entrada, ensure, evidencia e parada.
E. OPERACOES: 1 capability por passo mutavel, separando administrativo do Hermes vs operacao do CHAR.
F. GPS E ARQUIVOS: Localizacao dos arquivos reais de Hermes/profiles/toolsets com status (leitura, escrita ou PENDENTE).
G. CONTRATO DA CAPABILITY ATOMICA: Schema exato de argumentos, require/ensure/invariants, allowlist, protecoes.
H. GRAFO E MAQUINA DE ESTADOS: Predecessores/sucessores (READY -> EXECUTING -> VERIFYING -> DELIVERED).
I. PLANO DE TESTES: Fixtures descartaveis, casos path/content validos/invalidos, proibicao de tools concorrentes.
J. ESTIMATIVA DE GRANDEZA: Classificacao (F a SS) justificada por risco, tempo, tokens e reversibilidade.

Finalize registrando o plano no kanban_complete. NAO IMPLEMENTE CODIGO.

## Metadados Fatuais
```json
{}
```
