"""
az000_governance.ports.registry — Registro Determinístico e Roteador de Portas Down Plant.
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional
from az000_governance.plant.addressing import parse_down_plant_address, DownPlantAddress
from .envelope import TypedPortEnvelope, validate_port_envelope


@dataclass
class PortDefinition:
    port_id: str
    address_str: str
    address: DownPlantAddress
    direction: str  # 'IN', 'OUT', 'INOUT'
    description: str
    allowed_schemas: List[str]


class PortRegistry:
    def __init__(self):
        self._ports: Dict[str, PortDefinition] = {}
        self._listeners: Dict[str, List[Callable[[TypedPortEnvelope], None]]] = {}
        self._dispatch_history: List[TypedPortEnvelope] = []

    def register_port(
        self,
        address_str: str,
        direction: str = "INOUT",
        description: str = "",
        allowed_schemas: Optional[List[str]] = None
    ) -> PortDefinition:
        addr = parse_down_plant_address(address_str)
        port_id = addr.port
        if not port_id:
            raise ValueError(f"Endereco '{address_str}' nao contem identificador de porta (:PORTA).")

        normalized_dir = direction.upper()
        if normalized_dir not in ("IN", "OUT", "INOUT"):
            raise ValueError(f"Direcao de porta invalida: '{direction}'. Esperado: IN, OUT ou INOUT.")

        defn = PortDefinition(
            port_id=port_id,
            address_str=address_str,
            address=addr,
            direction=normalized_dir,
            description=description,
            allowed_schemas=[s.upper() for s in (allowed_schemas or ["*"])]
        )
        self._ports[address_str] = defn
        return defn

    def get_port(self, address_str: str) -> Optional[PortDefinition]:
        return self._ports.get(address_str)

    def list_ports(self) -> List[PortDefinition]:
        return list(self._ports.values())

    def subscribe(self, address_str: str, callback: Callable[[TypedPortEnvelope], None]):
        if address_str not in self._ports:
            raise KeyError(f"Porta '{address_str}' nao registrada.")
        if address_str not in self._listeners:
            self._listeners[address_str] = []
        self._listeners[address_str].append(callback)

    def dispatch(self, envelope: TypedPortEnvelope) -> bool:
        valid, msg = validate_port_envelope(envelope.to_dict())
        if not valid:
            raise ValueError(f"Envelope invalido rejeitado pelo roteador de portas: {msg}")

        target_port = self.get_port(envelope.target)
        if not target_port:
            raise KeyError(f"Porta de destino nao encontrada no registro: {envelope.target}")

        if target_port.direction == "OUT":
            raise PermissionError(f"Porta de destino '{envelope.target}' e somente OUT (nao aceita mensagens de entrada).")

        if "*" not in target_port.allowed_schemas and envelope.schema not in target_port.allowed_schemas:
            raise ValueError(f"Schema '{envelope.schema}' nao permitido na porta '{envelope.target}'. Permitidos: {target_port.allowed_schemas}")

        # Entregar aos assinantes
        listeners = self._listeners.get(envelope.target, [])
        for cb in listeners:
            cb(envelope)

        self._dispatch_history.append(envelope)
        return True

    def get_history(self) -> List[TypedPortEnvelope]:
        return list(self._dispatch_history)


_GLOBAL_REGISTRY: Optional[PortRegistry] = None

def get_global_port_registry() -> PortRegistry:
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = PortRegistry()
    return _GLOBAL_REGISTRY
