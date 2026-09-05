"""
az000_governance.cockpits.controller — Controlador Central dos Cockpits de Supervisão, Visualização Espacial e Teacher Mode.
Em conformidade com critérios ARCA: "Visualização espacial sem atrito", "Mapeamento de comandos do Proprietário".
"""

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple

from az000_governance.arca import get_room_order
from az000_governance.cockpits.models import (
    CockpitView,
    OwnerCommand,
    RoomSnapshot,
    TeacherModeState,
)
from az000_governance.ports.envelope import TypedPortEnvelope, create_port_envelope


class CockpitController:
    """Controlador de cockpits humanos, Teacher Mode e comando soberano."""

    def __init__(self, owner_secret: str = "hangar_sovereign_owner_key_2026"):
        self.owner_secret = owner_secret
        self.teacher_mode = TeacherModeState()
        self._command_history: List[OwnerCommand] = []

    def render_spatial_view(self, room_statuses: Optional[Dict[str, str]] = None) -> CockpitView:
        """
        Gera snapshot sem atrito da visualização espacial de todos os 11 cômodos da ARCA.
        Critério ARCA: 'Visualização espacial sem atrito'.
        """
        statuses = room_statuses or {}
        rooms = get_room_order()
        snapshots: List[RoomSnapshot] = []

        for r in rooms:
            status = statuses.get(r.room_name, "COMPLETE" if r.tier <= 9 else ("IN_PROGRESS" if r.tier == 10 else "PENDING"))
            primary_port = f"Hangar_v1/{r.room_name}/CONSOLE/DEFAULT:P-{r.room_name[:4]}-01"
            snapshots.append(
                RoomSnapshot(
                    room_id=r.room_id,
                    room_name=r.room_name,
                    tier=r.tier,
                    status=status,
                    primary_port=primary_port,
                )
            )

        now_iso = datetime.now(timezone.utc).isoformat()
        view_id = f"VIEW-SPATIAL-{int(datetime.now(timezone.utc).timestamp())}"
        
        return CockpitView(
            view_id=view_id,
            timestamp_iso=now_iso,
            rooms=snapshots,
            active_agent_count=5,
            trace_ledger_length=len(snapshots),
            system_health="HEALTHY",
        )

    def dispatch_owner_command(self, cmd: OwnerCommand) -> Tuple[bool, str, Optional[TypedPortEnvelope]]:
        """
        Valida autoridade e mapeia comandos soberanos do Proprietário.
        Invariante R-DOM-001 (SOBERANIA_PROPRIETARIO) e R-DOM-002 (FAIL_CLOSED).
        Critério ARCA: 'Mapeamento de comandos do Proprietário'.
        """
        # 1. Verificar soberania do emissor
        if not cmd.is_sovereign():
            return False, "FAIL_CLOSED: R-DOM-001 violada. Emissor nao detem autoridade soberana do Proprietario.", None

        # 2. Verificar autenticidade do token do Proprietário
        if not cmd.auth_token or cmd.auth_token.strip() != self.owner_secret:
            return False, "FAIL_CLOSED: Token de autenticacao do Proprietario ausente ou invalido.", None

        # 3. Comandos válidos suportados
        valid_commands = {"PAUSE_PIPELINE", "RESUME_PIPELINE", "APPROVE_ROOM", "OVERRIDE_STOP_RULE", "AUDIT_INSPECT"}
        if cmd.command_type not in valid_commands:
            return False, f"FAIL_CLOSED: Comando desconhecido '{cmd.command_type}'.", None

        # 4. Envelopar comando como TypedPortEnvelope Down Plant
        envelope = create_port_envelope(
            source_id="Hangar_v1/COCKPITS/CONSOLE/DISPATCH:P-COCKPIT-DISPATCH-01",
            target="Hangar_v1/GOVERNANCE/AUTHORITY/SOVEREIGN:P-GOV-AUTH-01",
            schema="OWNER_COMMAND_V1",
            payload={
                "command_id": cmd.command_id,
                "command_type": cmd.command_type,
                "issuer": cmd.issuer,
                "parameters": cmd.parameters,
                "authorized": True,
            }
        )

        self._command_history.append(cmd)
        return True, f"Comando '{cmd.command_type}' mapeado e despachado com autoridade soberana.", envelope

    def get_teacher_mode(self) -> TeacherModeState:
        return self.teacher_mode

    def set_teacher_mode(self, active: bool, level: str = "FULL_AUDIT") -> TeacherModeState:
        self.teacher_mode.is_active = active
        self.teacher_mode.inspection_level = level
        self.teacher_mode.last_interaction_iso = datetime.now(timezone.utc).isoformat()
        return self.teacher_mode


_GLOBAL_COCKPIT_CONTROLLER: Optional[CockpitController] = None


def get_global_cockpit_controller() -> CockpitController:
    global _GLOBAL_COCKPIT_CONTROLLER
    if _GLOBAL_COCKPIT_CONTROLLER is None:
        _GLOBAL_COCKPIT_CONTROLLER = CockpitController()
    return _GLOBAL_COCKPIT_CONTROLLER
