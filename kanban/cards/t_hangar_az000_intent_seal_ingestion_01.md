# T-HANGAR-AZ000-INTENT-SEAL-INGESTION-01: Integracao Funcional do Circuito AZ000 Owner Intent na Recepcao da Ponte

- **CARD_ID:** `t_hangar_az000_intent_seal_ingestion_01`
- **STATUS:** `done`
- **PRIORITY:** `1`
- **CREATED_AT:** `1788573984`
- **COMPLETED_AT:** `2026-09-04T23:29:07.797631-03:00`

## Descrição
DP_PROJECT: Hangar_v1
DP_TERRAIN: Hangar_v1
DP_ROOM: AZ000_GOVERNANCA_SOBERANIA
DP_MODULE: OWNER_INTENT
DP_SUBMODULE: SEALED_CONTRACT_EMITTER
DP_PORT: P-OWNER-INTENT-INGEST-01 e P-INTENT-HANDOFF-N01-01
DP_CIRCUIT: CIRCUIT_OWNER_INTENT_TO_PLANNER
DP_ARTIFACT: az000_governance/owner_intent/ingestor.py + bridge/github_webhook_server.py
DP_ACTION: Implementar adaptador deterministico que ingere CALLs textuais da ponte, executa OwnerIntentCircuit, gera SealedIntentContract com SHA-256 e entrega HandoffEnvelope ao Planner N01.
DP_TARGET: Chamadas operacionais da PR #1 recebidas via Webhook ou relay.
DP_IMPACT_DIRECT: Garante o invariante NO_UNSEALED_PASS, vinculando cada CALL recebida a um contrato criptografico imutavel no disco.
DP_IMPACT_INDIRECT: Sem impacto no CronosEdu ou nos CHARs T5.
DP_AXIS_DOCUMENTATION: DOCS/19_AZ000_BRIDGE_INGESTION_SEAL_INTEGRATION.md
DP_AXIS_CODE: az000_governance/owner_intent/ingestor.py
DP_AXIS_TEST: tests/test_az000_bridge_ingestor.py
DP_OUT_OF_SCOPE: Redesign de portas existentes, alteracao de rotas de transporte (webhook/inbound).
DP_ACCEPTANCE:
  1. Ingestao de CALL textual gera OwnerRawIntent, valida como ACCEPT, emite SealedIntentContract com SHA-256 integro e emite HandoffEnvelope.
  2. Chamadas invalidas ou com campos faltantes sofrem bloqueio fail-closed.
  3. Contratos gerados sao persistidos em runtime/sealed_contracts/{contract_id}.json.
  4. Suite de testes unitarios 100% verde e sem regressoes.
DP_ROLLBACK: Reversao do arquivo ingestor.py e purga dos contratos transitórios de teste.


## Metadados Fatuais
```json
{
  "final_state": "DONE",
  "closed_at": "2026-09-04T23:29:07.797631-03:00",
  "room_status": "COMPLETE",
  "closure_evidence": "30/30 unit & regression tests passing; SHA-256 contracts verified; zero gaps."
}
```
