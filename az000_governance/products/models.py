"""
az000_governance.products.models — Modelos canônicos de produtos de software, release notes e manifestos de integridade.
Referência ARCA: R-DOM-002 (FAIL_CLOSED_SYSTEMIC), R-DOM-005 (ROOM_BY_ROOM_ORDER), R-DOM-006 (SINGLE_SOURCE_OF_TRUTH_ARCA).
Critérios ARCA: "Release notes canônicas validadas", "Manifesto de integridade final emitido".
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ProductArtifact:
    name: str
    version: str
    tier: int
    primary_port: str
    sha256: str
    description: str


@dataclass
class CanonicalReleaseNotes:
    release_tag: str
    release_title: str
    date_iso: str
    tier_summaries: List[Dict[str, Any]]
    total_tests_passed: int
    hash_manifest: Dict[str, str]
    overall_status: str  # HOMOLOGATED, REJECTED, PENDING

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ProductIntegrityManifest:
    manifest_id: str
    timestamp_iso: str
    release_tag: str
    room_digests: Dict[str, str]
    ledger_digest: str
    root_sha256: str = ""
    is_complete: bool = False

    def compute_root_hash(self) -> str:
        data = {
            "manifest_id": self.manifest_id,
            "timestamp_iso": self.timestamp_iso,
            "release_tag": self.release_tag,
            "room_digests": self.room_digests,
            "ledger_digest": self.ledger_digest,
        }
        serialized = json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    def seal(self) -> "ProductIntegrityManifest":
        if not self.root_sha256:
            self.root_sha256 = self.compute_root_hash()
        self.is_complete = True
        return self

    def verify_integrity(self) -> bool:
        if not self.root_sha256:
            return False
        return self.root_sha256 == self.compute_root_hash()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
