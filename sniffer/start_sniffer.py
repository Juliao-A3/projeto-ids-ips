import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

interfaces = [item.strip() for item in os.getenv("SNIFFER_INTERFACES", "eth0").split(",") if item.strip()]
if not interfaces:
    raise SystemExit("Nenhuma interface informada em SNIFFER_INTERFACES")

flow_endpoint = (
    os.getenv("SNIFFER_FLOW_ENDPOINT")
    or os.getenv("FLOW_ENDPOINT")
    or "http://127.0.0.1:8000/sniffer/flow-input"
)
expired_update = os.getenv("SNIFFER_EXPIRED_UPDATE", "1.0")
packets_per_gc = os.getenv("SNIFFER_PACKETS_PER_GC", "50")
verbose = os.getenv("SNIFFER_VERBOSE", "0") == "1"

processes: list[subprocess.Popen] = []


def _build_command(interface: str) -> list[str]:
    command = [
        sys.executable,
        "-m",
        "backend.scapy_module.cicflow_fast",
        "--interface",
        interface,
        "--url",
        f"{flow_endpoint}?interface={quote(interface, safe='')}",
        "--expired-update",
        expired_update,
        "--packets-per-gc",
        packets_per_gc,
    ]
    if verbose:
        command.append("--verbose")
    return command


def _terminate(*_args):
    for process in processes:
        if process.poll() is None:
            process.terminate()
    deadline = time.time() + 5
    for process in processes:
        while process.poll() is None and time.time() < deadline:
            time.sleep(0.1)
        if process.poll() is None:
            process.kill()


signal.signal(signal.SIGTERM, _terminate)
signal.signal(signal.SIGINT, _terminate)

for interface in interfaces:
    command = _build_command(interface)
    print(f"[sniffer] Iniciando: {' '.join(command)}")
    processes.append(
        subprocess.Popen(command)
    )

try:
    while True:
        alive = [process for process in processes if process.poll() is None]
        if not alive:
            break
        time.sleep(1)
finally:
    _terminate()
