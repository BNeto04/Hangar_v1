"""
az000_governance.trace.engine — Motor Criptográfico de Traces Append-Only e Encadeamento SHA-256.
Garante imutabilidade, verificação em tempo de execução e fail-closed para o cômodo TRACE (Tier 9).
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from az000_governance.trace.models import SHA256_HEX_REGEX, TraceRecord


class CryptographicTraceEngine:
    """Motor de registro e verificação append-only de traces criptográficos."""

    GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

    def __init__(self, ledger_path: Optional[str] = None):
        if ledger_path is None:
            ledger_path = str(Path(r"C:\Users\PICHAU\Hangar_v1\runtime\traces\trace_ledger.jsonl"))
        self.ledger_path = Path(ledger_path)
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        self._chain: List[TraceRecord] = []
        self._index: Dict[str, TraceRecord] = {}
        self._load_ledger()

    def _load_ledger(self) -> None:
        self._chain.clear()
        self._index.clear()
        if not self.ledger_path.exists():
            return

        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                raw = line.strip()
                if not raw:
                    continue
                data = json.loads(raw)
                trace = TraceRecord(**data)
                self._chain.append(trace)
                self._index[trace.trace_id] = trace

    def get_latest_trace(self) -> Optional[TraceRecord]:
        return self._chain[-1] if self._chain else None

    def get_trace(self, trace_id: str) -> Optional[TraceRecord]:
        return self._index.get(trace_id)

    def record_trace(self, trace: TraceRecord) -> TraceRecord:
        """
        Registra um trace append-only na cadeia criptográfica.
        Invariante R-DOM-002: FAIL_CLOSED caso qualquer hash ou evidência seja inválido.
        """
        # 1. Validar integridade dos evidence_digests
        for k, digest in trace.evidence_digests.items():
            if not SHA256_HEX_REGEX.match(digest):
                raise ValueError(
                    f"FAIL_CLOSED: Evidence digest '{k}' nao eh um hash SHA-256 valido (64 hex): '{digest}'"
                )

        # 2. Determinar parent_trace_hash
        latest = self.get_latest_trace()
        if latest is None:
            trace.parent_trace_hash = self.GENESIS_HASH
        else:
            trace.parent_trace_hash = latest.trace_sha256

        # 3. Selar o trace com hash criptográfico SHA-256
        trace.seal()

        # 4. Invariante de unicidade
        if trace.trace_id in self._index:
            raise ValueError(f"FAIL_CLOSED: Trace ID '{trace.trace_id}' ja existe no ledger append-only.")

        # 5. Persistir em disco modo append-only
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(trace.to_dict(), separators=(",", ":")) + "\n")

        self._chain.append(trace)
        self._index[trace.trace_id] = trace

        return trace

    def verify_chain(self) -> Tuple[bool, str]:
        """
        Verifica a integridade completa da cadeia criptográfica do genesis até o topo.
        Qualquer anomalia resulta em falha estrita (FAIL_CLOSED).
        """
        if not self._chain:
            return True, "CHAIN_EMPTY_VALID"

        expected_parent = self.GENESIS_HASH
        for idx, trace in enumerate(self._chain):
            # Verificar integridade interna do trace
            if not trace.verify_integrity():
                return False, f"FAIL_CLOSED: Hash invalido no trace index {idx} ({trace.trace_id})."

            # Verificar integridade do elo com o pai
            if trace.parent_trace_hash != expected_parent:
                return False, (
                    f"FAIL_CLOSED: Quebra de elo criptografico no trace index {idx} ({trace.trace_id}). "
                    f"Esperado: {expected_parent}, Encontrado: {trace.parent_trace_hash}"
                )

            expected_parent = trace.trace_sha256

        return True, f"CHAIN_VERIFIED_OK: {len(self._chain)} traces autenticados com sucesso."


_GLOBAL_TRACE_ENGINE: Optional[CryptographicTraceEngine] = None


def get_global_trace_engine() -> CryptographicTraceEngine:
    global _GLOBAL_TRACE_ENGINE
    if _GLOBAL_TRACE_ENGINE is None:
        _GLOBAL_TRACE_ENGINE = CryptographicTraceEngine()
    return _GLOBAL_TRACE_ENGINE
