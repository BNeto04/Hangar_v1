"""
az000_governance.intelligence.orchestrator — Orquestrador Tipado de Agentes Cognitivos.
Garante raciocínio estruturado sem alucinação e conformidade com a ARCA.
"""

from typing import Dict, List, Optional, Set
from .models import CognitiveAgentDefinition, AgentThoughtChain


class TypedAgentOrchestrator:
    def __init__(self):
        self._agents: Dict[str, CognitiveAgentDefinition] = {}
        self._execution_history: List[AgentThoughtChain] = []

    def register_agent(self, agent: CognitiveAgentDefinition) -> None:
        key = agent.agent_id.upper()
        if key in self._agents:
            raise ValueError(f"Agente cognitivo duplicado: {key}")
        self._agents[key] = agent

    def get_agent(self, agent_id: str) -> Optional[CognitiveAgentDefinition]:
        return self._agents.get(agent_id.upper())

    def list_agents(self) -> List[CognitiveAgentDefinition]:
        return list(self._agents.values())

    def verify_and_record_thought_chain(
        self,
        chain: AgentThoughtChain,
        known_facts: Set[str]
    ) -> bool:
        """
        Valida que o raciocínio estruturado do agente é estritamente ancorado em premissas factuais comprovadas.
        Se qualquer premissa citada não constar em 'known_facts', rejeita sob FAIL_CLOSED (alucinação detectada).
        """
        if chain.agent_id.upper() not in self._agents:
            raise KeyError(f"Agente cognitivo '{chain.agent_id}' não registrado no orquestrador.")

        for premise in chain.premises:
            if premise not in known_facts:
                chain.verdict = "HOLD"
                raise ValueError(
                    f"[ANTI_ALUCINACAO] Premissa '{premise}' não comprovada factualmentemente. Raciocínio rejeitado."
                )

        if not chain.deductions:
            chain.verdict = "HOLD"
            raise ValueError("[RACIOCINIO_ESTRUTURADO] Nenhuma dedução apresentada na cadeia.")

        self._execution_history.append(chain)
        return True

    def get_history(self) -> List[AgentThoughtChain]:
        return list(self._execution_history)


_GLOBAL_ORCHESTRATOR: Optional[TypedAgentOrchestrator] = None


def get_global_agent_orchestrator() -> TypedAgentOrchestrator:
    global _GLOBAL_ORCHESTRATOR
    if _GLOBAL_ORCHESTRATOR is None:
        _GLOBAL_ORCHESTRATOR = TypedAgentOrchestrator()
        # Registrar os agentes cognitivos canônicos (CHARs N01 a N10)
        _GLOBAL_ORCHESTRATOR.register_agent(CognitiveAgentDefinition(
            agent_id="CHAR-PLANNER-01",
            level="N01",
            persona_name="Master Planner",
            role="Planejamento estratégico, decomposição em fatias e alinhamento com intenção soberana",
            primary_port="Hangar_v1/INTELLIGENCE/CHAR/CHAR_PLANNER_01:P-INTEL-PLAN-01",
            allowed_capabilities=["RUFLO", "OPEN_DESIGN"]
        ))
        _GLOBAL_ORCHESTRATOR.register_agent(CognitiveAgentDefinition(
            agent_id="CHAR-EXECUTOR-01",
            level="N03",
            persona_name="Technical Down Plant Executor",
            role="Execução técnica restrita, mutação cirúrgica de código e conformidade N03",
            primary_port="Hangar_v1/INTELLIGENCE/CHAR/CHAR_EXECUTOR_01:P-INTEL-EXEC-01",
            allowed_capabilities=["IMPROVE"]
        ))
        _GLOBAL_ORCHESTRATOR.register_agent(CognitiveAgentDefinition(
            agent_id="CHAR-VERIFIER-01",
            level="N08",
            persona_name="Deterministic Quality Gate Auditor",
            role="Auditoria matemática fail-closed e emissão de provas SHA-256",
            primary_port="Hangar_v1/INTELLIGENCE/CHAR/CHAR_VERIFIER_01:P-INTEL-VERIFY-01",
            allowed_capabilities=["GRAPHIFY"]
        ))
        _GLOBAL_ORCHESTRATOR.register_agent(CognitiveAgentDefinition(
            agent_id="CHAR-CURATOR-01",
            level="N09",
            persona_name="Doc Tree Factual Curator",
            role="Custódia, reconciliação documental contínua e integridade factual",
            primary_port="Hangar_v1/INTELLIGENCE/CHAR/CHAR_CURATOR_01:P-INTEL-CURATOR-01",
            allowed_capabilities=["PONYTAIL"]
        ))
        _GLOBAL_ORCHESTRATOR.register_agent(CognitiveAgentDefinition(
            agent_id="CHAR-OBSIDIAN-01",
            level="N10",
            persona_name="Vault Spatial Navigator",
            role="Indexação espacial, projeção de Canvas e manutenção de grafos de conhecimento",
            primary_port="Hangar_v1/INTELLIGENCE/CHAR/CHAR_OBSIDIAN_01:P-INTEL-OBSIDIAN-01",
            allowed_capabilities=["GRAPHIFY", "OPEN_DESIGN"]
        ))
    return _GLOBAL_ORCHESTRATOR
