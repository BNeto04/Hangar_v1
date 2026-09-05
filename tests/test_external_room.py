#!/usr/bin/env python3
"""
test_external_room.py — Suíte de testes unitários para validação do cômodo EXTERNAL (Tier 8).
Garante conformidade com ARCA (R-DOM-002, R-DOM-005, R-DOM-006).
Critérios: "Transportes orientados a eventos comprovados", "Deduplicação e HMAC SHA-256 ativos".
"""

import hashlib
import hmac
import json
import sqlite3
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from az000_governance.arca import (
    get_room_dependencies,
    get_room_order,
)
from az000_governance.external import (
    ExternalAuthPolicy,
    ExternalBridgeGateway,
    ExternalChannel,
    ExternalEventPayload,
    ExternalTransmissionResult,
    get_global_external_gateway,
)
from az000_governance.plant.addressing import validate_down_plant_address


class TestExternalRoom(unittest.TestCase):

    def setUp(self):
        self.gateway = ExternalBridgeGateway()

    def test_01_arca_canonical_dependencies(self):
        """Valida se o cômodo EXTERNAL está registrado na ARCA com dependências estritas."""
        rooms = get_room_order()
        ext_room = next((r for r in rooms if r.room_name == "EXTERNAL"), None)
        self.assertIsNotNone(ext_room, "Cômodo EXTERNAL deve existir na ARCA.")
        self.assertEqual(ext_room.tier, 8)
        self.assertIn("PORTS", ext_room.dependencies)
        self.assertIn("INTELLIGENCE", ext_room.dependencies)
        self.assertIn("Transportes orientados a eventos comprovados", ext_room.closure_criteria)
        self.assertIn("Deduplicação e HMAC SHA-256 ativos", ext_room.closure_criteria)

    def test_02_hmac_sha256_verification(self):
        """Valida computação e verificação precisa de assinatura HMAC SHA-256."""
        secret = "super_secret_webhook_key"
        payload_bytes = b'{"action": "opened", "number": 1}'
        
        expected_sig = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
        
        # Testar assinatura com prefixo sha256=
        self.assertTrue(
            ExternalBridgeGateway.verify_hmac_sha256(payload_bytes, secret, f"sha256={expected_sig}")
        )
        # Testar assinatura direta
        self.assertTrue(
            ExternalBridgeGateway.verify_hmac_sha256(payload_bytes, secret, expected_sig)
        )
        # Testar assinatura inválida
        self.assertFalse(
            ExternalBridgeGateway.verify_hmac_sha256(payload_bytes, secret, "sha256=invalid_signature")
        )
        # Testar segredo vazio
        self.assertFalse(
            ExternalBridgeGateway.verify_hmac_sha256(payload_bytes, "", expected_sig)
        )

    def test_03_fail_closed_on_invalid_auth(self):
        """R-DOM-002: Invariante FAIL_CLOSED diante de assinatura ou credencial inválida."""
        policy = ExternalAuthPolicy(
            channel=ExternalChannel.GITHUB_WEBHOOK,
            auth_scheme="HMAC_SHA256",
            secret="secure_secret_123",
            require_signature=True
        )
        self.gateway.register_policy(policy)

        # Evento com assinatura falsa
        event = ExternalEventPayload(
            event_id="EVT-001",
            channel=ExternalChannel.GITHUB_WEBHOOK,
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            source="github.com",
            signature="sha256=corrupted_sig",
            body={"event": "ping"}
        )

        res, env = self.gateway.process_inbound_event(event)
        self.assertFalse(res.accepted)
        self.assertIn("FAIL_CLOSED", res.reason)
        self.assertIsNone(env)

    def test_04_event_deduplication(self):
        """Valida que eventos duplicados são descartados na borda."""
        policy = ExternalAuthPolicy(
            channel=ExternalChannel.TELEGRAM_BOT,
            auth_scheme="SECRET_HEADER",
            secret="telegram_token_xyz",
            require_signature=True
        )
        self.gateway.register_policy(policy)

        event = ExternalEventPayload(
            event_id="EVT-TG-100",
            channel=ExternalChannel.TELEGRAM_BOT,
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            source="telegram",
            signature="telegram_token_xyz",
            body={"text": "/status", "chat_id": 12345}
        )

        # Primeira transmissão: aceita
        res1, env1 = self.gateway.process_inbound_event(event)
        self.assertTrue(res1.accepted)
        self.assertFalse(res1.deduplicated)
        self.assertIsNotNone(env1)

        # Segunda transmissão idêntica: deduplicada
        res2, env2 = self.gateway.process_inbound_event(event)
        self.assertFalse(res2.accepted)
        self.assertTrue(res2.deduplicated)
        self.assertIn("Deduplicacao", res2.reason)
        self.assertIsNone(env2)

    def test_05_successful_ingestion_and_envelope_generation(self):
        """Valida geração de envelope Down Plant tipado após autenticação bem-sucedida."""
        secret = "pr_relay_secret"
        policy = ExternalAuthPolicy(
            channel=ExternalChannel.GITHUB_PR_RELAY,
            auth_scheme="TOKEN_BEARER",
            secret=secret,
            require_signature=True
        )
        self.gateway.register_policy(policy)

        event = ExternalEventPayload(
            event_id="EVT-PR-999",
            channel=ExternalChannel.GITHUB_PR_RELAY,
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            source="github_pr_1",
            signature=secret,
            body={"pr": 1, "comment_id": "CG-000138", "action": "audit_call"}
        )

        res, env = self.gateway.process_inbound_event(event)
        self.assertTrue(res.accepted)
        self.assertIsNotNone(env)
        self.assertEqual(env.schema, "EXTERNAL_EVENT_INGEST_V1")
        self.assertTrue(validate_down_plant_address(env.source_id))
        self.assertTrue(validate_down_plant_address(env.target))
        self.assertEqual(env.payload["event_id"], "EVT-PR-999")
        self.assertTrue(env.payload["authenticated"])

    def test_06_unregistered_channel_fail_closed_and_next_order(self):
        """Canais não registrados são rejeitados imediatamente e próximo cômodo é TRACE."""
        empty_gateway = ExternalBridgeGateway()
        empty_gateway._policies.clear()

        event = ExternalEventPayload(
            event_id="EVT-ROGUE-001",
            channel=ExternalChannel.CLOUDFLARE_TUNNEL,
            timestamp_iso=datetime.now(timezone.utc).isoformat(),
            source="unknown_host",
            signature="none",
            body={"command": "eval"}
        )

        res, env = empty_gateway.process_inbound_event(event)
        self.assertFalse(res.accepted)
        self.assertIn("FAIL_CLOSED", res.reason)
        self.assertIsNone(env)

        # Verificar ordem topológica para o próximo cômodo
        rooms = get_room_order()
        ext_idx = next(i for i, r in enumerate(rooms) if r.room_name == "EXTERNAL")
        self.assertEqual(ext_idx, 7)  # Oitavo cômodo (Tier 8)

        next_room = rooms[ext_idx + 1]
        self.assertEqual(next_room.room_name, "TRACE", "O próximo cômodo na ordem deve ser TRACE.")
        self.assertEqual(next_room.tier, 9)


if __name__ == "__main__":
    unittest.main()
