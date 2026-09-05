"""
az000_governance.capabilities.graphify_engine — Motor Determinístico Graphify.
Realiza extração e validação do grafo de nós e wikilinks no Vault.
Em conformidade com a especificação Obsidian e DOCS/07_DOC_TREE_CURATORSHIP.md.
"""

import re
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from .models import CapabilityExecutionResult
from datetime import datetime, timezone

WIKILINK_REGEX = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")
INLINE_CODE_REGEX = re.compile(r"`[^`]+`")


class GraphifyEngine:
    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path).resolve()

    def audit_vault_graph(self) -> Tuple[CapabilityExecutionResult, Dict[str, Any]]:
        nodes: Set[str] = set()
        basenames: Dict[str, str] = {}
        edges: List[Tuple[str, str]] = []
        broken_links: List[Tuple[str, str]] = []

        if not self.vault_path.exists():
            return CapabilityExecutionResult(
                capability_id="GRAPHIFY",
                status="FAILED",
                timestamp_iso=datetime.now(timezone.utc).isoformat(),
                summary=f"Vault path nao encontrado: {self.vault_path}"
            ), {}

        # Mapear todos os arquivos no vault
        for f in self.vault_path.rglob("*.*"):
            if f.is_file():
                rel_path = f.relative_to(self.vault_path).as_posix()
                node_key = rel_path.replace(".md", "")
                nodes.add(node_key)
                nodes.add(rel_path)
                basenames[f.stem] = node_key
                basenames[f.name] = node_key

        # Extrair e verificar arestas
        for md_file in self.vault_path.rglob("*.md"):
            src_node = md_file.relative_to(self.vault_path).as_posix().replace(".md", "")
            src_dir = md_file.parent

            try:
                raw_content = md_file.read_text(encoding="utf-8")
                # Remove codigo inline entre crases para nao falsificar links
                clean_content = INLINE_CODE_REGEX.sub("", raw_content)
                matches = WIKILINK_REGEX.findall(clean_content)

                for target, _ in matches:
                    clean_target = target.strip()
                    file_part = clean_target.split("#")[0].strip()

                    # Link interno para secao do proprio documento
                    if not file_part:
                        edges.append((src_node, f"{src_node}#{clean_target.split('#', 1)[1]}"))
                        continue

                    edges.append((src_node, file_part))

                    # 1. Checagem exata no vault
                    if file_part in nodes or file_part.replace(".md", "") in nodes:
                        continue

                    # 2. Checagem relativa ao diretorio de origem no disco
                    resolved_rel = (src_dir / file_part).resolve()
                    if resolved_rel.exists() or resolved_rel.with_suffix(".md").exists():
                        continue

                    # 3. Checagem relativa a raiz do vault
                    resolved_vault = (self.vault_path / file_part).resolve()
                    if resolved_vault.exists() or resolved_vault.with_suffix(".md").exists():
                        continue

                    # 4. Checagem por basename (convencao canônica do Obsidian)
                    stem = Path(file_part).stem
                    if stem in basenames or Path(file_part).name in basenames:
                        continue

                    # Se nenhuma das resolucoes for satisfeita, o link e quebrado
                    broken_links.append((src_node, clean_target))

            except Exception:
                pass

        total_nodes = len(nodes)
        total_edges = len(edges)
        broken_count = len(broken_links)

        summary = f"Graphify audit: {total_nodes} nodes, {total_edges} edges, {broken_count} broken links."
        status = "SUCCESS" if broken_count == 0 else "HOLD"

        metrics = {
            "total_nodes": total_nodes,
            "total_edges": total_edges,
            "broken_links_count": broken_count,
            "broken_links": broken_links
        }

        sha256_hash = hashlib.sha256(summary.encode("utf-8")).hexdigest()

        result = CapabilityExecutionResult(
            capability_id="GRAPHIFY",
            status=status,
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            summary=summary,
            metrics=metrics,
            evidence_sha256=sha256_hash
        )

        return result, metrics
