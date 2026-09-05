"""
Módulo ARCA (AZ000_GOVERNANCA_SOBERANIA / ARCA).
Repositório Canônico e Somente-Leitura de Regras de Domínio e Ordem de Cômodos do Hangar V1.
"""
from .canonical_domain_rules import (
    ARCA_SCHEMA_VERSION,
    ARCA_DOMAIN_RULES,
    ROOM_EXECUTION_ORDER,
    DomainRule,
    RoomDefinition,
    get_domain_rules,
    get_rule_by_id,
    get_room_order,
    get_room_dependencies,
    verify_arca_integrity,
    compute_arca_sha256,
)

__all__ = [
    "ARCA_SCHEMA_VERSION",
    "ARCA_DOMAIN_RULES",
    "ROOM_EXECUTION_ORDER",
    "DomainRule",
    "RoomDefinition",
    "get_domain_rules",
    "get_rule_by_id",
    "get_room_order",
    "get_room_dependencies",
    "verify_arca_integrity",
    "compute_arca_sha256",
]
