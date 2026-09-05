"""
az000_governance.capabilities.models — Modelos de Dados para Capacidades e Motores.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


@dataclass(frozen=True)
class CapabilityDefinition:
    capability_id: str
    name: str
    version: str
    description: str
    primary_port: str
    dependencies: List[str] = field(default_factory=list)
    is_active: bool = True


@dataclass
class CapabilityExecutionResult:
    capability_id: str
    status: str  # "SUCCESS", "FAILED", "HOLD"
    timestamp_iso: str
    summary: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    evidence_sha256: Optional[str] = None
