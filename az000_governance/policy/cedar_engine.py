"""
az000_governance.policy.cedar_engine — Motor Canônico de Políticas de Autoridade Cedar.
Implementação determinística e em-processo da semântica Cedar (permit/forbid) para o Hangar V1.
Referência: DOCS/09_HANGAR_GOVERNANCE_ROADTRACE.md (Critério 2, GAP-001).
Invariante: R-DOM-001 (SOBERANIA_PROPRIETARIO), R-DOM-002 (FAIL_CLOSED_SYSTEMIC default-deny).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class CedarEffect(str, Enum):
    PERMIT = "permit"
    FORBID = "forbid"


class CedarDecision(str, Enum):
    PERMIT = "PERMIT"
    FORBID = "FORBID"


@dataclass(frozen=True)
class CedarEntity:
    entity_type: str  # ex: "User", "Role", "Agent", "Port", "Artifact"
    entity_id: str    # ex: "PROPRIETARIO", "CHAR-EXECUTOR-01", "P-GOV-AUTH-01"

    def to_string(self) -> str:
        return f'{self.entity_type}::"{self.entity_id}"'


@dataclass(frozen=True)
class CedarPolicy:
    policy_id: str
    effect: CedarEffect
    principal_type: str  # "*" para qualquer um ou nome exato ex: "User"
    principal_id: Optional[str] = None
    action_name: str = "*"  # "*" para qualquer ação ou nome exato ex: 'Action::"MUTATE_CODE"'
    resource_type: str = "*"
    resource_id: Optional[str] = None
    description: str = ""

    def matches(self, principal: CedarEntity, action: str, resource: CedarEntity) -> bool:
        # Match principal
        if self.principal_type != "*" and self.principal_type != principal.entity_type:
            return False
        if self.principal_id is not None and self.principal_id != principal.entity_id:
            return False

        # Match action
        if self.action_name != "*" and self.action_name != action:
            return False

        # Match resource
        if self.resource_type != "*" and self.resource_type != resource.entity_type:
            return False
        if self.resource_id is not None and self.resource_id != resource.entity_id:
            return False

        return True


class CedarAuthorityEngine:
    """Motor de avaliação determinística de autoridade baseado na semântica Cedar."""

    def __init__(self):
        self._policies: Dict[str, CedarPolicy] = {}
        self._load_canonical_hangar_policies()

    def _load_canonical_hangar_policies(self):
        # 1. Soberania do Proprietário: PERMIT irrestrito para todas as ações e recursos (R-DOM-001)
        self.add_policy(
            CedarPolicy(
                policy_id="policy-sovereign-owner-all",
                effect=CedarEffect.PERMIT,
                principal_type="User",
                principal_id="PROPRIETARIO",
                action_name="*",
                resource_type="*",
                description="O Proprietario detem autoridade maxima sobre todas as acoes."
            )
        )

        # 2. Executor N03: PERMIT para executar mutações e compilações de código
        self.add_policy(
            CedarPolicy(
                policy_id="policy-executor-write-code",
                effect=CedarEffect.PERMIT,
                principal_type="Agent",
                principal_id="CHAR-EXECUTOR-01",
                action_name='Action::"MUTATE_CODE"',
                resource_type="Artifact",
                description="Executor N03 detem monopolio de mutacao fisica autorizada."
            )
        )

        # 3. Lentes Read-Only (N04, N05, N06): FORBID explícito para qualquer ação de escrita ou mutação
        for lens_id in ("CHAR-REVIEWER-01", "CHAR-DDD-01", "CHAR-SECURITY-01", "CHAR-VERIFIER-01"):
            self.add_policy(
                CedarPolicy(
                    policy_id=f"policy-forbid-write-{lens_id.lower()}",
                    effect=CedarEffect.FORBID,
                    principal_type="Agent",
                    principal_id=lens_id,
                    action_name='Action::"MUTATE_CODE"',
                    resource_type="Artifact",
                    description="Lentes operam em modo payload-in / parecer-out (sem permissao de escrita)."
                )
            )

    def add_policy(self, policy: CedarPolicy) -> None:
        self._policies[policy.policy_id] = policy

    def remove_policy(self, policy_id: str) -> None:
        self._policies.pop(policy_id, None)

    def evaluate(
        self,
        principal: CedarEntity,
        action: str,
        resource: CedarEntity,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[CedarDecision, str]:
        """
        Avalia a solicitação segundo a semântica Cedar:
        - Se qualquer política FORBID casar -> FORBID imediato (forbid trumps permit).
        - Se ao menos uma política PERMIT casar e nenhuma FORBID -> PERMIT.
        - Se nenhuma política casar -> FORBID (Fail-Closed Default Deny, R-DOM-002).
        """
        matching_forbids: List[CedarPolicy] = []
        matching_permits: List[CedarPolicy] = []

        for p in self._policies.values():
            if p.matches(principal, action, resource):
                if p.effect == CedarEffect.FORBID:
                    matching_forbids.append(p)
                elif p.effect == CedarEffect.PERMIT:
                    matching_permits.append(p)

        if matching_forbids:
            reasons = ", ".join(p.policy_id for p in matching_forbids)
            return CedarDecision.FORBID, f"FAIL_CLOSED: Rejeitado explicitamente por politica FORBID ({reasons})."

        if matching_permits:
            reasons = ", ".join(p.policy_id for p in matching_permits)
            return CedarDecision.PERMIT, f"Autorizado por politica PERMIT ({reasons})."

        return CedarDecision.FORBID, "FAIL_CLOSED: Rejeitado por falta de politica PERMIT aplicavel (Default Deny)."
