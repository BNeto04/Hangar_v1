"""
az000_governance.capabilities — Módulo de Capacidades Estruturais e Motores do Hangar V1.
Referência ARCA: R-DOM-005, R-DOM-006.
"""

from .models import CapabilityDefinition, CapabilityExecutionResult
from .registry import CapabilityRegistry, get_global_capability_registry
from .graphify_engine import GraphifyEngine

__all__ = [
    "CapabilityDefinition",
    "CapabilityExecutionResult",
    "CapabilityRegistry",
    "get_global_capability_registry",
    "GraphifyEngine",
]
