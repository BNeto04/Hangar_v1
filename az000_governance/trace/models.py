"""
az000_governance.trace.models — Modelos canônicos de traces imutáveis e evidências criptográficas.
Referência ARCA: R-DOM-002 (FAIL_CLOSED_SYSTEMIC), R-DOM-005 (ROOM_BY_ROOM_ORDER), R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA).
Conforme: DOCS/06_TRACE_SCHEMA.md.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import hashlib
import json
import re
from typing import Any, Dict, List, Optional


SHA256_HEX_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")


@dataclass
class TraceRecord:
    trace_id: str
    call_id: str
    card_id: str
    timestamp_iso: str
    route_taken: str
    actors: Dict[str, Any]
    evidence_digests: Dict[str, str]
    overall_verdict: str
    parent_trace_hash: str = ""
    trace_sha256: str = ""

    def compute_hash(self) -> str:
        data = {
            "trace_id": self.trace_id,
            "call_id": self.call_id,
            "card_id": self.card_id,
            "timestamp_iso": self.timestamp_iso,
            "route_taken": self.route_taken,
            "actors": self.actors,
            "evidence_digests": self.evidence_digests,
            "overall_verdict": self.overall_verdict,
            "parent_trace_hash": self.parent_trace_hash,
        }
        serialized = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    def seal(self) -> "TraceRecord":
        if not self.trace_sha256:
            self.trace_sha256 = self.compute_hash()
        return self

    def verify_integrity(self) -> bool:
        if not self.trace_sha256:
            return False
        return self.trace_sha256 == self.compute_hash()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
