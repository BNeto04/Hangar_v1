"""
Contratos tipados e imutáveis para o circuito de Intenção do Proprietário (AZ000).
"""
import hashlib
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class OwnerRawIntent:
    call_id: str
    owner_id: str
    action: str
    scope: str
    directives: List[str]
    mode: str = "LOCAL_CHAR_SLM_ONLY; ANTIGRAVITY_OBSERVE_ONLY"
    route: str = "N01>N02>HERMES>N03>N10>N09>N08>N07"
    raw_payload: Optional[Dict[str, Any]] = None


@dataclass(frozen=True)
class IntentValidationResult:
    is_valid: bool
    verdict: str  # ACCEPT, HOLD_INCONCLUSIVE, REJECT_UNAUTHORIZED, REJECT_INVALID_SCHEMA
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    blocking_reasons: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class SealedIntentContract:
    schema: str
    contract_id: str
    call_id: str
    owner_id: str
    action: str
    scope: str
    directives: List[str]
    mode: str
    route: str
    created_at_iso: str
    contract_sha256: str
    validation_verdict: str

    def verify_integrity(self) -> bool:
        """Verifica se o hash SHA256 do contrato corresponde exatamente ao seu conteúdo."""
        data_to_hash = {
            "schema": self.schema,
            "contract_id": self.contract_id,
            "call_id": self.call_id,
            "owner_id": self.owner_id,
            "action": self.action,
            "scope": self.scope,
            "directives": self.directives,
            "mode": self.mode,
            "route": self.route,
            "created_at_iso": self.created_at_iso,
            "validation_verdict": self.validation_verdict,
        }
        serialized = json.dumps(data_to_hash, sort_keys=True)
        computed_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        return computed_hash == self.contract_sha256


@dataclass(frozen=True)
class HandoffEnvelope:
    schema: str
    source_port: str
    target_port: str
    timestamp_iso: str
    sealed_contract: SealedIntentContract
    handoff_sha256: str
