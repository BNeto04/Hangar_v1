"""
az000_governance.machines.fsm — Motor Determinístico de Máquina de Estados Finitos (FSM).
Garante transições puras (EstadoAtual, Evento) -> NovoEstado e invariante FAIL_CLOSED.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple


class MachineState(str, Enum):
    INITIAL = "INITIAL"
    READY = "READY"
    RUNNING = "RUNNING"
    HOLD = "HOLD"
    DONE = "DONE"
    FAILED = "FAILED"


@dataclass(frozen=True)
class StateTransition:
    from_state: str
    event: str
    to_state: str
    guard: Optional[str] = None  # Nome da condição de guarda


class FiniteStateMachine:
    def __init__(self, machine_id: str, initial_state: str = "INITIAL"):
        self.machine_id = machine_id
        self.current_state = initial_state
        self._transitions: Dict[Tuple[str, str], StateTransition] = {}
        self._history: List[Tuple[str, str, str]] = []  # (from, event, to)

    def add_transition(self, from_state: str, event: str, to_state: str, guard: Optional[str] = None) -> None:
        key = (from_state.upper(), event.upper())
        if key in self._transitions:
            raise ValueError(f"Transição duplicada já registrada para {key}")
        self._transitions[key] = StateTransition(
            from_state=from_state.upper(),
            event=event.upper(),
            to_state=to_state.upper(),
            guard=guard
        )

    def trigger(self, event: str, guard_fn: Optional[Callable[[], bool]] = None) -> str:
        """
        Aplica o evento e realiza a transição de estado pura.
        Se o evento for inválido ou a guarda falhar, o sistema rejeita sob a regra FAIL_CLOSED.
        """
        key = (self.current_state.upper(), event.upper())
        if key not in self._transitions:
            # Regra FAIL_CLOSED: evento ilegal trava a máquina em HOLD ou FAILED
            prev_state = self.current_state
            self.current_state = MachineState.HOLD.value
            raise PermissionError(
                f"[FAIL_CLOSED] Evento ilegal '{event}' para o estado atual '{prev_state}'. Máquina travada em HOLD."
            )

        trans = self._transitions[key]

        if guard_fn is not None and not guard_fn():
            prev_state = self.current_state
            self.current_state = MachineState.HOLD.value
            raise PermissionError(
                f"[FAIL_CLOSED] Guarda falhou para transição {trans}. Máquina travada em HOLD."
            )

        # Transição pura bem sucedida
        self._history.append((self.current_state, event.upper(), trans.to_state))
        self.current_state = trans.to_state
        return self.current_state

    def get_history(self) -> List[Tuple[str, str, str]]:
        return list(self._history)
