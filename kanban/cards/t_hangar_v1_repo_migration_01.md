# T-HANGAR-V1-REPO-MIGRATION-01: Migração do Repositório Canônico para BNeto04/Hangar_v1

- **CARD_ID:** `t_hangar_v1_repo_migration_01`
- **STATUS:** `review`
- **PRIORITY:** `1`
- **CREATED_AT:** `1788424894`
- **COMPLETED_AT:** `null`

## Descrição
Migração de todo o ecossistema canônico do Hangar para o repositório dedicado BNeto04/Hangar_v1:
- Criação e inicialização do repo BNeto04/Hangar_v1.
- Migração de DOCS/, vault/, az000_governance/, envelopes/, test_hangar_v1_sprint_01.py.
- Migração do espelho Kanban (kanban/kanban_state.json).
- Criação de CUTOVER_MANIFEST.md referenciando syntheon_adk PR #2 como histórico read-only.
- Criação da branch permanente bridge-chatgpt-antigravity e da nova PR de mensagens.
- Atualização do relay local para operar sobre o novo repositório.
- Rota: N01 > N02 > Hermes > N03 > N09 > N08 > N07.

## Metadados Fatuais
```json
{
  "card_id": "t_hangar_v1_repo_migration_01",
  "call_id": "CALL-HANGAR-V1-REPO-MIGRATION-001",
  "target": "BNeto04/Hangar_v1",
  "workspace_kind": "Hangar_v1",
  "status": "REPO_MIGRATED_CANONICAL_ESTABLISHED",
  "trust_level": "T4",
  "quality_gate_status": "QUALITY_GATE_PASS",
  "recommendation": "ADVANCE",
  "eligible_for_promotion": true,
  "verifier_sha256": "5ad24f948a611cb55941d41236e9f943db7aab78493b21c975516a306f3a869d",
  "security_sha256": "667ed6d51315e1de4d993561bb0f004582d72f7c1c302a3d0022fdd4a72cf2d3",
  "canonical_repo": "BNeto04/Hangar_v1",
  "bridge_branch": "bridge-chatgpt-antigravity",
  "new_pr_number": 1,
  "tests_passed": "7/7 OK (1.963s)"
}
```
