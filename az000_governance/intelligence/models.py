"""
az000_governance.intelligence.models — Modelos de Dados para Agentes Cognitivos e Raciocínio Estruturado.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import hashlib
import json


@dataclass(frozen=True)
class CognitiveAgentDefinition:
    agent_id: str
    level: str  # N01 a N10
    persona_name: str
    role: str
    primary_port: str  # Endereço Down Plant
    allowed_capabilities: List[str]
    is_active: bool = True


@dataclass
class AgentThoughtChain:
    chain_id: str
    agent_id: str
    premises: List[str]
    deductions: List[str]
    verdict: str  # "APPROVED", "REJECTED", "HOLD"
    anti_hallucination_sha256: str = ""

    def __post_init__(self):
        if not self.anti_hallucination_sha256:
            data = {
                "chain_id": self.chain_id,
                "agent_id": self.agent_id,
                "premises": self.premises,
                "deductions": self.deductions,
                "verdict": self.verdict
            }
            serialized = json.dumps(data, sort_keys=True).encode("utf-8")
            self.anti_hallucination_sha256 = hashlib.sha256(serialized).hexdigest()
