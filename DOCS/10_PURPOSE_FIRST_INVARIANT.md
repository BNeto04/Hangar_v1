# 10_PURPOSE_FIRST_INVARIANT.md — Invariante Soberano de Propósito Operacional Obrigatório

## 1. Declaração do Invariante Soberano
> **"Nada existente deve ser substituído apenas por conveniência ou estética. Nenhuma ação, arquivo, estrutura, automação, refatoração, reorganização, visual, integração ou ferramenta deve ser criada/alterada sem propósito operacional claro."**
> — *Diretiva Soberana do Proprietário (`CALL-HANGAR-PURPOSE-FIRST-INVARIANT-001` / `CG-000106`)*

---

## 2. Requisitos Mandatórios para Toda Ação Material

Antes de qualquer mutação em código, Planta, Vault, documentação, kanban ou infraestrutura, a proposição técnica deve declarar explicitamente as seguintes **8 Dimensões Operacionais**:

| Dimensão | Pergunta de Validação | Exigência Técnica |
| :--- | :--- | :--- |
| **1. PURPOSE** | Qual problema real resolve? | Justificativa funcional concreta; proibido "melhoria estética". |
| **2. SCOPE** | Onde atua? | Endereço Down Plant estrito (`TERRITÓRIO/CÔMODO/MÓDULO:PORTA`). |
| **3. BENEFICIARY** | Quem/qual fluxo consome? | Agente (CHAR), Máquina (NM) ou consumidor operacional declarado. |
| **4. EXPECTED_RESULT** | Qual o resultado objetivo? | Efeito observável e mensurável no sistema. |
| **5. ACCEPTANCE_CRITERIA**| Como provar o valor? | Critérios objetivos e verificáveis matematicamente. |
| **6. EVIDENCE** | Qual evidência comprova? | Envelope SHA256, trace de execução ou teste automatizado. |
| **7. COST / RISK** | Qual o impacto relevante? | Análise de regressão, carga e consumo de recursos. |
| **8. PRESERVE** | O que não pode ser substituído? | Garantia de não-regressão de capacidades ativas. |

---

## 3. Políticas Fail-Closed de Rejeição Automática

O Quality Gate N07 e os motores de deliberação devem aplicar retenção imediata (`HOLD`) se qualquer uma das seguintes violações for detectada:

1. **`ESTHETIC_ONLY` $	o$ `HOLD`:**
   Alterações de layout, estilo, sintaxe ou organização que não adicionem valor funcional ou operacional.
2. **`DUPLICATE_WITHOUT_NEW_CAPABILITY` $	o$ `HOLD`:**
   Criação de novos arquivos, classes, tabelas ou docs que repitam capacidades já existentes na Planta.
3. **`TOOL_WITHOUT_CLEAR_CONSUMER` $	o$ `HOLD`:**
   Invocação ou adição de ferramentas, automações ou dependências que não possuam consumidor ativo declarado.
4. **`CHANGE_WITHOUT_ACCEPTANCE_CRITERIA` $	o$ `HOLD`:**
   Propostas de mudança que não definam métrica ou teste objetivo de aceitação.

---

## 4. Regra de Substituição de Capacidades Existentes

Uma capacidade, módulo, arquivo ou ferramenta pré-existente **somente pode ser substituída** quando todos os 3 requisitos forem simultaneamente atendidos:
1. **Razão Funcional Explícita:** Demonstração matemática ou funcional da superioridade da nova abordagem.
2. **Evidência de Migração:** Plano e teste de transição comprovando que nenhum dado ou fluxo foi rompido.
3. **Zero Perda de Capacidade:** A capacidade anterior deve ser totalmente suprida ou expandida pela nova.

---

## 5. Relação de Complementaridade da Infraestrutura (Git e Ferramental)
> **"Git complementa Planta, Governança, Documentação, Código, Kanban, CHARs e Máquinas; ele não substitui nenhum deles."**

O Git atua exclusivamente como barramento determinístico, repositório de evidências, versionamento auditável e ponto de enforcement (Quality Gates). Não substitui a verdade topológica expressa na Planta nem a soberania das diretivas do Proprietário.
