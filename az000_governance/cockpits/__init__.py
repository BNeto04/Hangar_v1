"""
az000_governance.cockpits — Módulo Canônico de Cockpits de Supervisão, Painéis Espaciais e Teacher Mode.
Referência ARCA: R-DOM-001 (SOBERANIA_PROPRIETARIO), R-DOM-002 (FAIL_CLOSED), R-DOM-005 (ROOM_BY_ROOM_ORDER), R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA).
Critérios de Fechamento: "Visualização espacial sem atrito", "Mapeamento de comandos do Proprietário".
"""

from .models import (
    RoomSnapshot,
    CockpitView,
    OwnerCommand,
    TeacherModeState,
)
from .controller import (
    CockpitController,
    get_global_cockpit_controller,
)

__all__ = [
    "RoomSnapshot",
    "CockpitView",
    "OwnerCommand",
    "TeacherModeState",
    "CockpitController",
    "get_global_cockpit_controller",
]
