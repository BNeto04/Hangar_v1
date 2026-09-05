"""
az000_governance.intelligence — Módulo Canônico de Inteligência, Agentes Cognitivos e Raciocínio Estruturado.
Referência ARCA: R-DOM-005, R-DOM-006.
Critérios de Fechamento: "Orquestrador de agentes tipado", "Raciocínio estruturado sem alucinação".
"""

from .models import CognitiveAgentDefinition, AgentThoughtChain
from .orchestrator import TypedAgentOrchestrator, get_global_agent_orchestrator

__all__ = [
    "CognitiveAgentDefinition",
    "AgentThoughtChain",
    "TypedAgentOrchestrator",
    "get_global_agent_orchestrator",
]
