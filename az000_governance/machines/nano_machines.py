"""
az000_governance.machines.nano_machines — Catálogo Canônico de Nano Máquinas Operacionais.
Conectadas a endereços GPS Down Plant e portas tipadas.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional

from az000_governance.capabilities.graphify_engine import GraphifyEngine
from .fsm import FiniteStateMachine, MachineState


@dataclass
class NanoExecutionOutput:
    machine_id: str
    port: str
    status: str
    timestamp_iso: str
    result_data: Dict[str, Any]
    output_sha256: str


class NanoMachine(ABC):
    def __init__(self, machine_id: str, primary_port: str):
        self.machine_id = machine_id
        self.primary_port = primary_port
        self.fsm = FiniteStateMachine(machine_id=machine_id, initial_state="INITIAL")
        self._setup_fsm()

    @abstractmethod
    def _setup_fsm(self) -> None:
        pass

    @abstractmethod
    def execute(self, payload: Dict[str, Any]) -> NanoExecutionOutput:
        pass


class NM_OBS_01_VaultAuditor(NanoMachine):
    """
    Nano Máquina NM-OBS-01: Auditoria determinística e validação de nós do Vault Obsidian.
    Endereço: Hangar_v1/MACHINES/NANO/NM_OBS_01:P-MACH-OBS-AUDIT-01
    """
    def __init__(self):
        super().__init__(
            machine_id="NM-OBS-01",
            primary_port="Hangar_v1/MACHINES/NANO/NM_OBS_01:P-MACH-OBS-AUDIT-01"
        )

    def _setup_fsm(self) -> None:
        self.fsm.add_transition("INITIAL", "INITIALIZE", "READY")
        self.fsm.add_transition("READY", "AUDIT", "RUNNING")
        self.fsm.add_transition("RUNNING", "PASS", "DONE")
        self.fsm.add_transition("RUNNING", "FAIL", "FAILED")
        self.fsm.add_transition("DONE", "RESET", "READY")

    def execute(self, payload: Dict[str, Any]) -> NanoExecutionOutput:
        vault_path = Path(payload.get("vault_path", "vault"))
        if self.fsm.current_state == "INITIAL":
            self.fsm.trigger("INITIALIZE")
        
        self.fsm.trigger("AUDIT")

        engine = GraphifyEngine(vault_path)
        cap_res, metrics = engine.audit_vault_graph()

        if cap_res.status == "SUCCESS":
            self.fsm.trigger("PASS")
            final_status = "SUCCESS"
        else:
            self.fsm.trigger("FAIL")
            final_status = "FAILED"

        now = datetime.now(timezone.utc).isoformat()
        serialized = f"{self.machine_id}|{final_status}|{metrics.get('total_nodes', 0)}|{now}"
        sha = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        return NanoExecutionOutput(
            machine_id=self.machine_id,
            port=self.primary_port,
            status=final_status,
            timestamp_iso=now,
            result_data=metrics,
            output_sha256=sha
        )


class NM_EXEC_01_TaskAutomata(NanoMachine):
    """
    Nano Máquina NM-EXEC-01: Autômato de transições determinísticas de ciclo de vida de tarefas.
    Endereço: Hangar_v1/MACHINES/NANO/NM_EXEC_01:P-MACH-TASK-EXEC-01
    """
    def __init__(self):
        super().__init__(
            machine_id="NM-EXEC-01",
            primary_port="Hangar_v1/MACHINES/NANO/NM_EXEC_01:P-MACH-TASK-EXEC-01"
        )

    def _setup_fsm(self) -> None:
        self.fsm.add_transition("INITIAL", "ENQUEUE", "READY")
        self.fsm.add_transition("READY", "DISPATCH", "RUNNING")
        self.fsm.add_transition("RUNNING", "COMPLETE", "DONE")
        self.fsm.add_transition("RUNNING", "ABORT", "HOLD")
        self.fsm.add_transition("HOLD", "RESUME", "RUNNING")

    def execute(self, payload: Dict[str, Any]) -> NanoExecutionOutput:
        event = payload.get("event", "DISPATCH")
        if self.fsm.current_state == "INITIAL":
            self.fsm.trigger("ENQUEUE")

        new_state = self.fsm.trigger(event)
        now = datetime.now(timezone.utc).isoformat()
        sha = hashlib.sha256(f"{self.machine_id}:{new_state}:{now}".encode("utf-8")).hexdigest()

        return NanoExecutionOutput(
            machine_id=self.machine_id,
            port=self.primary_port,
            status=new_state,
            timestamp_iso=now,
            result_data={"state": new_state, "history": self.fsm.get_history()},
            output_sha256=sha
        )
