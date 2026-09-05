"""
az000_governance.trace — Módulo Canônico de Trilhas Append-Only, Evidências Criptográficas e Traces N08.
Referência ARCA: R-DOM-002 (FAIL_CLOSED_SYSTEMIC), R-DOM-005 (ROOM_BY_ROOM_ORDER), R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA).
Critérios de Fechamento: "06_TRACE_SCHEMA.md em conformidade", "Hashes SHA-256 verificáveis".
"""

from .models import (
    TraceRecord,
    SHA256_HEX_REGEX,
)
from .engine import (
    CryptographicTraceEngine,
    get_global_trace_engine,
)

__all__ = [
    "TraceRecord",
    "SHA256_HEX_REGEX",
    "CryptographicTraceEngine",
    "get_global_trace_engine",
]
