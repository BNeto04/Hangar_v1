"""
az000_governance.capabilities.registry — Registro Canônico e Detector de Ciclos para Motores/Capacidades.
Critério Canônico de Fechamento: "Motores integrados e sem dependências cíclicas".
"""

from typing import Dict, List, Optional
from .models import CapabilityDefinition


class CapabilityRegistry:
    def __init__(self):
        self._capabilities: Dict[str, CapabilityDefinition] = {}

    def register(self, cap: CapabilityDefinition) -> None:
        self._capabilities[cap.capability_id.upper()] = cap
        self._validate_acyclic()

    def get(self, capability_id: str) -> Optional[CapabilityDefinition]:
        return self._capabilities.get(capability_id.upper())

    def list_all(self) -> List[CapabilityDefinition]:
        return list(self._capabilities.values())

    def _validate_acyclic(self) -> None:
        visited = set()
        rec_stack = set()

        def dfs(node_id: str):
            visited.add(node_id)
            rec_stack.add(node_id)

            cap = self._capabilities.get(node_id)
            if cap:
                for dep in cap.dependencies:
                    dep_upper = dep.upper()
                    if dep_upper not in visited:
                        dfs(dep_upper)
                    elif dep_upper in rec_stack:
                        raise ValueError(f"Dependencia ciclica detectada no registro de capacidades: {node_id} -> {dep_upper}")

            rec_stack.remove(node_id)

        for cap_id in self._capabilities:
            if cap_id not in visited:
                dfs(cap_id)


_GLOBAL_REGISTRY: Optional[CapabilityRegistry] = None


def get_global_capability_registry() -> CapabilityRegistry:
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = CapabilityRegistry()
        _GLOBAL_REGISTRY.register(CapabilityDefinition(
            capability_id="GRAPHIFY",
            name="Graphify Knowledge Extractor",
            version="1.0.0",
            description="Extrator deterministico de grafos de conhecimento e auditor de wikilinks.",
            primary_port="Hangar_v1/CAPABILITIES/ENGINES/GRAPHIFY:P-CAP-GRAPHIFY-01",
            dependencies=[]
        ))
        _GLOBAL_REGISTRY.register(CapabilityDefinition(
            capability_id="OPEN_DESIGN",
            name="Open Design Specifications",
            version="1.0.0",
            description="Motor de especificacoes abertas e projecao ontologica de interfaces.",
            primary_port="Hangar_v1/CAPABILITIES/ENGINES/OPEN_DESIGN:P-CAP-OPENDESIGN-01",
            dependencies=["GRAPHIFY"]
        ))
        _GLOBAL_REGISTRY.register(CapabilityDefinition(
            capability_id="PONYTAIL",
            name="Ponytail Document Curator",
            version="1.0.0",
            description="Curadoria e higienizacao deterministica da arvore de documentacao.",
            primary_port="Hangar_v1/CAPABILITIES/ENGINES/PONYTAIL:P-CAP-PONYTAIL-01",
            dependencies=["GRAPHIFY"]
        ))
        _GLOBAL_REGISTRY.register(CapabilityDefinition(
            capability_id="IMPROVE",
            name="Improve Code Refactor",
            version="1.0.0",
            description="Motor de evolucao estrutural e auditoria de debito tecnico.",
            primary_port="Hangar_v1/CAPABILITIES/ENGINES/IMPROVE:P-CAP-IMPROVE-01",
            dependencies=["GRAPHIFY"]
        ))
        _GLOBAL_REGISTRY.register(CapabilityDefinition(
            capability_id="RUFLO",
            name="Ruflo Workflow Orchestrator",
            version="1.0.0",
            description="Orquestrador deterministico de esteiras e transicoes de tarefas.",
            primary_port="Hangar_v1/CAPABILITIES/ENGINES/RUFLO:P-CAP-RUFLO-01",
            dependencies=["IMPROVE", "PONYTAIL"]
        ))
    return _GLOBAL_REGISTRY
