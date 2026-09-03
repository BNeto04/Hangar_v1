#!/usr/bin/env python3
"""
AUTOWAKE-RECEIVER v2: Turn Trigger Adapter (Porta P-CODEX-AG-AUTOWAKE-01).

Strategy: EXIT-ON-DETECT.
When a new CALL appears in the watched file, the receiver prints structured
evidence to stdout and TERMINATES. The Antigravity runtime detects the
background task completion ("Task finished") and starts a new inference turn.
The agent then reads the CALL directly from the file.

This receiver does NOT:
- Call send-message or any LLM API
- Interpret or execute the CALL content
- Relaunch itself
"""

import argparse
import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

LOG = logging.getLogger("autowake-receiver")


class LockError(Exception):
    """Raised when another receiver instance is already running."""
    pass


class ConfigError(Exception):
    """Raised when configuration is invalid."""
    pass


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Autowake Receiver v2 - Turn Trigger Adapter"
    )
    p.add_argument("--root", required=True, help="Circuito root directory")
    p.add_argument("--watch", default="conversa de ia.txt",
                   help="Filename to watch inside root")
    p.add_argument("--poll-interval", type=float, default=5.0,
                   help="Seconds between polls (default: 5.0)")
    p.add_argument("--timeout", type=float, default=0,
                   help="Max seconds to wait, 0=unlimited (default: 0)")
    return p.parse_args(argv)


def compute_signature(filepath: Path) -> Optional[dict]:
    if not filepath.exists():
        return None
    try:
        data = filepath.read_bytes()
    except OSError as exc:
        LOG.warning("Cannot read %s: %s", filepath, exc)
        return None
    if not data.strip():
        return None
    sha = hashlib.sha256(data).hexdigest()
    text = data.decode("utf-8", errors="replace")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    header = lines[0] if lines else ""
    return {"sha": sha, "header": header, "size": len(data)}


def load_notified(state_path: Path) -> dict:
    if state_path.exists():
        try:
            return json.loads(state_path.read_text("utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            LOG.warning("Corrupt state file %s: %s", state_path, exc)
            return {}
    return {}


def save_notified(state_path: Path, state: dict) -> None:
    tmp = state_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2), "utf-8")
    tmp.replace(state_path)


def _is_pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid
            )
            if handle:
                kernel32.CloseHandle(handle)
                return True
            return False
        except (AttributeError, OSError):
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True


def acquire_lock(lock_path: Path) -> None:
    if lock_path.exists():
        try:
            stored_pid = int(lock_path.read_text("utf-8").strip())
        except (ValueError, OSError):
            stored_pid = -1
        if _is_pid_alive(stored_pid):
            raise LockError(
                f"Another receiver instance is running (PID {stored_pid}, "
                f"lock={lock_path})"
            )
        LOG.info("Stale lock for PID %d - taking over", stored_pid)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path.write_text(str(os.getpid()), "utf-8")


def release_lock(lock_path: Path) -> None:
    try:
        if lock_path.exists():
            stored = lock_path.read_text("utf-8").strip()
            if stored == str(os.getpid()):
                lock_path.unlink()
    except OSError as exc:
        LOG.warning("Could not release lock: %s", exc)


def main(argv=None):
    args = parse_args(argv)

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        stream=sys.stderr,
    )

    root = Path(args.root)
    if not root.is_dir():
        raise ConfigError(f"Root directory does not exist: {root}")

    watch_path = root / args.watch
    lock_path = root / "runtime" / ".autowake.lock"
    state_path = root / ".autowake_notified.json"

    acquire_lock(lock_path)

    try:
        print("AUTOWAKE_RECEIVER_V2_INITIALIZED", flush=True)
        LOG.info("Watching: %s (poll=%.1fs, timeout=%.0fs)",
                 watch_path, args.poll_interval, args.timeout)

        current = compute_signature(watch_path)
        state = load_notified(state_path)
        if current and current["sha"] not in state:
            state[current["sha"]] = {
                "header": current["header"],
                "seen_at": time.time(),
                "bootstrapped": True,
            }
            save_notified(state_path, state)
            LOG.info("Bootstrapped existing CALL: %s (sha=%s)",
                     current["header"], current["sha"][:12])

        start_time = time.time()

        while True:
            if args.timeout > 0 and (time.time() - start_time) > args.timeout:
                print("AUTOWAKE_TIMEOUT", flush=True)
                LOG.info("Timeout reached (%.0fs), exiting without detection",
                         args.timeout)
                sys.exit(2)

            sig = compute_signature(watch_path)
            if sig:
                state = load_notified(state_path)
                if sig["sha"] not in state:
                    detected_at = time.time()
                    state[sig["sha"]] = {
                        "header": sig["header"],
                        "detected_at": detected_at,
                        "bootstrapped": False,
                    }
                    save_notified(state_path, state)

                    print("WAKE_CALL_DETECTED", flush=True)
                    print(f"CALL_HEADER={sig['header']}", flush=True)
                    print(f"CALL_SHA256={sig['sha']}", flush=True)
                    print(f"CALL_SIZE={sig['size']}", flush=True)
                    print(f"DETECTED_AT={detected_at}", flush=True)
                    LOG.info("New CALL detected: %s (sha=%s)",
                             sig["header"], sig["sha"][:12])

                    sys.exit(0)

            time.sleep(args.poll_interval)

    finally:
        release_lock(lock_path)


if __name__ == "__main__":
    main()
