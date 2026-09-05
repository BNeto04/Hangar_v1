"""
az000_governance.cockpits.models — Modelos canônicos de visualização espacial, Teacher Mode e comandos soberanos.
Referência ARCA: R-DOM-001 (SOBERANIA_PROPRIETARIO), R-DOM-002 (FAIL_CLOSED_SYSTEMIC), R-DOM-005 (ROOM_BY_ROOM_ORDER), R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA).
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class RoomSnapshot:
    room_id: str
    room_name: str
    tier: int
    status: str  # COMPLETE, IN_PROGRESS, PENDING
    primary_port: str


@dataclass
class CockpitView:
    view_id: str
    timestamp_iso: str
    rooms: List[RoomSnapshot]
    active_agent_count: int
    trace_ledger_length: int
    system_health: str  # HEALTHY, DEGRADED, CRITICAL

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass(frozen=True)
class OwnerCommand:
    command_id: str
    command_type: str  # PAUSE_PIPELINE, RESUME_PIPELINE, APPROVE_ROOM, OVERRIDE_STOP_RULE, AUDIT_INSPECT
    issuer: str  # Deve ser 'PROPRIETARIO' ou 'OWNER' para conformidade com R-DOM-001
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp_iso: str = ""
    auth_token: str = ""

    def is_sovereign(self) -> bool:
        return self.issuer.strip().upper() in ("PROPRIETARIO", "OWNER")


@dataclass
class TeacherModeState:
    is_active: bool = True
    inspection_level: str = "FULL_AUDIT"  # SUMMARY, DETAIL, FULL_AUDIT
    telemetry_stream: str = "hangar://cockpits/telemetry/live"
    last_interaction_iso: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
