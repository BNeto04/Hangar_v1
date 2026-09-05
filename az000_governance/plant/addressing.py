#!/usr/bin/env python3
"""
addressing.py — Validador e Parser Canônico de Endereçamento GPS Down Plant.
Gramática Normativa: TERRENO / CÔMODO / MÓDULO / SUBMÓDULO : PORTA
Conforme DOCS/03_ADDRESS_SCHEMA.md e ARCA (R-DOM-005).
"""

import re
from dataclasses import dataclass
from typing import Optional

from az000_governance.arca import get_room_order

# Expressão regular canônica de endereçamento Down Plant
# Exemplo: Hangar_v1/AZ000_GOVERNANCA_SOBERANIA/ARCA/DOMAIN_RULES:P-GOV-ARCA-RULES-01
ADDRESS_REGEX = re.compile(
    r"^([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+):([a-zA-Z0-9_-]+)$"
)

@dataclass(frozen=True)
class DownPlantAddress:
    terrain: str
    room: str
    module: str
    submodule: str
    port: str

    def to_canonical_string(self) -> str:
        return f"{self.terrain}/{self.room}/{self.module}/{self.submodule}:{self.port}"

    def is_canonical_room(self) -> bool:
        return is_valid_room(self.room)


def parse_down_plant_address(address_str: str) -> DownPlantAddress:
    """Realiza o parse determinístico de um endereço GPS Down Plant."""
    if not isinstance(address_str, str):
        raise ValueError("O endereço Down Plant deve ser uma string.")
    
    clean_addr = address_str.strip()
    match = ADDRESS_REGEX.match(clean_addr)
    if not match:
        raise ValueError(f"Endereço Down Plant fora da gramática normativa 'TERRENO/COMODO/MODULO/SUBMODULO:PORTA': '{address_str}'")
    
    terrain, room, module, submodule, port = match.groups()
    return DownPlantAddress(
        terrain=terrain,
        room=room,
        module=module,
        submodule=submodule,
        port=port,
    )


def validate_down_plant_address(address_str: str) -> bool:
    """Retorna True se o endereço estiver estritamente em conformidade sintática."""
    try:
        parse_down_plant_address(address_str)
        return True
    except (ValueError, TypeError):
        return False


def is_valid_room(room_name: str) -> bool:
    """Verifica se o cômodo pertence ao catálogo topológico canônico da ARCA."""
    canonical_rooms = {r.room_name.upper() for r in get_room_order()}
    canonical_rooms.add("AZ000_GOVERNANCA_SOBERANIA")  # Alias histórico aceito para GOVERNANCE
    return room_name.upper() in canonical_rooms


def format_down_plant_address(terrain: str, room: str, module: str, submodule: str, port: str) -> str:
    """Constrói uma string de endereço canônico e valida sua sintaxe."""
    addr = DownPlantAddress(terrain, room, module, submodule, port)
    canonical = addr.to_canonical_string()
    if not validate_down_plant_address(canonical):
        raise ValueError(f"Composição de endereço inválida: {canonical}")
    return canonical


if __name__ == "__main__":
    sample = "Hangar_v1/AZ000_GOVERNANCA_SOBERANIA/ARCA/DOMAIN_RULES:P-GOV-ARCA-RULES-01"
    parsed = parse_down_plant_address(sample)
    print(f"Parsed: {parsed}")
    print(f"Canonical: {parsed.to_canonical_string()}")
    print(f"Valid Room: {parsed.is_canonical_room()}")
