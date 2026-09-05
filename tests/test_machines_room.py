import unittest
import sqlite3
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from az000_governance.machines import (
    FiniteStateMachine,
    StateTransition,
    MachineState,
    NM_OBS_01_VaultAuditor,
    NM_EXEC_01_TaskAutomata,
)
from az000_governance.arca import (
    get_room_dependencies,
    get_room_order,
)


class TestMachinesRoom(unittest.TestCase):
    def setUp(self):
        self.fsm = FiniteStateMachine("TEST_FSM", initial_state="INITIAL")
        self.fsm.add_transition("INITIAL", "BOOT", "READY")
        self.fsm.add_transition("READY", "START", "RUNNING")
        self.fsm.add_transition("RUNNING", "COMPLETE", "DONE")

    def test_01_fsm_pure_state_transitions(self):
        s1 = self.fsm.trigger("BOOT")
        self.assertEqual(s1, "READY")
        self.assertEqual(self.fsm.current_state, "READY")

        s2 = self.fsm.trigger("START")
        self.assertEqual(s2, "RUNNING")

        s3 = self.fsm.trigger("COMPLETE")
        self.assertEqual(s3, "DONE")

        history = self.fsm.get_history()
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0], ("INITIAL", "BOOT", "READY"))
        self.assertEqual(history[1], ("READY", "START", "RUNNING"))
        self.assertEqual(history[2], ("RUNNING", "COMPLETE", "DONE"))

    def test_02_fsm_fail_closed_on_illegal_event(self):
        # Disparar evento ilegal no estado INITIAL deve falhar fechado em HOLD
        with self.assertRaises(PermissionError) as ctx:
            self.fsm.trigger("ILLEGAL_EVENT")
        
        self.assertIn("FAIL_CLOSED", str(ctx.exception))
        self.assertEqual(self.fsm.current_state, "HOLD")

    def test_03_fsm_fail_closed_on_guard_failure(self):
        guard_allowed = False
        def guard_fn():
            return guard_allowed

        self.fsm.add_transition("INITIAL", "GATED_STEP", "READY", guard="guard_fn")

        with self.assertRaises(PermissionError) as ctx:
            self.fsm.trigger("GATED_STEP", guard_fn=guard_fn)

        self.assertIn("Guarda falhou", str(ctx.exception))
        self.assertEqual(self.fsm.current_state, "HOLD")

    def test_04_nano_machines_execution(self):
        # 1. NM_OBS_01_VaultAuditor
        nm_obs = NM_OBS_01_VaultAuditor()
        out_obs = nm_obs.execute({"vault_path": str(REPO_ROOT / "vault")})
        self.assertEqual(out_obs.machine_id, "NM-OBS-01")
        self.assertEqual(out_obs.status, "SUCCESS")
        self.assertEqual(len(out_obs.output_sha256), 64)

        # 2. NM_EXEC_01_TaskAutomata
        nm_exec = NM_EXEC_01_TaskAutomata()
        out_exec = nm_exec.execute({"event": "DISPATCH"})
        self.assertEqual(out_exec.machine_id, "NM-EXEC-01")
        self.assertEqual(out_exec.status, "RUNNING")
        self.assertEqual(len(out_exec.output_sha256), 64)

    def test_05_upstream_dependencies_governance_to_capabilities_complete(self):
        db_path = Path(r"C:\Users\PICHAU\AppData\Local\hermes\kanban.db")
        self.assertTrue(db_path.exists())
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        tasks_to_check = [
            "t_hangar_az000_intent_seal_ingestion_01",
            "t_hangar_world_room_completion_01",
            "t_hangar_plant_room_completion_01",
            "t_hangar_ports_room_completion_01",
            "t_hangar_capabilities_room_completion_01",
        ]

        for tid in tasks_to_check:
            cur.execute("SELECT id, status FROM tasks WHERE id = ?", (tid,))
            row = cur.fetchone()
            self.assertIsNotNone(row, f"Card '{tid}' deve existir no Hermes Kanban.")
            self.assertEqual(row[1], "done", f"Card '{tid}' deve estar 'done'.")

        conn.close()

    def test_06_machines_index_and_spec_reference_arca_and_next_room(self):
        index_file = REPO_ROOT / "vault" / "MACHINES" / "INDEX.md"
        spec_file = REPO_ROOT / "DOCS" / "26_MACHINES_ROOM_SPEC.md"

        self.assertTrue(index_file.exists())
        self.assertTrue(spec_file.exists())

        idx_text = index_file.read_text(encoding="utf-8")
        spec_text = spec_file.read_text(encoding="utf-8")

        self.assertIn("R-DOM-005", idx_text)
        self.assertIn("R-DOM-006", idx_text)
        self.assertIn("R-DOM-005", spec_text)
        self.assertIn("R-DOM-006", spec_text)

        rooms = get_room_order()
        mach_idx = next(i for i, r in enumerate(rooms) if r.room_name == "MACHINES")
        self.assertEqual(mach_idx, 5)  # Sexto comodo (Tier 6)

        next_room = rooms[mach_idx + 1]
        self.assertEqual(next_room.room_name, "INTELLIGENCE", "O proximo comodo na ordem deve ser INTELLIGENCE.")
        self.assertEqual(next_room.tier, 7)


if __name__ == "__main__":
    unittest.main()
