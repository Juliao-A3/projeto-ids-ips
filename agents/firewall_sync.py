import ipaddress
import os
import shutil
import signal
import subprocess
import sys
import time
from typing import Optional

import httpx


def _env_int(name: str, default: int) -> int:
    try:
        return max(1, int(os.getenv(name, str(default))))
    except (TypeError, ValueError):
        return default


def _env_float(name: str, default: float) -> float:
    try:
        value = float(os.getenv(name, str(default)))
        return default if value != value else max(0.1, value)
    except (TypeError, ValueError):
        return default


def _is_valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(str(value).strip())
        return True
    except ValueError:
        return False


def _detect_firewall_cmd() -> Optional[str]:
    for candidate in ("iptables", "iptables-nft", "iptables-legacy"):
        if shutil.which(candidate):
            return candidate
    return None


def _run_command(args: list[str]) -> bool:
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    return result.returncode == 0


def _ensure_rule(firewall_cmd: str, chain: str, option: str, ip: str, action: str) -> bool:
    check_cmd = [firewall_cmd, "-C", chain, option, ip, "-j", action]
    insert_cmd = [firewall_cmd, "-I", chain, option, ip, "-j", action]
    if _run_command(check_cmd):
        return True
    return _run_command(insert_cmd)


def _remove_rule(firewall_cmd: str, chain: str, option: str, ip: str, action: str) -> bool:
    removed_any = False
    while _run_command([firewall_cmd, "-C", chain, option, ip, "-j", action]):
        _run_command([firewall_cmd, "-D", chain, option, ip, "-j", action])
        removed_any = True
    return removed_any


def _apply_block(firewall_cmd: str, ip: str) -> bool:
    added_in = _ensure_rule(firewall_cmd, "INPUT", "-s", ip, "DROP")
    added_out = _ensure_rule(firewall_cmd, "OUTPUT", "-d", ip, "DROP")
    return added_in or added_out


def _apply_unblock(firewall_cmd: str, ip: str) -> bool:
    removed_in = _remove_rule(firewall_cmd, "INPUT", "-s", ip, "DROP")
    removed_out = _remove_rule(firewall_cmd, "OUTPUT", "-d", ip, "DROP")
    return removed_in or removed_out


def _fetch_blocked_ips(base_url: str, token: str, timeout_seconds: float) -> set[str]:
    response = httpx.get(
        f"{base_url}/api/agent/bloqueios",
        headers={"X-Agent-Token": token},
        timeout=timeout_seconds,
    )
    response.raise_for_status()

    payload = response.json()
    blocked_ips: set[str] = set()
    if not isinstance(payload, list):
        return blocked_ips

    for item in payload:
        if not isinstance(item, dict):
            continue
        ip = str(item.get("ip_bloqueado", "")).strip()
        if ip and _is_valid_ip(ip):
            blocked_ips.add(ip)
    return blocked_ips


def main() -> int:
    cloud_url = (os.getenv("CLOUD_URL") or "http://127.0.0.1:8000").rstrip("/")
    agent_token = str(os.getenv("AGENT_TOKEN") or "").strip()
    poll_seconds = _env_int("AGENT_POLL_SECONDS", 10)
    timeout_seconds = _env_float("AGENT_HTTP_TIMEOUT", 10.0)

    if not agent_token:
        print("[AGENT] AGENT_TOKEN não definido.", file=sys.stderr)
        return 1

    firewall_cmd = _detect_firewall_cmd()
    if not firewall_cmd:
        print("[AGENT] Nenhum comando de firewall encontrado.", file=sys.stderr)
        return 1

    def _stop(*_args):
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _stop)
    signal.signal(signal.SIGINT, _stop)

    applied_ips: set[str] = set()
    print(f"[AGENT] firewall-sync ativo | cloud={cloud_url} | firewall={firewall_cmd}", flush=True)

    while True:
        try:
            cloud_ips = _fetch_blocked_ips(cloud_url, agent_token, timeout_seconds)
            next_applied: set[str] = set()

            for ip in sorted(cloud_ips - applied_ips):
                if _apply_block(firewall_cmd, ip):
                    print(f"[AGENT] IP bloqueado localmente: {ip}", flush=True)
                    next_applied.add(ip)

            for ip in sorted(applied_ips - cloud_ips):
                if _apply_unblock(firewall_cmd, ip):
                    print(f"[AGENT] IP desbloqueado localmente: {ip}", flush=True)
                else:
                    next_applied.add(ip)

            applied_ips = next_applied | (cloud_ips & applied_ips)
            print(f"[AGENT] sync ok | ativos={len(applied_ips)}", flush=True)
        except Exception as exc:
            print(f"[AGENT] Erro a sincronizar firewall: {exc}", flush=True)

        time.sleep(poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())