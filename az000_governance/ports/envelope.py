"""
az000_governance.ports.envelope — Esquema de Envelopes Tipados para Mensagens entre Portas.
Em conformidade com DOCS/03_ADDRESS_SCHEMA.md e ARCA.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional

from az000_governance.plant.addressing import validate_down_plant_address


@dataclass
class TypedPortEnvelope:
    schema: str
    source_id: str
    target: str
    timestamp_iso: str
    payload: Dict[str, Any]
    evidence_refs: List[str] = field(default_factory=list)
    payload_sha256: str = ""

    def __post_init__(self):
        if not self.payload_sha256:
            serialized_payload = json.dumps(self.payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
            self.payload_sha256 = hashlib.sha256(serialized_payload).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def create_port_envelope(
    source_id: str,
    target: str,
    schema: str,
    payload: Dict[str, Any],
    evidence_refs: Optional[List[str]] = None
) -> TypedPortEnvelope:
    if not validate_down_plant_address(source_id):
        raise ValueError(f"source_id invalido para porta Down Plant: '{source_id}'")

    if not validate_down_plant_address(target):
        raise ValueError(f"target invalido para porta Down Plant: '{target}'")

    now = datetime.now(timezone.utc).isoformat()
    return TypedPortEnvelope(
        schema=schema.strip().upper(),
        source_id=source_id.strip(),
        target=target.strip(),
        timestamp_iso=now,
        payload=payload,
        evidence_refs=evidence_refs or []
    )


def validate_port_envelope(data: Dict[str, Any]) -> tuple[bool, str]:
    required_keys = ("schema", "source_id", "target", "timestamp_iso", "payload")
    for rk in required_keys:
        if rk not in data:
            return False, f"Chave obrigatoria ausente: {rk}"

    if not validate_down_plant_address(data["source_id"]):
        return False, f"source_id invalido: {data['source_id']}"

    if not validate_down_plant_address(data["target"]):
        return False, f"target invalido: {data['target']}"

    if not isinstance(data["payload"], dict):
        return False, "payload deve ser um objeto JSON (dict)"

    # Se payload_sha256 fornecido, validar integridade
    if "payload_sha256" in data and data["payload_sha256"]:
        serialized = json.dumps(data["payload"], sort_keys=True, separators=(",", ":")).encode("utf-8")
        actual_hash = hashlib.sha256(serialized).hexdigest()
        if actual_hash != data["payload_sha256"]:
            return False, f"Hash SHA-256 do payload divergente: esperado {data['payload_sha256']}, obtido {actual_hash}"

    return True, "VALID"
