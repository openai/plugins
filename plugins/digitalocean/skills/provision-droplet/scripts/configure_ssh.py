#!/usr/bin/env python3
"""Configure local SSH access for a freshly provisioned DigitalOcean droplet.

Steps:
  1. Render ssh_config.tmpl and append a Host block to ~/.ssh/config.
  2. Refresh ~/.ssh/known_hosts via ssh-keyscan (20 retries x 10s).
  3. Probe with a real SSH login until cloud-init is done (42 retries x 10s).
  4. Print Codex remote-workspace handoff instructions.

Uses only the Python standard library — no pip install required.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import threading
import time
from pathlib import Path


# --------------------------------------------------------------------------- #
# Heartbeat thread
# --------------------------------------------------------------------------- #
class HeartbeatThread(threading.Thread):
    def __init__(self, interval: int = 5):
        super().__init__(daemon=True)
        self._interval = interval
        self._stop_event = threading.Event()
        self._status = "working..."
        self._lock = threading.Lock()
        self._start_time = time.monotonic()

    def set_status(self, msg: str) -> None:
        with self._lock:
            self._status = msg

    def stop(self) -> None:
        self._stop_event.set()
        self.join()

    def run(self) -> None:
        while not self._stop_event.wait(timeout=self._interval):
            elapsed = int(time.monotonic() - self._start_time)
            with self._lock:
                msg = self._status
            print(f"⏳ [{elapsed}s] {msg}", flush=True)


# --------------------------------------------------------------------------- #
# SSH config
# --------------------------------------------------------------------------- #
def write_ssh_config(template_path: Path, alias: str, ip: str, user: str,
                     identity: Path, config_path: Path) -> None:
    tmpl = template_path.read_text()
    block = (tmpl
             .replace("{{ALIAS}}", alias)
             .replace("{{IP}}", ip)
             .replace("{{USER}}", user)
             .replace("{{IDENTITY_FILE}}", str(identity)))
    config_path.parent.mkdir(parents=True, exist_ok=True)
    existing = config_path.read_text() if config_path.exists() else ""
    if f"Host {alias}\n" in existing or f"Host {alias} " in existing:
        print(f"~/.ssh/config already has 'Host {alias}'; leaving it untouched.", flush=True)
        return
    with config_path.open("a") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write("\n" + block.rstrip() + "\n")
    config_path.chmod(0o600)
    print(f"Appended SSH config block for '{alias}' to {config_path}.", flush=True)


# --------------------------------------------------------------------------- #
# known_hosts
# --------------------------------------------------------------------------- #
def update_known_hosts(ip: str, known_hosts: Path,
                       heartbeat: HeartbeatThread,
                       tries: int = 20, delay: int = 10) -> None:
    known_hosts.parent.mkdir(parents=True, exist_ok=True)
    known_hosts.touch(exist_ok=True)
    subprocess.run(["ssh-keygen", "-R", ip, "-f", str(known_hosts)],
                   capture_output=True)
    for attempt in range(1, tries + 1):
        heartbeat.set_status(f"Scanning SSH host keys (attempt {attempt}/{tries})...")
        scan = subprocess.run(["ssh-keyscan", "-T", "10", "-H", ip],
                              capture_output=True, text=True)
        if scan.stdout.strip():
            with known_hosts.open("a") as f:
                f.write(scan.stdout)
            print(f"Added host keys for {ip} to {known_hosts}.", flush=True)
            return
        time.sleep(delay)
    print(f"WARNING: ssh-keyscan never got a key from {ip}. "
          "Run it manually once the droplet finishes booting.", flush=True)


# --------------------------------------------------------------------------- #
# SSH login probe
# --------------------------------------------------------------------------- #
def wait_for_ssh_login(ip: str, user: str, key_path: Path,
                       heartbeat: HeartbeatThread,
                       tries: int = 42, delay: int = 10) -> bool:
    cmd = [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=10",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "IdentitiesOnly=yes",
        "-i", str(key_path),
        f"{user}@{ip}",
        "echo", "ok",
    ]
    for attempt in range(1, tries + 1):
        heartbeat.set_status(f"Probing SSH login (attempt {attempt}/{tries})...")
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode == 0:
            print("SSH login succeeded. Droplet is fully ready.", flush=True)
            return True
        if attempt < tries:
            time.sleep(delay)
    print(
        f"WARNING: SSH login never succeeded after {tries} attempts. "
        "The droplet may still be finishing cloud-init. "
        "Proceeding — Codex will connect once it is ready.", flush=True
    )
    return False


# --------------------------------------------------------------------------- #
# Codex handoff
# --------------------------------------------------------------------------- #
def codex_handoff(alias: str, remote_path: str) -> None:
    print("\n" + "=" * 64, flush=True)
    print("DROPLET READY. To use it as a Codex remote workspace:", flush=True)
    print("=" * 64, flush=True)
    print(f"""
The host '{alias}' is now in ~/.ssh/config, so the Codex App detects it
automatically. Add it as a remote project:

  Codex App  ->  Settings  ->  Connections  ->  Add SSH Host
             ->  pick '{alias}'  ->  remote folder: {remote_path}

Codex installs its app-server over SSH on connect, so make sure the CLI is
present on the droplet (the app will offer to install it, or run once):

  ssh {alias} 'curl -fsSL https://chatgpt.com/codex/install.sh | CODEX_NON_INTERACTIVE=1 sh'

NOTE: there is currently no supported CLI to register a desktop remote project
from automation (openai/codex#21554 is open). The one click above is the
supported path.
""", flush=True)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> None:
    p = argparse.ArgumentParser(
        description="Configure local SSH access for a provisioned DO droplet."
    )
    p.add_argument("--alias",       required=True,  help="SSH Host alias")
    p.add_argument("--ip",          required=True,  help="Droplet public IP")
    p.add_argument("--user",        default="root", help="SSH login user (default root)")
    p.add_argument("--key-path",    required=True,  help="Path to private key")
    p.add_argument("--ssh-template", default=None,  help="Path to ssh_config.tmpl")
    p.add_argument("--ssh-config",  default="~/.ssh/config")
    p.add_argument("--known-hosts", default="~/.ssh/known_hosts")
    p.add_argument("--remote-path", default="/root/workspace",
                   help="Remote project folder for Codex")
    p.add_argument("--emit-codex-state", action="store_true",
                   help="Print the UNSUPPORTED Codex global-state snippet")
    args = p.parse_args()

    key_path    = Path(args.key_path).expanduser()
    ssh_config  = Path(args.ssh_config).expanduser()
    known_hosts = Path(args.known_hosts).expanduser()
    template    = (Path(args.ssh_template).expanduser() if args.ssh_template
                   else Path(__file__).resolve().parent.parent / "ssh_config.tmpl")

    heartbeat = HeartbeatThread(interval=5)
    heartbeat.start()

    try:
        heartbeat.set_status("Writing ~/.ssh/config entry...")
        write_ssh_config(template, args.alias, args.ip, args.user,
                         key_path, ssh_config)

        update_known_hosts(args.ip, known_hosts, heartbeat)
        wait_for_ssh_login(args.ip, args.user, key_path, heartbeat)

    except Exception:
        heartbeat.stop()
        raise

    heartbeat.stop()
    codex_handoff(args.alias, args.remote_path)


if __name__ == "__main__":
    main()
