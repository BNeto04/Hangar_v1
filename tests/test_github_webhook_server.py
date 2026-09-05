#!/usr/bin/env python3
"""
test_github_webhook_server.py — Suíte unitária determinística do GitHub Webhook Receiver.
Valida: HMAC SHA-256 fail-closed, filtragem estrita de TYPE: CALL da PR #1, dedupe e health.
"""

import hashlib
import hmac
import json
import threading
import time
import unittest
import urllib.request
import urllib.error
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import bridge.github_webhook_server as gws

TEST_SECRET = "test_secret_hangar_v1_webhook_12345"
TEST_PORT = 18766

class TestGitHubWebhookServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = gws.create_server("127.0.0.1", TEST_PORT, secret=TEST_SECRET)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _sign(self, data_bytes: bytes, secret: str = TEST_SECRET) -> str:
        return "sha256=" + hmac.new(secret.encode("utf-8"), data_bytes, hashlib.sha256).hexdigest()

    def _post(self, payload: dict, event: str = "issue_comment", delivery_id: str = "deliv-001", signature: str = None):
        data = json.dumps(payload).encode("utf-8")
        if signature is None:
            sig = self._sign(data)
        else:
            sig = signature

        headers = {
            "Content-Type": "application/json",
            "X-GitHub-Event": event,
            "X-GitHub-Delivery": delivery_id,
        }
        if sig:
            headers["X-Hub-Signature-256"] = sig

        req = urllib.request.Request(f"http://127.0.0.1:{TEST_PORT}/github-webhook", data=data, headers=headers)
        return urllib.request.urlopen(req, timeout=5)

    def test_01_health_endpoint(self):
        req = urllib.request.Request(f"http://127.0.0.1:{TEST_PORT}/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "healthy")

    def test_02_invalid_hmac_rejected(self):
        payload = {"action": "created", "issue": {"number": 1}, "comment": {"id": 101, "body": "TYPE: CALL"}}
        data = json.dumps(payload).encode("utf-8")
        bad_sig = "sha256=0000000000000000000000000000000000000000000000000000000000000000"
        
        req = urllib.request.Request(
            f"http://127.0.0.1:{TEST_PORT}/github-webhook",
            data=data,
            headers={
                "Content-Type": "application/json",
                "X-GitHub-Event": "issue_comment",
                "X-GitHub-Delivery": "deliv-bad-sig",
                "X-Hub-Signature-256": bad_sig
            }
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req, timeout=5)
        self.assertEqual(ctx.exception.code, 401)

    def test_03_ping_event_accepted(self):
        with self._post({"zen": "Design for failure."}, event="ping", delivery_id="deliv-ping") as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("msg"), "pong")

    def test_04_ignored_non_issue_comment_event(self):
        with self._post({"ref": "refs/heads/main"}, event="push", delivery_id="deliv-push") as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("Ignored", data.get("msg", ""))

    def test_05_ignored_wrong_issue(self):
        payload = {"action": "created", "issue": {"number": 99}, "comment": {"id": 201, "body": "TYPE: CALL"}}
        with self._post(payload, delivery_id="deliv-issue-99") as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("Ignored", data.get("msg", ""))

    def test_06_ignored_no_call(self):
        payload = {"action": "created", "issue": {"number": 1}, "comment": {"id": 301, "body": "Just a normal discussion comment."}}
        with self._post(payload, delivery_id="deliv-no-call") as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("Ignored", data.get("msg", ""))

    def test_07_valid_call_accepted_and_dispatched(self):
        comment_id = int(time.time() * 1000)
        payload = {
            "action": "created",
            "issue": {"number": 1},
            "comment": {
                "id": comment_id,
                "body": "CG-000126\nTYPE: CALL\nTO: ANTIGRAVITY\nCALL_ID: CALL-TEST-WEBHOOK-001\nACTION: RUN"
            }
        }
        with self._post(payload, delivery_id=f"deliv-valid-{comment_id}") as resp:
            self.assertEqual(resp.status, 202)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data.get("status"), "accepted")
            self.assertTrue(data.get("dispatched"))

    def test_08_strict_dedupe_duplicate_call(self):
        comment_id = int(time.time() * 1000) + 777
        delivery_id = f"deliv-dedupe-{comment_id}"
        payload = {
            "action": "created",
            "issue": {"number": 1},
            "comment": {
                "id": comment_id,
                "body": "CG-000126\nTYPE: CALL\nCALL_ID: CALL-TEST-DEDUPE"
            }
        }
        # Primeira entrega: aceita
        with self._post(payload, delivery_id=delivery_id) as resp1:
            self.assertEqual(resp1.status, 202)

        # Segunda entrega (mesmo delivery_id e comment_id): deduplicada com 200
        with self._post(payload, delivery_id=delivery_id) as resp2:
            self.assertEqual(resp2.status, 200)
            data = json.loads(resp2.read().decode("utf-8"))
            self.assertIn("Duplicate", data.get("msg", ""))

if __name__ == "__main__":
    unittest.main()
