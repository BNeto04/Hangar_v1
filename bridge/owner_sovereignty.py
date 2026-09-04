#!/usr/bin/env python3
"""
owner_sovereignty.py — Motor de Precedência Soberana e Despacho Anti-Silêncio.

Invariantes:
1. OWNER_DIRECTIVE tem precedência soberana sobre filas de espera, rotinas e auditorias pendentes.
2. Anti-Silêncio: Uma auditoria pendente NUNCA pode causar silêncio para o Proprietário.
3. Se houver bloqueio técnico, de segurança ou de escopo, este deve ser reportado como BLOQUEIO FACTUAL imediato, nunca como prioridade superior ao Owner.
"""

from typing import Dict, Any, Tuple

# Matriz de Poderes Reais
REAL_POWERS_MATRIX = {
    "Sentinela_PC_Casa": {
        "node_type": "REMOTE_TELEGRAM_SENTINEL",
        "authorized_powers": [
            "RECEIVE_AUTHENTICATED_OWNER_COMMANDS",
            "READ_LIVE_KANBAN_STATE",
            "READ_GITHUB_BRIDGE_PR_STATE",
            "DISPATCH_LOCAL_WAKE_TRIGGER",
            "PUSH_TELEGRAM_NOTIFICATIONS_TO_OWNER",
            "APPEND_AUDITABLE_JOURNAL_DIRECTIVE"
        ],
        "prohibited_powers": [
            "ARBITRARY_CODE_MUTATION",
            "UNVALIDATED_CARD_PROMOTION",
            "EXTERNAL_UNAUTHORIZED_NETWORK_CALLS"
        ]
    },
    "Antigravity": {
        "node_type": "PRIMARY_LOCAL_EXECUTOR",
        "authorized_powers": [
            "CODE_ANALYSIS_AND_MUTATION",
            "DETERMINISTIC_TEST_EXECUTION",
            "QUALITY_GATE_DELIBERATION_REQUEST",
            "CANONICAL_PR_POSTING_AND_COMMIT",
            "IMMEDIATE_OWNER_STATUS_RESPONSE"
        ],
        "prohibited_powers": [
            "SILENT_WAIT_ON_PENDING_AUDIT_WHEN_OWNER_ASKS",
            "PROMOTION_WITHOUT_OWNER_OR_GATE_APPROVAL",
            "MUTATION_OUTSIDE_CANONICAL_SCOPE"
        ]
    }
}

def evaluate_precedence(
    sender_id: str,
    directive_type: str,
    action: str,
    pending_audit: bool = False,
    safety_violation: bool = False,
    scope_violation: bool = False
) -> Dict[str, Any]:
    """
    Avalia a precedência da ação requisitada.
    Retorna decisão com status: EXECUTE_IMMEDIATELY, REPORT_FACTUAL_BLOCKER ou HOLD.
    """
    is_owner = (directive_type == "OWNER_DIRECTIVE" or sender_id in ("OWNER", "Manoel", "6857459665"))
    
    if not is_owner:
        if pending_audit:
            return {
                "decision": "WAIT_FOR_AUDIT",
                "reason": "Rotina não soberana aguardando auditoria do Codex/ChatGPT.",
                "action_allowed": False
            }
        return {
            "decision": "STANDARD_QUEUE",
            "reason": "Processamento padrão de rotina.",
            "action_allowed": True
        }

    # Tratamento Soberano do Proprietário (OWNER)
    if safety_violation:
        return {
            "decision": "REPORT_FACTUAL_BLOCKER",
            "blocker_type": "SAFETY_VIOLATION",
            "reason": "Ação bloqueada por restrição factual de segurança do sistema.",
            "action_allowed": False,
            "anti_silence_response": "Ação solicitada viola invariante de segurança; execução retida com bloqueio factual reportado."
        }
        
    if scope_violation:
        return {
            "decision": "REPORT_FACTUAL_BLOCKER",
            "blocker_type": "SCOPE_VIOLATION",
            "reason": "Ação solicitada excede o escopo canônico autorizado do Hangar.",
            "action_allowed": False,
            "anti_silence_response": "Ação solicitada excede o escopo autorizado; execução retida com bloqueio factual reportado."
        }

    # Se há auditoria pendente, o Owner NÃO é silenciado nem bloqueado
    if pending_audit:
        return {
            "decision": "EXECUTE_IMMEDIATELY_PREEMPT_AUDIT",
            "reason": "OWNER_DIRECTIVE possui precedência máxima. Auditoria pendente informada mas não bloqueia resposta.",
            "action_allowed": True,
            "anti_silence_response": "Diretiva do Proprietário acolhida imediatamente; auditoria pendente registrada no contexto sem causar silêncio."
        }

    return {
        "decision": "EXECUTE_IMMEDIATELY",
        "reason": "Diretiva do Proprietário válida e dentro dos limites operacionais.",
        "action_allowed": True,
        "anti_silence_response": "Diretiva do Proprietário em execução imediata."
    }
