"""
az000_governance.external.gateway — Gateway Canônico e Unificado de Pontes Externas com Autenticação e Deduplicação.
Garante isolamento de borda, validação HMAC SHA-256 e protocolo estrito FAIL_CLOSED.
"""

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Set

from az000_governance.external.models import (
    ExternalAuthPolicy,
    ExternalChannel,
    ExternalEventPayload,
    ExternalTransmissionResult,
)
from az000_governance.ports.envelope import TypedPortEnvelope, create_port_envelope


class ExternalBridgeGateway:
    """Gateway de borda para eventos externos."""

    def __init__(self):
        self._policies: Dict[ExternalChannel, ExternalAuthPolicy] = {}
        self._seen_event_ids: Set[str] = set()
        self._seen_payload_hashes: Set[str] = set()
        self._register_default_policies()

    def _register_default_policies(self):
        self._policies[ExternalChannel.GITHUB_WEBHOOK] = ExternalAuthPolicy(
            channel=ExternalChannel.GITHUB_WEBHOOK,
            auth_scheme="HMAC_SHA256",
            secret="hangar_github_secret_default",
            require_signature=True
        )
        self._policies[ExternalChannel.GITHUB_PR_RELAY] = ExternalAuthPolicy(
            channel=ExternalChannel.GITHUB_PR_RELAY,
            auth_scheme="TOKEN_BEARER",
            secret="hangar_pr_relay_token",
            require_signature=True
        )
        self._policies[ExternalChannel.TELEGRAM_BOT] = ExternalAuthPolicy(
            channel=ExternalChannel.TELEGRAM_BOT,
            auth_scheme="SECRET_HEADER",
            secret="hangar_telegram_secret",
            require_signature=True
        )
        self._policies[ExternalChannel.CLOUDFLARE_TUNNEL] = ExternalAuthPolicy(
            channel=ExternalChannel.CLOUDFLARE_TUNNEL,
            auth_scheme="CF_HEADER",
            secret="hangar_tunnel_secret",
            require_signature=False
        )
        self._policies[ExternalChannel.BROWSER_BRIDGE] = ExternalAuthPolicy(
            channel=ExternalChannel.BROWSER_BRIDGE,
            auth_scheme="SHARED_SECRET",
            secret="hangar_browser_bridge_token",
            require_signature=False
        )

    def register_policy(self, policy: ExternalAuthPolicy) -> None:
        self._policies[policy.channel] = policy

    def get_policy(self, channel: ExternalChannel) -> Optional[ExternalAuthPolicy]:
        return self._policies.get(channel)

    @staticmethod
    def compute_hmac_sha256(raw_bytes: bytes, secret: str) -> str:
        return hmac.new(secret.encode("utf-8"), raw_bytes, hashlib.sha256).hexdigest()

    @classmethod
    def verify_hmac_sha256(cls, raw_bytes: bytes, secret: str, signature_header: str) -> bool:
        if not secret or not signature_header or not raw_bytes:
            return False
        
        expected_sig = cls.compute_hmac_sha256(raw_bytes, secret)
        clean_sig = signature_header.strip()
        if clean_sig.startswith("sha256="):
            clean_sig = clean_sig[7:]
        
        return hmac.compare_digest(expected_sig, clean_sig)

    def is_duplicate(self, event_id: str, event_hash: str) -> bool:
        return (event_id in self._seen_event_ids) or (event_hash in self._seen_payload_hashes)

    def process_inbound_event(
        self, event: ExternalEventPayload
    ) -> tuple[ExternalTransmissionResult, Optional[TypedPortEnvelope]]:
        """
        Processa e autentica um evento externo.
        Em conformidade com R-DOM-002: FAIL_CLOSED em qualquer inconsistência.
        """
        # Calcular hash canônico do corpo do evento
        serialized_body = json.dumps(event.body, sort_keys=True, separators=(",", ":")).encode("utf-8")
        event_hash = hashlib.sha256(serialized_body).hexdigest()

        # 1. Verificar se canal é autorizado
        policy = self._policies.get(event.channel)
        if not policy:
            return (
                ExternalTransmissionResult(
                    event_id=event.event_id,
                    channel=event.channel,
                    accepted=False,
                    reason="FAIL_CLOSED: Canal externo nao registrado ou nao autorizado.",
                    event_hash=event_hash,
                ),
                None,
            )

        # 2. Verificar autenticação / assinatura se exigida
        if policy.require_signature:
            if policy.auth_scheme == "HMAC_SHA256":
                payload_bytes = event.raw_bytes if event.raw_bytes is not None else serialized_body
                if not self.verify_hmac_sha256(payload_bytes, policy.secret, event.signature):
                    return (
                        ExternalTransmissionResult(
                            event_id=event.event_id,
                            channel=event.channel,
                            accepted=False,
                            reason="FAIL_CLOSED: Assinatura HMAC SHA-256 invalida ou divergente.",
                            event_hash=event_hash,
                        ),
                        None,
                    )
            elif policy.auth_scheme in ("TOKEN_BEARER", "SECRET_HEADER", "SHARED_SECRET"):
                if not hmac.compare_digest(policy.secret, event.signature.strip()):
                    return (
                        ExternalTransmissionResult(
                            event_id=event.event_id,
                            channel=event.channel,
                            accepted=False,
                            reason=f"FAIL_CLOSED: Token de autenticacao invalido para {policy.auth_scheme}.",
                            event_hash=event_hash,
                        ),
                        None,
                    )

        # 3. Deduplicação de eventos
        if self.is_duplicate(event.event_id, event_hash):
            return (
                ExternalTransmissionResult(
                    event_id=event.event_id,
                    channel=event.channel,
                    accepted=False,
                    reason="Deduplicacao de borda: Evento ja recebido e processado anteriormente.",
                    event_hash=event_hash,
                    deduplicated=True,
                ),
                None,
            )

        # 4. Criar envelope tipado Down Plant para entrega interna
        source_addr = f"Hangar_v1/EXTERNAL/{event.channel.value}/INBOUND:P-EXT-INBOUND-01"
        target_addr = "Hangar_v1/GOVERNANCE/INGESTION/DISPATCHER:P-GOV-INGEST-01"
        
        envelope = create_port_envelope(
            source_id=source_addr,
            target=target_addr,
            schema="EXTERNAL_EVENT_INGEST_V1",
            payload={
                "event_id": event.event_id,
                "channel": event.channel.value,
                "source": event.source,
                "body": event.body,
                "authenticated": True,
                "verified_at": datetime.now(timezone.utc).isoformat(),
            },
            evidence_refs=[f"event_hash:{event_hash}"]
        )

        # 5. Registrar no cache de deduplicação
        self._seen_event_ids.add(event.event_id)
        self._seen_payload_hashes.add(event_hash)

        return (
            ExternalTransmissionResult(
                event_id=event.event_id,
                channel=event.channel,
                accepted=True,
                reason="Evento autenticado e envelopado com sucesso.",
                event_hash=event_hash,
                deduplicated=False,
                envelope_ref=envelope.payload_sha256,
            ),
            envelope,
        )


_GLOBAL_EXTERNAL_GATEWAY: Optional[ExternalBridgeGateway] = None


def get_global_external_gateway() -> ExternalBridgeGateway:
    global _GLOBAL_EXTERNAL_GATEWAY
    if _GLOBAL_EXTERNAL_GATEWAY is None:
        _GLOBAL_EXTERNAL_GATEWAY = ExternalBridgeGateway()
    return _GLOBAL_EXTERNAL_GATEWAY
