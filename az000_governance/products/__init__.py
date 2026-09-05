"""
az000_governance.products — Módulo Canônico de Produtos de Software, Releases e Manifestos de Integridade.
Referência ARCA: R-DOM-002 (FAIL_CLOSED), R-DOM-005 (ROOM_BY_ROOM_ORDER), R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA).
Critérios de Fechamento: "Release notes canônicas validadas", "Manifesto de integridade final emitido".
"""

from .models import (
    ProductArtifact,
    CanonicalReleaseNotes,
    ProductIntegrityManifest,
)
from .manager import (
    ProductReleaseManager,
    get_global_product_release_manager,
)

__all__ = [
    "ProductArtifact",
    "CanonicalReleaseNotes",
    "ProductIntegrityManifest",
    "ProductReleaseManager",
    "get_global_product_release_manager",
]
