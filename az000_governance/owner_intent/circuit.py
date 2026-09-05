"""
Circuito Funcional: CIRCUIT_OWNER_INTENT_TO_PLANNER (AZ000 / OWNER_INTENT)
Executa a esteira determinística de normalização, validação, selagem e handoff.
"""
import hashlib
import json
import time
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from .contracts import (
    HandoffEnvelope,
    IntentValidationResult,
    OwnerRawIntent,
    SealedIntentContract,
)
from .ports import (
    PORT_INTENT_HANDOFF_N01,
    PORT_PLANNER_N01_RECEIVE,
)
from ..arca.canonical_domain_rules import ARCA_SCHEMA_VERSION, get_rule_by_id

# Referências Canônicas ao Módulo ARCA (R-DOM-006: SINGLE_SOURCE_OF_TRUTH_ARCA)
ARCA_RULES_REF = {
    "sovereignty": "R-DOM-001",
    "fail_closed": "R-DOM-002",
    "no_unsealed_pass": "R-DOM-003",
}

# Constantes e Políticas de Soberania (Fundamentadas na ARCA)
ALLOWED_OWNERS = {"OWNER", "CHATGPT", "PROPRIETARIO"}
AUTHORIZED_SCOPES_PREFIXES = ["hangar_v1", "AZ000", "syntheon_adk"]
AMBIGUOUS_KEYWORDS = ["talvez", "se possível", "opcionalmente", "quem sabe", "pode ser"]


class OwnerIntentCircuit:
    """Circuito determinístico e fail-closed de ingestão e selagem de intenções do Proprietário."""

    @classmethod
    def normalize_intent(cls, raw_data: Dict[str, Any]) -> Tuple[Optional[OwnerRawIntent], Optional[IntentValidationResult]]:
        """Porta P-INTENT-NORMALIZATION-01: Normaliza dados brutos em objeto tipado."""
        if not isinstance(raw_data, dict):
            return None, IntentValidationResult(
                is_valid=False,
                verdict="REJECT_INVALID_SCHEMA",
                error_code="INVALID_PAYLOAD_TYPE",
                error_message="O payload da intenção deve ser um dicionário JSON válido.",
                blocking_reasons=["Payload não é dicionário."],
            )

        call_id = raw_data.get("call_id") or raw_data.get("CALL_ID")
        owner_id = raw_data.get("owner_id") or raw_data.get("FROM") or raw_data.get("owner")
        action = raw_data.get("action") or raw_data.get("ACTION")
        scope = raw_data.get("scope") or raw_data.get("SCOPE")
        directives = raw_data.get("directives") or raw_data.get("RULES") or []
        if isinstance(directives, str):
            directives = [d.strip() for d in directives.split("\n") if d.strip()]

        if not call_id or not action or not scope:
            return None, IntentValidationResult(
                is_valid=False,
                verdict="REJECT_INVALID_SCHEMA",
                error_code="MISSING_CRITICAL_FIELDS",
                error_message="Campos críticos obrigatórios (call_id, action, scope) ausentes.",
                blocking_reasons=[f"call_id={bool(call_id)}", f"action={bool(action)}", f"scope={bool(scope)}"],
            )

        intent = OwnerRawIntent(
            call_id=str(call_id),
            owner_id=str(owner_id or "OWNER").upper(),
            action=str(action),
            scope=str(scope),
            directives=directives,
            mode=raw_data.get("mode", "LOCAL_CHAR_SLM_ONLY; ANTIGRAVITY_OBSERVE_ONLY"),
            route=raw_data.get("route", "N01>N02>HERMES>N03>N10>N09>N08>N07"),
            raw_payload=raw_data,
        )
        return intent, None

    @classmethod
    def validate_intent(cls, intent: OwnerRawIntent) -> IntentValidationResult:
        """Porta P-INTENT-VALIDATION-01: Validação determinística de autoridade, escopo e clareza."""
        # 1. Validação de Autoridade do Dono
        if intent.owner_id not in ALLOWED_OWNERS:
            return IntentValidationResult(
                is_valid=False,
                verdict="REJECT_UNAUTHORIZED",
                error_code="UNAUTHORIZED_OWNER",
                error_message=f"Emissor '{intent.owner_id}' não possui autoridade soberana no Hangar V1.",
                blocking_reasons=[f"Owner '{intent.owner_id}' fora da lista autorizada: {sorted(ALLOWED_OWNERS)}"],
            )

        # 2. Validação de Escopo Físico
        scope_normalized = intent.scope.replace("\\", "/")
        scope_lower = scope_normalized.lower()
        if not any(scope_lower.startswith(p.lower()) or p.lower() in scope_lower for p in AUTHORIZED_SCOPES_PREFIXES):
            return IntentValidationResult(
                is_valid=False,
                verdict="REJECT_UNAUTHORIZED",
                error_code="OUT_OF_BOUNDS_SCOPE",
                error_message=f"Escopo '{intent.scope}' fora dos limites do Hangar V1 / AZ000.",
                blocking_reasons=[f"Escopo '{intent.scope}' não corresponde aos prefixos autorizados: {AUTHORIZED_SCOPES_PREFIXES}"],
            )

        # 3. Detecção de Ambiguidade (Fail-Closed => HOLD)
        full_text = f"{intent.action} {' '.join(intent.directives)}".lower()
        for kw in AMBIGUOUS_KEYWORDS:
            if kw in full_text:
                return IntentValidationResult(
                    is_valid=False,
                    verdict="HOLD_INCONCLUSIVE",
                    error_code="AMBIGUOUS_DIRECTIVE",
                    error_message=f"Diretiva contém termo ambíguo proibido: '{kw}'.",
                    blocking_reasons=[f"Termo ambíguo detectado: '{kw}'. Requer esclarecimento prévio."],
                )

        return IntentValidationResult(
            is_valid=True,
            verdict="ACCEPT",
            error_code=None,
            error_message=None,
            blocking_reasons=[],
        )

    @classmethod
    def seal_contract(cls, intent: OwnerRawIntent, validation: IntentValidationResult) -> Tuple[Optional[SealedIntentContract], Optional[str]]:
        """Porta P-INTENT-SEAL-01: Selagem criptográfica e carimbo de imutabilidade."""
        if not validation.is_valid or validation.verdict != "ACCEPT":
            return None, f"Impossível selar contrato inválido ou bloqueado (veredicto={validation.verdict})."

        now_iso = datetime.now(timezone.utc).isoformat()
        contract_id = f"CONTRACT-{intent.call_id}-{hashlib.sha256(intent.call_id.encode()).hexdigest()[:8].upper()}"

        data_to_hash = {
            "schema": "AZ000-OWNER-INTENT-SEALED-CONTRACT-1",
            "contract_id": contract_id,
            "call_id": intent.call_id,
            "owner_id": intent.owner_id,
            "action": intent.action,
            "scope": intent.scope,
            "directives": intent.directives,
            "mode": intent.mode,
            "route": intent.route,
            "created_at_iso": now_iso,
            "validation_verdict": validation.verdict,
        }
        serialized = json.dumps(data_to_hash, sort_keys=True)
        contract_sha256 = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        sealed = SealedIntentContract(
            schema="AZ000-OWNER-INTENT-SEALED-CONTRACT-1",
            contract_id=contract_id,
            call_id=intent.call_id,
            owner_id=intent.owner_id,
            action=intent.action,
            scope=intent.scope,
            directives=intent.directives,
            mode=intent.mode,
            route=intent.route,
            created_at_iso=now_iso,
            contract_sha256=contract_sha256,
            validation_verdict=validation.verdict,
        )
        return sealed, None

    @classmethod
    def handoff_to_planner_n01(cls, sealed_contract: SealedIntentContract) -> Tuple[Optional[HandoffEnvelope], Optional[str]]:
        """Porta P-INTENT-HANDOFF-N01-01: Realiza o handoff seguro e verificado para o Planner N01."""
        if not sealed_contract.verify_integrity():
            return None, "FALHA DE SEGURANÇA: Contrato adulterado ou com hash corrompido. Handoff rejeitado."

        now_iso = datetime.now(timezone.utc).isoformat()
        handoff_data = {
            "source_port": PORT_INTENT_HANDOFF_N01,
            "target_port": PORT_PLANNER_N01_RECEIVE,
            "contract_sha256": sealed_contract.contract_sha256,
            "timestamp_iso": now_iso,
        }
        handoff_sha = hashlib.sha256(json.dumps(handoff_data, sort_keys=True).encode("utf-8")).hexdigest()

        envelope = HandoffEnvelope(
            schema="AZ000-INTENT-TO-PLANNER-HANDOFF-1",
            source_port=PORT_INTENT_HANDOFF_N01,
            target_port=PORT_PLANNER_N01_RECEIVE,
            timestamp_iso=now_iso,
            sealed_contract=sealed_contract,
            handoff_sha256=handoff_sha,
        )
        return envelope, None

    @classmethod
    def execute_full_pipeline(cls, raw_intent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a esteira completa do circuito end-to-end com auditoria fail-closed."""
        # 1. Normalização
        intent, norm_err = cls.normalize_intent(raw_intent_data)
        if norm_err:
            return {
                "status": "FAILED",
                "stage": "NORMALIZATION",
                "validation": asdict(norm_err),
                "sealed_contract": None,
                "handoff_envelope": None,
            }

        # 2. Validação
        val_res = cls.validate_intent(intent)
        if not val_res.is_valid:
            return {
                "status": "BLOCKED",
                "stage": "VALIDATION",
                "validation": asdict(val_res),
                "sealed_contract": None,
                "handoff_envelope": None,
            }

        # 3. Selagem
        sealed_contract, seal_err = cls.seal_contract(intent, val_res)
        if seal_err:
            return {
                "status": "FAILED",
                "stage": "SEAL",
                "error": seal_err,
                "validation": asdict(val_res),
                "sealed_contract": None,
                "handoff_envelope": None,
            }

        # 4. Handoff
        envelope, handoff_err = cls.handoff_to_planner_n01(sealed_contract)
        if handoff_err:
            return {
                "status": "FAILED",
                "stage": "HANDOFF",
                "error": handoff_err,
                "validation": asdict(val_res),
                "sealed_contract": asdict(sealed_contract),
                "handoff_envelope": None,
            }

        return {
            "status": "SUCCESS",
            "stage": "HANDOFF_COMPLETED",
            "validation": asdict(val_res),
            "sealed_contract": asdict(sealed_contract),
            "handoff_envelope": asdict(envelope),
        }
