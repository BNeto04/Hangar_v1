# CUTOVER_MANIFEST.md — Manifesto de Continuidade e Migração do Hangar V1

## 1. Identificação do Repositório Canônico
- **Repositório Destino:** `BNeto04/Hangar_v1`
- **Repositório de Origem Histórica:** `BNeto04/syntheon_adk` (PR #2)
- **Data do Cutover:** `2026-09-03`
- **Diretiva de Origem:** `CALL-HANGAR-V1-REPO-MIGRATION-001` (Envelope `CG-000102`)

---

## 2. Política de Histórico e Continuidade
- A PR #2 de `BNeto04/syntheon_adk` permanece congelada como evidência histórica auditável (read-only) com 180 comentários históricos (`CG-000001` até `CG-000102` / `AG-RES-000104`).
- A partir deste cutover, todas as novas mensagens, interações, chamadas operacionais e atualizações de estado do Hangar V1 ocorrem exclusivamente no repositório `BNeto04/Hangar_v1` através de sua nova Pull Request permanente de bridge.
- Continuidade estrita da sequência de identificadores (`MESSAGE_ID`, `CALL_ID`, `REPLY_TO`) e deduplicação.

---

## 3. Inventário de Artefatos Migrados
1. `DOCS/`: Especificações arquiteturais `01` a `08`, contratos de curatela e artefatos de visualização de curadoria.
2. `vault/`: As 11 seções top-level canônicas, `Master_World.canvas`, `INDEX.md` mestre e `GOVERNANCE.md`.
3. `az000_governance/`: Pacote funcional de governança e circuito de intenção do proprietário (`contracts.py`, `ports.py`, `circuit.py`).
4. `envelopes/`: Envelopes criptográficos de auditoria e deliberação.
5. `test_hangar_v1_sprint_01.py`: Suíte de testes determinísticos ponta a ponta.
6. `kanban/`: Espelho versionado de 124 cards do Hermes Kanban.
7. `bridge/`: Infraestrutura de relay e automação de autowake adaptada para `BNeto04/Hangar_v1`.

---

## 4. Itens Excluídos (Segregação Estrita de Escopo)
- Artefatos legados do `syntheon_adk` não correlacionados ao Hangar V1.
- Projetos e testes experimentais externos sem dependência operacional comprovada.
