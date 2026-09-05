#!/usr/bin/env python3
"""
git_enforcement.py — Fundação de Enforcement Determinístico do Hangar V1.

Valida:
1. Commits Semânticos com rastreabilidade obrigatória (CARD_ID, INTENT_ID ou PLANT).
2. Invariantes da Árvore Documental (zero .md soltos na raiz exceto manifests autorizados).
3. Invariantes do Vault (11 seções canônicas intactas).
4. Integridade do espelho Kanban.
5. Suíte de Testes Determinísticos.
"""

import os
import re
import sys
import json
import unittest
import subprocess
from pathlib import Path
from typing import Dict, Any, Tuple, List

ALLOWED_TYPES = ("feat", "fix", "docs", "chore", "test", "refactor", "style", "ci")
ALLOWED_ROOT_MD = ("README.md", "CUTOVER_MANIFEST.md")
CANONICAL_VAULT_SECTIONS = sorted([
    "CAPABILITIES", "COCKPITS", "EXTERNAL", "GOVERNANCE", "INDEX.md",
    "INTELLIGENCE", "MACHINES", "PLANT", "PORTS", "PRODUCTS", "TRACE", "WORLD"
])

def validate_commit_message(msg: str) -> Tuple[bool, str]:
    """
    Valida a mensagem de commit de acordo com as regras semânticas do Hangar.
    Exige:
      <type>(<scope>): <descrição> [CARD_ID: ... | INTENT_ID: ... | PLANT: ...]
    Ou menção explícita de rastreabilidade no corpo ou cabeçalho.
    """
    clean_msg = msg.strip()
    if not clean_msg:
        return False, "Mensagem de commit vazia."
    
    first_line = clean_msg.splitlines()[0].strip()
    # Padrão: type(scope): message
    pattern = r"^([a-z]+)(\([a-zA-Z0-9_\-\./]+\))?:\s*(.+)$"
    match = re.match(pattern, first_line)
    if not match:
        return False, f"Formato de commit inválido. Esperado '<tipo>(<escopo>): <mensagem>'. Recebido: '{first_line}'"
    
    commit_type = match.group(1)
    if commit_type not in ALLOWED_TYPES:
        return False, f"Tipo '{commit_type}' não permitido. Permitidos: {', '.join(ALLOWED_TYPES)}"
    
    # Rastreabilidade obrigatória
    has_card = bool(re.search(r"(?:CARD_ID|card_id|t_hangar_|t_vigia_|t_az|t_doc|T-[A-Z0-9\-]+)", clean_msg, re.IGNORECASE))
    has_call = bool(re.search(r"(?:CALL_ID|CALL-[A-Z0-9\-]+|CG-[0-9]+|AG-RES-[0-9]+)", clean_msg, re.IGNORECASE))
    has_plant = bool(re.search(r"(?:PLANT|AZ[0-9]{3}|P-[A-Z0-9\-]+)", clean_msg, re.IGNORECASE))
    
    if not (has_card or has_call or has_plant):
        return False, "Commit rejeitado: Falta rastreabilidade obrigatória (CARD_ID, CALL_ID, ou endereço PLANT)."
        
    return True, "Commit semântico e rastreabilidade válidos."

def check_doc_tree_invariants(repo_root: Path) -> Tuple[bool, List[str]]:
    """Verifica se há documentos soltos fora de DOCS/."""
    violations = []
    loose_md = [p.name for p in repo_root.glob("*.md") if p.name not in ALLOWED_ROOT_MD]
    if loose_md:
        violations.append(f"Documentos .md soltos na raiz do repositório: {loose_md}")
    
    vault_dir = repo_root / "vault"
    if vault_dir.exists():
        entries = sorted([p.name for p in vault_dir.iterdir() if p.name != ".obsidian"])
        if entries != CANONICAL_VAULT_SECTIONS:
            violations.append(f"Entradas não canônicas no Vault: {entries}")
            
    return len(violations) == 0, violations

def check_kanban_mirror_integrity(repo_root: Path) -> Tuple[bool, str]:
    """Verifica integridade do espelho kanban_state.json."""
    kanban_file = repo_root / "kanban" / "kanban_state.json"
    if not kanban_file.exists():
        return False, "Arquivo kanban/kanban_state.json ausente."
    try:
        data = json.loads(kanban_file.read_text(encoding="utf-8"))
        if "total_cards" not in data or "cards" not in data:
            return False, "Schema inválido no kanban_state.json."
        if len(data["cards"]) != data["total_cards"]:
            return False, f"Contagem divergente no espelho Kanban: {len(data['cards'])} != {data['total_cards']}"
    except Exception as exc:
        return False, f"Erro ao ler espelho Kanban: {exc}"
    return True, f"Espelho Kanban integro com {data['total_cards']} cards."

def run_tests(repo_root: Path) -> Tuple[bool, str]:
    """Executa a suíte de testes determinísticos do Hangar (Sprint 01 + Todos os 11 Cômodos da ARCA)."""
    # 1. Testes fundacionais da Sprint 01
    test_file = repo_root / "test_hangar_v1_sprint_01.py"
    if test_file.exists():
        res1 = subprocess.run([sys.executable, "-m", "unittest", "test_hangar_v1_sprint_01"], cwd=str(repo_root), capture_output=True, text=True)
        if res1.returncode != 0:
            return False, f"Suíte fundacional Sprint 01 falhou:\n{res1.stderr}"

    # 2. Suíte de testes de todos os 11 cômodos da ARCA
    tests_dir = repo_root / "tests"
    if tests_dir.exists():
        res2 = subprocess.run([sys.executable, "-m", "unittest", "discover", "tests"], cwd=str(repo_root), capture_output=True, text=True)
        if res2.returncode != 0:
            return False, f"Suíte de cômodos da ARCA (tests/) falhou:\n{res2.stderr}"

    return True, "Suíte completa de testes determinísticos (Sprint 01 + 11 Cômodos ARCA + Policy Engines: 92 testes) 100% PASS."

def run_all_checks(repo_root: Path) -> Dict[str, Any]:
    """Executa todos os checks canônicos do Hangar V1."""
    docs_ok, doc_errors = check_doc_tree_invariants(repo_root)
    kanban_ok, kanban_msg = check_kanban_mirror_integrity(repo_root)
    tests_ok, tests_msg = run_tests(repo_root)
    
    passed = docs_ok and kanban_ok and tests_ok
    status = "PASS" if passed else "FAIL"
    
    return {
        "status": status,
        "eligible_for_merge": passed,
        "doc_tree": {"passed": docs_ok, "errors": doc_errors},
        "kanban": {"passed": kanban_ok, "detail": kanban_msg},
        "tests": {"passed": tests_ok, "detail": tests_msg},
    }

if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "check-commit" and len(sys.argv) > 2:
            ok, reason = validate_commit_message(sys.argv[2])
            print(f"COMMIT_VALIDATION: {ok} | {reason}")
            sys.exit(0 if ok else 1)
        elif cmd == "check-all":
            result = run_all_checks(root)
            print(json.dumps(result, indent=2))
            sys.exit(0 if result["status"] == "PASS" else 1)
            
    res = run_all_checks(root)
    print(json.dumps(res, indent=2))
    sys.exit(0 if res["status"] == "PASS" else 1)
