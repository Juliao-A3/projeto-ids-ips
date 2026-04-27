import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

interfaces = [item.strip() for item in os.getenv("SNIFFER_INTERFACES", "eth0").split(",") if item.strip()]
if not interfaces:
    raise SystemExit("Nenhuma interface informada em SNIFFER_INTERFACES")

cloud_url = str(os.getenv("CLOUD_URL") or "").strip().rstrip("/")
flow_endpoint = (
    os.getenv("SNIFFER_FLOW_ENDPOINT")
    or os.getenv("FLOW_ENDPOINT")
    or (f"{cloud_url}/sniffer/flow-input" if cloud_url else None)
    or "http://127.0.0.1:8000/sniffer/flow-input"
)
expired_update = os.getenv("SNIFFER_EXPIRED_UPDATE", "1.0")
packets_per_gc = os.getenv("SNIFFER_PACKETS_PER_GC", "50")
verbose = os.getenv("SNIFFER_VERBOSE", "0") == "1"
heartbeat_seconds = max(5, int(os.getenv("SNIFFER_HEARTBEAT_SECONDS", "15")))
restart_delay_seconds = max(1, int(os.getenv("SNIFFER_RESTART_DELAY_SECONDS", "2")))

processes: dict[str, subprocess.Popen] = {}
reader_threads: dict[str, threading.Thread] = {}


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


def _stream_output(interface: str, process: subprocess.Popen) -> None:
    if process.stdout is None:
        return

    for line in process.stdout:
        text = line.rstrip()
        if text:
            print(f"[sniffer:{interface}] {text}", flush=True)


def _start_interface(interface: str) -> None:
    command = _build_command(interface)
    print(f"[sniffer] Iniciando interface={interface} endpoint={flow_endpoint}", flush=True)
    print(f"[sniffer] CMD[{interface}]: {' '.join(command)}", flush=True)

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    processes[interface] = process

    reader = threading.Thread(
        target=_stream_output,
        args=(interface, process),
        daemon=True,
        name=f"sniffer-log-reader-{interface}",
    )
    reader.start()
    reader_threads[interface] = reader


def _terminate(*_args):
    for process in processes.values():
        if process.poll() is None:
            process.terminate()
    deadline = time.time() + 5
    for process in processes.values():
        while process.poll() is None and time.time() < deadline:
            time.sleep(0.1)
        if process.poll() is None:
            process.kill()


signal.signal(signal.SIGTERM, _terminate)
signal.signal(signal.SIGINT, _terminate)

for interface in interfaces:
    _start_interface(interface)

try:
    last_heartbeat = 0.0
    while True:
        for interface in interfaces:
            process = processes.get(interface)
            if process is None:
                continue
            exit_code = process.poll()
            if exit_code is not None:
                print(
                    f"[sniffer] Processo da interface={interface} saiu com code={exit_code}; reiniciando em {restart_delay_seconds}s",
                    flush=True,
                )
                time.sleep(restart_delay_seconds)
                _start_interface(interface)

        alive = [process for process in processes.values() if process.poll() is None]

        now = time.time()
        if now - last_heartbeat >= heartbeat_seconds:
            print(
                f"[sniffer] alive={len(alive)}/{len(processes)} interfaces={','.join(interfaces)} endpoint={flow_endpoint}",
                flush=True,
            )
            last_heartbeat = now
        time.sleep(1)
finally:
    _terminate()
