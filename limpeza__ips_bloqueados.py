#!/usr/bin/env python3
"""Limpa regras de bloqueio de IP no iptables/nftables e opcionalmente remove do banco.

Uso:
  sudo python limpeza__ips_bloqueados.py --ip 192.168.0.236
  sudo python limpeza__ips_bloqueados.py --ip 192.168.0.236 --db-path backend/database/banco.db --remove-db
  sudo python limpeza__ips_bloqueados.py --from-db --remove-db
"""

from __future__ import annotations

import argparse
import ipaddress
import os
import sqlite3
import subprocess
import sys
from pathlib import Path


RULES_IPTABLES = [
    ("INPUT", "-s"),
    ("OUTPUT", "-d"),
    ("FORWARD", "-s"),
    ("FORWARD", "-d"),
]


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def require_root() -> None:
    if os.geteuid() != 0:
        print("Erro: execute com sudo/root para manipular firewall.")
        sys.exit(1)


def remove_iptables_for_ip(ip: str) -> int:
    removed = 0
    for chain, direction in RULES_IPTABLES:
        while True:
            check = run_cmd(["iptables", "-C", chain, direction, ip, "-j", "DROP"])
            if check.returncode != 0:
                break

            delete = run_cmd(["iptables", "-D", chain, direction, ip, "-j", "DROP"])
            if delete.returncode == 0:
                removed += 1
            else:
                print(f"Aviso: falha ao remover regra iptables {chain} {direction} {ip}: {delete.stderr.strip()}")
                break

    return removed


def parse_nft_rule_handles_for_ip(ip: str) -> list[tuple[str, str, str]]:
    """Retorna [(family, table, handle)] para regras contendo o IP."""
    out = run_cmd(["nft", "-a", "list", "ruleset"])
    if out.returncode != 0:
        return []

    handles: list[tuple[str, str, str]] = []
    current_family = ""
    current_table = ""

    for raw_line in out.stdout.splitlines():
        line = raw_line.strip()
        if line.startswith("table "):
            parts = line.split()
            if len(parts) >= 3:
                current_family = parts[1]
                current_table = parts[2]
            continue

        if ip not in line or "# handle " not in line:
            continue

        handle = line.split("# handle ")[-1].strip()
        if current_family and current_table and handle.isdigit():
            handles.append((current_family, current_table, handle))

    # Remover duplicados mantendo ordem.
    seen: set[tuple[str, str, str]] = set()
    unique: list[tuple[str, str, str]] = []
    for item in handles:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)

    return unique


def remove_nft_for_ip(ip: str) -> int:
    removed = 0
    handles = parse_nft_rule_handles_for_ip(ip)
    for family, table, handle in handles:
        cmd = ["nft", "delete", "rule", family, table, "handle", handle]
        result = run_cmd(cmd)
        if result.returncode == 0:
            removed += 1
        else:
            print(
                "Aviso: falha ao remover regra nftables "
                f"{family}/{table} handle {handle}: {result.stderr.strip()}"
            )
    return removed


def read_ips_from_db(db_path: Path) -> list[str]:
    if not db_path.exists():
        print(f"Aviso: banco não encontrado em {db_path}")
        return []

    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute("SELECT ip_bloqueado FROM ips_bloqueados").fetchall()
        ips = [str(row[0]).strip() for row in rows if row and row[0]]
        return [ip for ip in ips if is_valid_ip(ip)]
    finally:
        conn.close()


def remove_ip_from_db(db_path: Path, ip: str) -> int:
    if not db_path.exists():
        return 0

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.execute("DELETE FROM ips_bloqueados WHERE ip_bloqueado = ?", (ip,))
        conn.commit()
        return int(cur.rowcount or 0)
    finally:
        conn.close()


def parse_args() -> argparse.Namespace:
    default_db = Path(__file__).resolve().parent / "backend" / "database" / "banco.db"

    parser = argparse.ArgumentParser(description="Limpeza de bloqueios IPS no firewall e banco")
    parser.add_argument("--ip", help="IP específico para desbloquear")
    parser.add_argument("--from-db", action="store_true", help="Lê IPs bloqueados da tabela ips_bloqueados")
    parser.add_argument("--db-path", default=str(default_db), help="Caminho do banco SQLite")
    parser.add_argument(
        "--remove-db",
        action="store_true",
        help="Remove também os registros da tabela ips_bloqueados",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    require_root()

    ips: list[str] = []

    if args.ip:
        ip = str(args.ip).strip()
        if not is_valid_ip(ip):
            print(f"Erro: IP inválido: {ip}")
            return 1
        ips.append(ip)

    db_path = Path(args.db_path).resolve()
    if args.from_db:
        ips.extend(read_ips_from_db(db_path))

    # Remover duplicados mantendo ordem.
    seen: set[str] = set()
    target_ips: list[str] = []
    for ip in ips:
        if ip in seen:
            continue
        seen.add(ip)
        target_ips.append(ip)

    if not target_ips:
        print("Nenhum IP alvo informado. Use --ip ou --from-db.")
        return 1

    print(f"Iniciando limpeza para {len(target_ips)} IP(s): {', '.join(target_ips)}")

    total_iptables = 0
    total_nft = 0
    total_db_deleted = 0

    for ip in target_ips:
        removed_iptables = remove_iptables_for_ip(ip)
        removed_nft = remove_nft_for_ip(ip)
        total_iptables += removed_iptables
        total_nft += removed_nft

        db_deleted = 0
        if args.remove_db:
            db_deleted = remove_ip_from_db(db_path, ip)
            total_db_deleted += db_deleted

        print(
            f"IP {ip}: iptables removidas={removed_iptables}, "
            f"nft removidas={removed_nft}, db removidos={db_deleted}"
        )

    print(
        "Resumo: "
        f"iptables={total_iptables}, nftables={total_nft}, db={total_db_deleted}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
