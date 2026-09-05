#!/usr/bin/env python3
"""
ingestor.py — Adaptador de Ingestão e Selagem de Intenções da Ponte (AZ000).
Converte envelopes textuais brutos da PR #1/Webhook em SealedIntentContracts e HandoffEnvelopes.
"""

import json
import logging
import os
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from .circuit import OwnerIntentCircuit
from .contracts import HandoffEnvelope, SealedIntentContract

logging.basicConfig(level=logging.INFO, format="%(asctime)s [az000-ingestor] %(levelname)s: %(message)s")
logger = logging.getLogger("az000-ingestor")

SEALED_CONTRACTS_DIR = Path(r"C:\Users\PICHAU\Hangar_v1\runtime\sealed_contracts")

def parse_raw_call_envelope(text: str) -> Dict[str, Any]:
    """Extrai campos canônicos de um envelope textual de CALL."""
    data = {}
    
    # CALL_ID
    m_call = re.search(r"CALL_ID:\s*([^\r\n]+)", text)
    if m_call:
        data["call_id"] = m_call.group(1).strip()
    else:
        m_cg = re.search(r"(CG-\d+)", text)
        if m_cg:
            data["call_id"] = m_cg.group(1).strip()
        else:
            data["call_id"] = None

    # OWNER_ID / FROM
    m_from = re.search(r"(?:FROM|OWNER|AUTHOR):\s*([^\r\n]+)", text, re.IGNORECASE)
    if m_from:
        data["owner_id"] = m_from.group(1).strip()
    elif "CG-" in text or "CHATGPT" in text:
        data["owner_id"] = "CHATGPT"
    else:
        data["owner_id"] = "OWNER"

    # ACTION
    m_action = re.search(r"ACTION:\s*([^\r\n]+)", text)
    if m_action:
        data["action"] = m_action.group(1).strip()
    else:
        data["action"] = "EXECUTE_TASK"

    # SCOPE
    m_scope = re.search(r"(?:DP_PROJECT|TARGET_CARD|TARGET|SCOPE):\s*([^\r\n]+)", text)
    if m_scope:
        data["scope"] = m_scope.group(1).strip()
    else:
        data["scope"] = "Hangar_v1"

    # DIRECTIVES / RULES
    directives = []
    for line in text.splitlines():
        line_clean = line.strip()
        if line_clean.startswith("OWNER_DIRECTIVE:") or line_clean.startswith("PURPOSE:"):
            directives.append(line_clean)
        elif line_clean.startswith("DP_"):
            directives.append(line_clean)
    data["directives"] = directives

    data["raw_payload"] = {"raw_text": text}
    return data

def ingest_and_seal_call(text: str) -> Dict[str, Any]:
    """
    Executa o pipeline completo do AZ000:
    Ingestão -> Normalização -> Validação Fail-Closed -> Selagem SHA-256 -> Persistência -> Handoff.
    """
    raw_data = parse_raw_call_envelope(text)
    
    if not raw_data.get("call_id"):
        return {
            "status": "FAILED",
            "stage": "INGESTION",
            "error": "Nenhum CALL_ID ou CG-xxxx identificado no payload.",
            "sealed_contract": None,
            "handoff_envelope": None
        }

    pipeline_res = OwnerIntentCircuit.execute_full_pipeline(raw_data)
    
    if pipeline_res.get("status") == "SUCCESS" and pipeline_res.get("sealed_contract"):
        contract = pipeline_res["sealed_contract"]
        contract_dict = contract if isinstance(contract, dict) else asdict(contract)
        contract_id = contract_dict.get("contract_id")
        
        # Persistir contrato selado no disco
        SEALED_CONTRACTS_DIR.mkdir(parents=True, exist_ok=True)
        contract_file = SEALED_CONTRACTS_DIR / f"{contract_id}.json"
        contract_file.write_text(json.dumps(contract_dict, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info(f"Contrato selado persistido com sucesso: {contract_file} (SHA256={contract_dict.get('contract_sha256')})")
        pipeline_res["contract_file"] = str(contract_file)

    return pipeline_res

if __name__ == "__main__":
    sample = """CG-000128
TYPE: CALL
TO: ANTIGRAVITY
CALL_ID: CALL-HANGAR-CONTINUOUS-FLOW-NEXT-CYCLE-001
OWNER_DIRECTIVE: TRUE
ACTION: CONTINUE_WITH_NEXT_USEFUL_TASK
DP_PROJECT: Hangar_v1
"""
    res = ingest_and_seal_call(sample)
    print(json.dumps(res, indent=2, default=str))
