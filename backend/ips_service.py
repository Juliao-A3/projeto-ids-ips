import ipaddress
import os
import subprocess
import threading
from datetime import datetime
from typing import Callable, Optional

from models import IpsBloqueados


class IPSService:
    """Serviço IPS simples: bloqueia IP após N alertas maliciosos."""

    def __init__(self, threshold: int = 5):
        self.threshold = max(1, int(threshold))
        self.running = False
        self._lock = threading.Lock()
        self._malicious_counts: dict[str, int] = {}
        self._blocked_ips: set[str] = set()

    def iniciar(self) -> None:
        self.running = True

    def parar(self) -> None:
        self.running = False

    def reset(self) -> None:
        with self._lock:
            self._malicious_counts.clear()

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

    def register_malicious_flow(
        self,
        src_ip: str,
        reason: str,
        session_factory: Optional[Callable] = None,
    ) -> dict:
        """Regista fluxo malicioso e bloqueia IP quando atingir threshold."""
        ip = str(src_ip or "").strip()
        if not self.running or not ip or not self._is_valid_ip(ip):
            return {"blocked": False}

        with self._lock:
            current = self._malicious_counts.get(ip, 0) + 1
            self._malicious_counts[ip] = current

            if ip in self._blocked_ips:
                return {
                    "blocked": False,
                    "already_blocked": True,
                    "ip": ip,
                    "count": current,
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

        rules = [
            ["iptables", "-C", "INPUT", "-s", ip, "-j", "DROP"],
            ["iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"],
            ["iptables", "-C", "OUTPUT", "-d", ip, "-j", "DROP"],
            ["iptables", "-I", "OUTPUT", "-d", ip, "-j", "DROP"],
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
            print("[IPS] iptables não encontrado; bloqueio aplicado apenas no banco/memória.")
            return False
        except Exception as exc:
            print(f"[IPS] Falha ao aplicar iptables para {ip}: {exc}")
            return False
