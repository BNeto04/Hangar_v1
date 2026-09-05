#!/usr/bin/env python3
"""
canonical_domain_rules.py — Módulo ARCA: Repositório Único e Imutável de Regras de Domínio.
Invariante: SINGLE_SOURCE_OF_TRUTH_ARCA.
Nenhum módulo deve duplicar regras de domínio localmente; todos devem referenciar este artefato.
"""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

ARCA_SCHEMA_VERSION = "AZ000-ARCA-DOMAIN-RULES-1"

@dataclass(frozen=True)
class DomainRule:
    rule_id: str
    name: str
    category: str
    description: str
    rationale: str
    enforcement: str  # FAIL_CLOSED, STATIC_CHECK, GATE_ARBITER, SOVEREIGN_DECISION
    is_active: bool = True

@dataclass(frozen=True)
class RoomDefinition:
    room_id: str
    room_name: str
    tier: int
    dependencies: Tuple[str, ...]
    description: str
    closure_criteria: Tuple[str, ...]

# Tabela Canônica e Imutável de Regras de Domínio do Hangar V1
_CANONICAL_RULES: Tuple[DomainRule, ...] = (
    DomainRule(
        rule_id="R-DOM-001",
        name="SOBERANIA_PROPRIETARIO",
        category="GOVERNANCE_AUTHORITY",
        description="O Proprietário detém a autoridade máxima e prerrogativa irrevogável sobre intenção, prioridade, escopo, regras de parada, homologação de fatias e autorização de publicação.",
        rationale="Garante que nenhuma máquina ou agente de SLM usurpe o monopólio de decisão humana estratégica.",
        enforcement="SOVEREIGN_DECISION",
    ),
    DomainRule(
        rule_id="R-DOM-002",
        name="FAIL_CLOSED_SYSTEMIC",
        category="SAFETY_INVARIANT",
        description="Diante de qualquer ambiguidade, inconsistência, corrupção de estado, falha de prova ou ausência de sinal, o sistema aborta a transição e trava em HOLD ou REJECT.",
        rationale="Elimina fallbacks silenciosos e comportamentos hipotéticos não comprovados.",
        enforcement="FAIL_CLOSED",
    ),
    DomainRule(
        rule_id="R-DOM-003",
        name="NO_UNSEALED_PASS",
        category="INGESTION_INTEGRITY",
        description="Nenhuma chamada ou instrução de agentes externos transita para o Planner ou Executor sem passar pelo circuito de validação AZ000 e receber selo imutável SHA-256 (SealedIntentContract).",
        rationale="Protege a esteira de execução contra injeções espúrias, comandos desprovidos de autoridade e escopos corrompidos.",
        enforcement="GATE_ARBITER",
    ),
    DomainRule(
        rule_id="R-DOM-004",
        name="NO_SPEC_NO_CODE",
        category="DEVELOPMENT_LIFECYCLE",
        description="Nenhuma alteração de código, teste ou documentação de produto pode ocorrer sem especificação formal prévia e card visível registrado no Hermes Kanban.",
        rationale="Previne mutações desgovernadas, escopo oculto e débito técnico invisível.",
        enforcement="STATIC_CHECK",
    ),
    DomainRule(
        rule_id="R-DOM-005",
        name="ROOM_BY_ROOM_ORDER",
        category="TOPOLOGICAL_DISCIPLINE",
        description="SPECs e desenvolvimentos são estritamente por CÔMODO. É mandatório fechar 100% as especificações, testes e documentação no Vault do cômodo atual antes de avançar para o cômodo seguinte, respeitando a ordem topológica de dependências.",
        rationale="Impede fragmentação de esforço, acoplamento desordenado e cômodos incompletos deixados para trás.",
        enforcement="GATE_ARBITER",
    ),
    DomainRule(
        rule_id="R-DOM-006",
        name="SINGLE_SOURCE_OF_TRUTH_ARCA",
        category="ARCHITECTURAL_COHERENCE",
        description="Todas as regras de domínio residem única e exclusivamente no módulo ARCA. É terminantemente proibido redefinir ou duplicar regras de domínio em submódulos locais.",
        rationale="Garante ausência de ambiguidades, contradições e divergências de interpretação entre agentes.",
        enforcement="STATIC_CHECK",
    ),
    DomainRule(
        rule_id="R-DOM-007",
        name="EVIDENCE_FIRST_PROMOTION",
        category="QUALITY_GATE",
        description="A promoção de tarefas para T5 (Done) exige prova material auditada (testes aprovados, hashes SHA-256 e parecer de lentes). Auto-declaração de sucesso pelo executor é proibida.",
        rationale="Assegura que apenas entregas factualmente comprovadas obtenham homologação.",
        enforcement="FAIL_CLOSED",
    ),
)

# Ordem Canônica de Cômodos do Hangar V1 (Topologia de Dependências)
_CANONICAL_ROOMS: Tuple[RoomDefinition, ...] = (
    RoomDefinition(
        room_id="ROOM-01",
        room_name="GOVERNANCE",
        tier=1,
        dependencies=(),
        description="Fundação soberana, módulo ARCA, regras de domínio, quality gates e autoridade.",
        closure_criteria=(
            "ARCA implementada e auditada",
            "Monólito de Governança GOVERNANCE.md atualizado",
            "Políticas de authority mapeadas",
        ),
    ),
    RoomDefinition(
        room_id="ROOM-02",
        room_name="WORLD",
        tier=2,
        dependencies=("GOVERNANCE",),
        description="Modelo de mundo, ontologia do território, grafo e canvas espacial.",
        closure_criteria=(
            "01_WORLD_MODEL.md validado",
            "Master_World.canvas com zero links quebrados",
            "Ontologia de entidades consolidada",
        ),
    ),
    RoomDefinition(
        room_id="ROOM-03",
        room_name="PLANT",
        tier=3,
        dependencies=("GOVERNANCE", "WORLD"),
        description="Topologia física, infraestrutura de execução, workspaces e isolamento de pastas.",
        closure_criteria=(
            "03_ADDRESS_SCHEMA.md validado",
            "Workspaces de agentes confinados",
            "Estrutura física do Vault mapeada",
        ),
    ),
    RoomDefinition(
        room_id="ROOM-04",
        room_name="PORTS",
        tier=4,
        dependencies=("GOVERNANCE", "PLANT"),
        description="Portas tipadas, esquemas de endereçamento e contratos imutáveis de comunicação.",
        closure_criteria=(
            "Envelopes tipados definidos",
            "Protocolos de despacho formalizados",
            "Contratos SHA-256 ativados",
        ),
    ),
    RoomDefinition(
        room_id="ROOM-05",
        room_name="CAPABILITIES",
        tier=5,
        dependencies=("GOVERNANCE", "PORTS"),
        description="Bibliotecas e motores estruturais (Graphify, Improve, Ruflo, Open Design).",
        closure_criteria=(
            "Motores integrados e sem dependências cíclicas",
            "Curadoria determinística verificada",
        ),
    ),
    RoomDefinition(
        room_id="ROOM-06",
        room_name="MACHINES",
        tier=6,
        dependencies=("PORTS", "CAPABILITIES"),
        description="Nano Máquinas determinísticas de estado e autômatas de apoio.",
        closure_criteria=(
            "Transições de estado puras",
            "Tratamento estrito de erros",
        ),
    ),
    RoomDefinition(
        room_id="ROOM-07",
        room_name="INTELLIGENCE",
        tier=7,
        dependencies=("GOVERNANCE", "PORTS", "MACHINES"),
        description="Agentes cognitivos confinados com papéis exclusivos (CHARs N01 a N10).",
        closure_criteria=(
            "Configurações platform_toolsets.cli isoladas",
            "Sem vazamento de permissão de escrita para lentes",
        ),
    ),
    RoomDefinition(
        room_id="ROOM-08",
        room_name="EXTERNAL",
        tier=8,
        dependencies=("PORTS", "INTELLIGENCE"),
        description="Fronteiras e adaptadores de borda (GitHub PR #1, Webhook, Telegram, Browser).",
        closure_criteria=(
            "Transportes orientados a eventos comprovados",
            "Deduplicação e HMAC SHA-256 ativos",
        ),
    ),
    RoomDefinition(
        room_id="ROOM-09",
        room_name="TRACE",
        tier=9,
        dependencies=("GOVERNANCE", "INTELLIGENCE", "EXTERNAL"),
        description="Trilhas append-only de auditoria, evidências criptográficas e traces N08.",
        closure_criteria=(
            "06_TRACE_SCHEMA.md em conformidade",
            "Hashes SHA-256 verificáveis",
        ),
    ),
    RoomDefinition(
        room_id="ROOM-10",
        room_name="COCKPITS",
        tier=10,
        dependencies=("INTELLIGENCE", "TRACE"),
        description="Painéis de visualização humana, Teacher Mode e consoles de controle.",
        closure_criteria=(
            "Visualização espacial sem atrito",
            "Mapeamento de comandos do Proprietário",
        ),
    ),
    RoomDefinition(
        room_id="ROOM-11",
        room_name="PRODUCTS",
        tier=11,
        dependencies=("GOVERNANCE", "WORLD", "PLANT", "PORTS", "CAPABILITIES", "MACHINES", "INTELLIGENCE", "EXTERNAL", "TRACE", "COCKPITS"),
        description="Entregáveis de software, produtos acabados e releases homologados.",
        closure_criteria=(
            "Todos os 10 cômodos precedentes fechados e auditados",
            "Homologação explícita do Proprietário",
        ),
    ),
)

# Exportação Imutável Pública
ARCA_DOMAIN_RULES: Tuple[DomainRule, ...] = _CANONICAL_RULES
ROOM_EXECUTION_ORDER: Tuple[RoomDefinition, ...] = _CANONICAL_ROOMS

def get_domain_rules() -> Tuple[DomainRule, ...]:
    """Retorna todas as regras de domínio da ARCA em tupla imutável."""
    return ARCA_DOMAIN_RULES

def get_rule_by_id(rule_id: str) -> Optional[DomainRule]:
    """Busca uma regra de domínio pelo seu identificador unívoco."""
    for rule in ARCA_DOMAIN_RULES:
        if rule.rule_id == rule_id:
            return rule
    return None

def get_room_order() -> Tuple[RoomDefinition, ...]:
    """Retorna a ordem topológica de cômodos do Hangar V1."""
    return ROOM_EXECUTION_ORDER

def get_room_dependencies(room_name: str) -> List[str]:
    """Retorna a lista de dependências obrigatórias para o cômodo indicado."""
    for r in ROOM_EXECUTION_ORDER:
        if r.room_name.upper() == room_name.upper():
            return list(r.dependencies)
    raise KeyError(f"Cômodo desconhecido: '{room_name}'")

def compute_arca_sha256() -> str:
    """Calcula o hash SHA-256 determinístico de todo o conteúdo normativo da ARCA."""
    rules_payload = [
        {
            "rule_id": r.rule_id,
            "name": r.name,
            "category": r.category,
            "description": r.description,
            "rationale": r.rationale,
            "enforcement": r.enforcement,
        }
        for r in ARCA_DOMAIN_RULES
    ]
    rooms_payload = [
        {
            "room_id": r.room_id,
            "room_name": r.room_name,
            "tier": r.tier,
            "dependencies": list(r.dependencies),
            "closure_criteria": list(r.closure_criteria),
        }
        for r in ROOM_EXECUTION_ORDER
    ]
    bundle = {
        "schema": ARCA_SCHEMA_VERSION,
        "rules": rules_payload,
        "rooms": rooms_payload,
    }
    serialized = json.dumps(bundle, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

def verify_arca_integrity() -> bool:
    """Verifica a integridade intrínseca do módulo ARCA."""
    rule_ids = [r.rule_id for r in ARCA_DOMAIN_RULES]
    if len(rule_ids) != len(set(rule_ids)):
        return False  # Duplicação de regra detectada
    room_names = [r.room_name for r in ROOM_EXECUTION_ORDER]
    if len(room_names) != len(set(room_names)):
        return False  # Duplicação de cômodo detectada
    return True

if __name__ == "__main__":
    print(f"ARCA v{ARCA_SCHEMA_VERSION}")
    print(f"Total Rules: {len(ARCA_DOMAIN_RULES)}")
    print(f"Total Rooms: {len(ROOM_EXECUTION_ORDER)}")
    print(f"ARCA SHA256: {compute_arca_sha256()}")
    print(f"Integrity PASS: {verify_arca_integrity()}")
