import ipaddress
import os
import subprocess
import threading
import time
import shutil
from collections import defaultdict, deque
from datetime import datetime
from typing import Callable, Optional

from models import IpsBloqueados
from sqlalchemy.orm import Session


class IPSService:
    """Serviço IPS simples: bloqueia IP após N alertas maliciosos."""

    def __init__(self, threshold: int = 5):
        self.threshold = max(1, int(threshold))
        self.attack_window_seconds = max(1, int(os.getenv("IPS_ATTACK_WINDOW_SECONDS", "120")))
        self.running = False
        self._lock = threading.Lock()
        self._malicious_counts: dict[str, int] = {}
        self._malicious_timestamps: dict[str, deque[float]] = defaultdict(deque)
        self._blocked_ips: set[str] = set()
        self._firewall_cmd = self._detect_firewall_cmd()

    def iniciar(self) -> None:
        self.running = True

    def parar(self) -> None:
        self.running = False

    def reset(self) -> None:
        with self._lock:
            self._malicious_counts.clear()
            self._malicious_timestamps.clear()

    def carregar_bloqueados_db(self, session_factory: Optional[Callable]) -> None:
        """Sincroniza estado em memória com IPs já bloqueados no banco."""
        if not session_factory:
            return

        session: Optional[Session] = None
        try:
            session = next(session_factory())
            rows = session.query(IpsBloqueados).all()
            blocked_from_db = {str(r.ip_bloqueado).strip() for r in rows if r.ip_bloqueado}
            with self._lock:
                self._blocked_ips = blocked_from_db

            # Reaplica no sistema para evitar estado "bloqueado no banco" sem regra ativa no kernel.
            if os.getenv("IPS_REAPPLY_DB_BLOCKS", "1") == "1":
                for ip in blocked_from_db:
                    if ip:
                        self._block_ip_system(ip)
        except Exception as exc:
            print(f"[IPS] Erro ao sincronizar IPs bloqueados do banco: {exc}")
        finally:
            if session is not None:
                session.close()

    def get_blocked_ips(self) -> list[str]:
        with self._lock:
            return sorted(self._blocked_ips)

    def get_block_count(self) -> int:
        with self._lock:
            return len(self._blocked_ips)

    def _is_valid_ip(self, ip: str) -> bool:
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def _detect_firewall_cmd(self) -> Optional[str]:
        for candidate in ("iptables", "iptables-nft", "iptables-legacy"):
            if shutil.which(candidate):
                return candidate
        return None

    def register_malicious_flow(
        self,
        src_ip: str,
        reason: str,
        session_factory: Optional[Callable] = None,
        observed_count: Optional[int] = None,
    ) -> dict:
        """Regista fluxo malicioso e bloqueia IP quando atingir threshold na janela ativa."""
        ip = str(src_ip or "").strip()
        if not self.running or not ip or not self._is_valid_ip(ip):
            return {"blocked": False}

        with self._lock:
            now = time.time()
            attempts = self._malicious_timestamps[ip]
            attempts.append(now)
            cutoff = now - self.attack_window_seconds
            while attempts and attempts[0] < cutoff:
                attempts.popleft()

            current = len(attempts)

            # Compatibilidade: manter contagem externa apenas se for maior e válida.
            if observed_count is not None:
                try:
                    observed = max(0, int(observed_count))
                    current = max(current, observed)
                except (TypeError, ValueError):
                    pass

            self._malicious_counts[ip] = current

            if ip in self._blocked_ips:
                # Garante regra ativa no sistema mesmo quando o IP já estava marcado em memória.
                blocked_system = self._block_ip_system(ip)
                return {
                    "blocked": False,
                    "already_blocked": True,
                    "ip": ip,
                    "count": current,
                    "blocked_system": blocked_system,
                }

            if current < self.threshold:
                return {
                    "blocked": False,
                    "ip": ip,
                    "count": current,
                    "remaining": self.threshold - current,
                }

            blocked_system = self._block_ip_system(ip)
            blocked_db = self._persist_block(ip, reason, session_factory)
            self._blocked_ips.add(ip)

            return {
                "blocked": True,
                "ip": ip,
                "count": current,
                "blocked_system": blocked_system,
                "blocked_db": blocked_db,
            }

    def unblock_ip(self, ip: str) -> dict:
        """Remove bloqueio do sistema e da memória para um IP."""
        ip = str(ip or "").strip()
        if not ip or not self._is_valid_ip(ip):
            return {"ok": False, "detail": "IP inválido"}

        unblocked_system = self._unblock_ip_system(ip)

        with self._lock:
            self._blocked_ips.discard(ip)
            self._malicious_counts.pop(ip, None)
            self._malicious_timestamps.pop(ip, None)

        return {"ok": True, "ip": ip, "unblocked_system": unblocked_system}

    def _persist_block(self, ip: str, reason: str, session_factory: Optional[Callable]) -> bool:
        if not session_factory:
            return False

        session = None
        try:
            session = next(session_factory())
            exists = session.query(IpsBloqueados).filter(IpsBloqueados.ip_bloqueado == ip).first()
            if exists:
                return True

            row = IpsBloqueados(
                ip_bloqueado=ip,
                motivo=reason or "Bloqueio automático por tráfego malicioso recorrente",
            )
            session.add(row)
            session.commit()
            return True
        except Exception as exc:
            if session is not None:
                try:
                    session.rollback()
                except Exception:
                    pass
            print(f"[IPS] Erro ao persistir bloqueio de IP {ip}: {exc}")
            return False
        finally:
            if session is not None:
                session.close()

    def _block_ip_system(self, ip: str) -> bool:
        """Aplica bloqueio no host Linux via iptables para INPUT e OUTPUT."""
        if not os.name == "posix":
            print(f"[IPS] Bloqueio de sistema indisponível neste SO para {ip}.")
            return False

        firewall_cmd = self._firewall_cmd or self._detect_firewall_cmd()
        if not firewall_cmd:
            print(f"[IPS] Nenhum comando de firewall encontrado; IP {ip} ficou apenas bloqueado na aplicação/banco.")
            return False
        self._firewall_cmd = firewall_cmd

        rules = [
            [firewall_cmd, "-C", "INPUT", "-s", ip, "-j", "DROP"],
            [firewall_cmd, "-I", "INPUT", "-s", ip, "-j", "DROP"],
            [firewall_cmd, "-C", "OUTPUT", "-d", ip, "-j", "DROP"],
            [firewall_cmd, "-I", "OUTPUT", "-d", ip, "-j", "DROP"],
        ]

        try:
            check_in = subprocess.run(rules[0], capture_output=True, text=True, check=False)
            if check_in.returncode != 0:
                subprocess.run(rules[1], capture_output=True, text=True, check=False)

            check_out = subprocess.run(rules[2], capture_output=True, text=True, check=False)
            if check_out.returncode != 0:
                subprocess.run(rules[3], capture_output=True, text=True, check=False)

            print(f"[IPS] IP bloqueado no sistema: {ip} em {datetime.now().isoformat()}")
            return True
        except FileNotFoundError:
            print(f"[IPS] {firewall_cmd} não encontrado; bloqueio aplicado apenas no banco/memória para {ip}.")
            return False
        except Exception as exc:
            print(f"[IPS] Falha ao aplicar iptables para {ip}: {exc}")
            return False

    def _unblock_ip_system(self, ip: str) -> bool:
        """Remove regras iptables de INPUT/OUTPUT para restabelecer tráfego."""
        if not os.name == "posix":
            print(f"[IPS] Desbloqueio de sistema indisponível neste SO para {ip}.")
            return False

        firewall_cmd = self._firewall_cmd or self._detect_firewall_cmd()
        if not firewall_cmd:
            print(f"[IPS] Nenhum comando de firewall encontrado; IP {ip} foi removido só da aplicação/banco.")
            return False

        deleted_any = False
        try:
            while True:
                chk = subprocess.run(
                    [firewall_cmd, "-C", "INPUT", "-s", ip, "-j", "DROP"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if chk.returncode != 0:
                    break
                subprocess.run(
                    [firewall_cmd, "-D", "INPUT", "-s", ip, "-j", "DROP"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                deleted_any = True

            while True:
                chk = subprocess.run(
                    [firewall_cmd, "-C", "OUTPUT", "-d", ip, "-j", "DROP"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if chk.returncode != 0:
                    break
                subprocess.run(
                    [firewall_cmd, "-D", "OUTPUT", "-d", ip, "-j", "DROP"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                deleted_any = True

            print(f"[IPS] IP desbloqueado no sistema: {ip} em {datetime.now().isoformat()}")
            return deleted_any
        except FileNotFoundError:
            print(f"[IPS] {firewall_cmd} não encontrado; desbloqueio aplicado apenas em memória/banco para {ip}.")
            return False
        except Exception as exc:
            print(f"[IPS] Falha ao remover regras iptables para {ip}: {exc}")
            return False
