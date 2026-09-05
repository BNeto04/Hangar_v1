"""
az000_governance.external — Módulo Canônico de Fronteiras Periféricas, Pontes Externas e Gateways Autenticados.
Referência ARCA: R-DOM-002, R-DOM-005, R-DOM-006.
Critérios de Fechamento: "Transportes orientados a eventos comprovados", "Deduplicação e HMAC SHA-256 ativos".
"""

from .models import (
    ExternalChannel,
    ExternalAuthPolicy,
    ExternalEventPayload,
    ExternalTransmissionResult,
)
from .gateway import (
    ExternalBridgeGateway,
    get_global_external_gateway,
)

__all__ = [
    "ExternalChannel",
    "ExternalAuthPolicy",
    "ExternalEventPayload",
    "ExternalTransmissionResult",
    "ExternalBridgeGateway",
    "get_global_external_gateway",
]
