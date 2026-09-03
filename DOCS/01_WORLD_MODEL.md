# HANGAR V1 — 01. WORLD MODEL (MODELO DE MUNDO)

**VERSÃO:** `1.0.0`  
**DATA:** `2026-09-01`  
**PROJETO:** `Hangar V1 / Colmeia Autônoma`  
**FRAMEWORK:** `Down Plant Architectural Topology`  
**CAPACIDADES INTEGRADAS:** `GRAPHIFY`, `IMPROVE`, `PONYTAIL`, `RUFLO`, `OPEN_DESIGN`  
**REGRA NORMATIVA:** `REUSE_FIRST_BUILD_LAST`  

---

## 1. Ontologia Fundamental do Mundo Operacional

O Hangar V1 modela o ambiente de desenvolvimento de software através de cinco entidades primárias disjuntas:

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                             WORLD MODEL TOPOLOGY                                 │
└──────────────────────────────────────────────────────────────────────────────────┘

 [ TERRITÓRIO / VAULT ] ──► Espaço físico/documental onde habitam arquivos e artefatos.
            ▲
            │ (Lê / Muta)
            ▼
 [ ENTIDADES / CHARs ]  ──► Agentes cognitivos confinados com papéis exclusivos (N01-N10).
            ▲
            │ (Despacha / Executa)
            ▼
 [ PORTAS & ENVELOPES ] ──► Interfaces tipadas e contratos imutáveis de comunicação.
            ▲
            │ (Avalia / Restringe)
            ▼
 [ QUALITY GATES ]      ──► Árbitros lógicos determinísticos e elegibilidade fail-closed.
            ▲
            │ (Comanda / Audita)
            ▼
 [ PROPRIETÁRIO / CODEX]──► Autoridade máxima de intenção, aprovação e homologação final.
```

---

## 2. Separação de Camadas (The 4 Planes)

1. **Plano de Intenção & Governança (L0):** Proprietário e Auditor Independente (Codex).
2. **Plano de Planejamento & Decomposição (L1-L2):** N01 Planner e N02 Task Decomposer.
3. **Plano de Execução & Mutação (L3):** N03 Executor (monopólio exclusivo de I/O em produto).
4. **Plano Factual, Análise & Gates (L4-L10):** Lentes (N04/N05/N06), Quality Gate (N07), Verifier (N08), Curator (N09) e Obsidian/Cartógrafo (N10).

---

## 3. Invariantes do Modelo de Mundo

- **I1 (Confinamento):** Nenhum agente opera fora do seu cômodo/workspace autorizado.
- **I2 (Monopólio de Escrita):** Apenas o N03 Executor grava código em produto.
- **I3 (Determinismo de Gates):** Decisões de Quality Gate dependem estritamente de provas materiais com hash SHA-256 verificável.
- **I4 (Zero Mocks Sob Teste):** A validação de interfaces exige chamadas às APIs públicas reais.
