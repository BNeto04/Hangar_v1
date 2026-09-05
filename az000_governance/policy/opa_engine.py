"""
az000_governance.policy.opa_engine — Motor Canônico de Deliberação de Quality Gates OPA / Rego.
Avaliação estrutural determinística de envelopes de evidências JSON sem abertura de portas de rede.
Referência: DOCS/09_HANGAR_GOVERNANCE_ROADTRACE.md (Critério 2, GAP-002).
Invariante: R-DOM-002 (FAIL_CLOSED_SYSTEMIC), R-DOM-007 (EVIDENCE_FIRST_PROMOTION).
"""

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Any, Dict, List, Optional, Tuple


SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")


class OpaGateVerdict(str, Enum):
    ALLOW = "ALLOW"
    HOLD = "HOLD"
    DENY = "DENY"


@dataclass
class QualityGateEvaluation:
    verdict: OpaGateVerdict
    allowed: bool
    violations: List[str]
    audit_trace: Dict[str, Any]


class OpaQualityGateEngine:
    """Motor de avaliação lógica OPA / Rego para deliberação de quality gates."""

    def __init__(self):
        pass

    def evaluate_gate(self, gate_input: Dict[str, Any]) -> QualityGateEvaluation:
        """
        Avalia deterministicamente as regras de gate:
        Regra 1: Verifier (N08) deve atestar 'VERIFICATION_PASSED'.
        Regra 2: Security Review (N06) deve atestar 'SECURITY_PASS'.
        Regra 3: Todos os evidence digests presentes devem ser hashes SHA-256 válidos (64 hex).
        Regra 4: A lista de 'blocking_reasons' deve estar rigorosamente vazia.
        Fail-Closed: Qualquer anomalia ou ausência de evidência trava em HOLD ou DENY.
        """
        violations: List[str] = []
        evidence = gate_input.get("evidence", {})

        # 1. Checagem do Verifier N08
        verifier_status = evidence.get("verifier_status") or gate_input.get("verifier_status")
        if verifier_status != "VERIFICATION_PASSED":
            violations.append(
                f"OPA_REGO_RULE_01_FAIL: Verifier reportou '{verifier_status}' (esperado: 'VERIFICATION_PASSED')."
            )

        # 2. Checagem de Segurança N06
        security_status = evidence.get("security_status") or gate_input.get("security_status")
        if security_status != "SECURITY_PASS":
            violations.append(
                f"OPA_REGO_RULE_02_FAIL: Security review reportou '{security_status}' (esperado: 'SECURITY_PASS')."
            )

        # 3. Validação dos hashes SHA-256 de evidência
        digests = evidence.get("digests") or gate_input.get("evidence_digests") or {}
        if not digests:
            violations.append("OPA_REGO_RULE_03_FAIL: Nenhum digest SHA-256 de evidencia fornecido.")
        else:
            for k, h in digests.items():
                if not isinstance(h, str) or not SHA256_REGEX.match(h):
                    violations.append(
                        f"OPA_REGO_RULE_03_FAIL: Evidence digest '{k}' invalido ou adulterado: '{h}'."
                    )

        # 4. Checagem de razões impeditivas
        blocking = gate_input.get("blocking_reasons") or []
        if blocking:
            violations.append(f"OPA_REGO_RULE_04_FAIL: Ha {len(blocking)} razoes bloqueantes registradas: {blocking}")

        # Veredito estrito fail-closed
        if violations:
            return QualityGateEvaluation(
                verdict=OpaGateVerdict.HOLD,
                allowed=False,
                violations=violations,
                audit_trace={
                    "rule_engine": "OPA_REGO_IN_PROCESS_V1",
                    "total_violations": len(violations),
                    "verdict": "HOLD_REJECTED"
                }
            )

        return QualityGateEvaluation(
            verdict=OpaGateVerdict.ALLOW,
            allowed=True,
            violations=[],
            audit_trace={
                "rule_engine": "OPA_REGO_IN_PROCESS_V1",
                "total_violations": 0,
                "verdict": "ALLOW_ADVANCE"
            }
        )
