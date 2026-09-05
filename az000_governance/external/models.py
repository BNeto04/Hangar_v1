"""
az000_governance.external.models — Modelos canônicos de integração externa, fronteiras periféricas e autenticação.
Referência ARCA: R-DOM-002 (FAIL_CLOSED_SYSTEMIC), R-DOM-005 (ROOM_BY_ROOM_ORDER), R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ExternalChannel(str, Enum):
    GITHUB_WEBHOOK = "GITHUB_WEBHOOK"
    GITHUB_PR_RELAY = "GITHUB_PR_RELAY"
    TELEGRAM_BOT = "TELEGRAM_BOT"
    CLOUDFLARE_TUNNEL = "CLOUDFLARE_TUNNEL"
    BROWSER_BRIDGE = "BROWSER_BRIDGE"


@dataclass(frozen=True)
class ExternalAuthPolicy:
    channel: ExternalChannel
    auth_scheme: str = "HMAC_SHA256"
    secret: str = ""
    require_signature: bool = True
    max_age_seconds: int = 300


@dataclass
class ExternalEventPayload:
    event_id: str
    channel: ExternalChannel
    timestamp_iso: str
    source: str
    signature: str
    body: Dict[str, Any]
    raw_bytes: Optional[bytes] = None


@dataclass(frozen=True)
class ExternalTransmissionResult:
    event_id: str
    channel: ExternalChannel
    accepted: bool
    reason: str
    event_hash: str
    deduplicated: bool = False
    envelope_ref: Optional[str] = None
