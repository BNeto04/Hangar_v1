"""
az000_governance.ports — Sistema Canônico de Portas, Contratos e Envelopes Tipados.
Referência ARCA: R-DOM-005 (ROOM_BY_ROOM_ORDER), R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA).
"""

from .envelope import TypedPortEnvelope, create_port_envelope, validate_port_envelope
from .registry import PortDefinition, PortRegistry, get_global_port_registry

__all__ = [
    "TypedPortEnvelope",
    "create_port_envelope",
    "validate_port_envelope",
    "PortDefinition",
    "PortRegistry",
    "get_global_port_registry",
]
