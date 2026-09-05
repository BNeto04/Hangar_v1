"""
az000_governance.machines — Módulo Canônico de Autômatos Finitos e Nano Máquinas Operacionais.
Referência ARCA: R-DOM-005, R-DOM-006.
Critérios de Fechamento: "Transições de estado puras", "Tratamento estrito de erros".
"""

from .fsm import FiniteStateMachine, StateTransition, MachineState
from .nano_machines import NanoMachine, NM_OBS_01_VaultAuditor, NM_EXEC_01_TaskAutomata

__all__ = [
    "FiniteStateMachine",
    "StateTransition",
    "MachineState",
    "NanoMachine",
    "NM_OBS_01_VaultAuditor",
    "NM_EXEC_01_TaskAutomata",
]
