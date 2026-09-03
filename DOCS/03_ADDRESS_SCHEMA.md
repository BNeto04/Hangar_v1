# HANGAR V1 — 03. ADDRESS SCHEMA (ESQUEMA DE ENDEREÇAMENTO)

**VERSÃO:** `1.0.0`  
**DATA:** `2026-09-01`  
**PROJETO:** `Hangar V1 / Colmeia Autônoma`  
**PADRÃO:** `Down Plant Universal Resource Addressing`  
**CAPACIDADES:** `GRAPHIFY`, `OPEN_DESIGN`  

---

## 1. Notação Canônica de Endereçamento GPS Down Plant

Qualquer recurso, artefato, robô ou porta no Hangar V1 possui um endereço determinístico unívoco seguindo a gramática:

$$\text{TERRENO} \mathbin{/} \text{CÔMODO} \mathbin{/} \text{MÓDULO} \mathbin{/} \text{SUBMÓDULO} \mathbin{:} \text{PORTA}$$

Exemplos Canônicos:
- `MOCK-TERRAIN/Hangar/CharPlanner/Core:P-PLAN-01`
- `MOCK-TERRAIN/Hangar/CharTaskDecomposer/Core:P-DECOMPOSE-01`
- `MOCK-TERRAIN/Hangar/CharExecutor/Core:P-EXECUTE-01`
- `MOCK-TERRAIN/Hangar/CharQualityGate/Evaluator:P-QUALITY-GATE-DECISION-01`
- `MOCK-TERRAIN/Hangar/CharObsidian/Vault:P-OBSIDIAN-STATE-01`

---

## 2. Esquema de Envelopes Tipados

Todos os envelopes trocados entre portas devem conter:

```json
{
  "schema": "STRING_UPPERCASE_VERSIONED",
  "source_id": "ADDRESS_CANONICAL_SOURCE",
  "target": "TARGET_RESOURCE_PATH",
  "timestamp_iso": "ISO_8601_UTC",
  "payload": {},
  "evidence_refs": ["SHA256_HEX_DIGESTS"]
}
```

---

## 3. Regras de Resolução de Caminhos

- Caminhos são relativos ao `terrain_root` e sempre normalizados com barras `/` (formato POSIX).
- Proibição absoluta de caracteres de escape, drive letters soltas (`C:`) e path traversal (`../`).
