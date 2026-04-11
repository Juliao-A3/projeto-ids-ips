"""
Módulo centralizado de whitelist para IDS/IPS
Gerencia IPs seguros (locais, confiáveis) para evitar falsos positivos
"""

import ipaddress
import socket
from typing import Set, List


def get_local_ips() -> Set[str]:
    """Detecta todos os IPs locais da máquina dinamicamente."""
    local_ips = {'127.0.0.1', '::1', 'localhost'}  # loopback
    # Descobre o IP ativo da interface padrão sem enviar tráfego real.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ips.add(s.getsockname()[0])
    except Exception:
        pass

    try:
        hostname = socket.gethostname()
        all_ips_data = socket.getaddrinfo(hostname, None)
        for ip_tuple in all_ips_data:
            ip = ip_tuple[4][0]
            if not ip.startswith('127.') and not ip.startswith('169.254.') and ip not in local_ips:
                local_ips.add(ip)
    except Exception as e:
        print(f"⚠️  Erro ao detectar IPs locais: {e}")
    
    return local_ips


def _load_default_cidr_ranges() -> List[ipaddress.IPv4Network | ipaddress.IPv6Network]:
    """Carrega ranges CIDR padrão seguros."""
    cidr_defaults = [
        # Loopback / link-local / multicast / broadcast
        '127.0.0.0/8',
        '::1/128',
        '169.254.0.0/16',
        'fe80::/10',
        '224.0.0.0/4',
        'ff00::/8',
        '224.0.0.251',
        '239.255.255.250',
        '255.255.255.255',

        # Redes privadas (RFC 1918)
        '10.0.0.0/8',
        '172.16.0.0/12',
        '192.168.0.0/16',

        # Google (GCP + serviços)
        '8.8.8.0/24',
        '8.8.4.0/24',
        '142.250.0.0/15',
        '142.251.0.0/16',
        '172.217.0.0/16',
        '34.0.0.0/9',
        '35.184.0.0/13',

        # Microsoft / Azure
        '13.64.0.0/11',
        '13.96.0.0/13',
        '13.104.0.0/14',
        '20.0.0.0/8',
        '40.64.0.0/10',

        # GitHub
        '140.82.112.0/20',
        '192.30.252.0/22',
        '185.199.108.0/22',

        # Cloudflare
        '1.1.1.0/24',
        '1.0.0.0/24',
        '104.16.0.0/13',
        '104.24.0.0/14',
    ]
    
    cidr_networks = []
    for cidr in cidr_defaults:
        try:
            cidr_networks.append(ipaddress.ip_network(cidr, strict=False))
        except ValueError:
            pass
    
    return cidr_networks


class Whitelist:
    """Gerenciador centralizado de whitelist para IDS/IPS."""
    
    def __init__(self):
        self.exact_ips: Set[str] = get_local_ips()
        self.cidr_networks: List[ipaddress.IPv4Network | ipaddress.IPv6Network] = _load_default_cidr_ranges()
        print(f"✅ Whitelist inicializada - IPs locais: {self.exact_ips}")
    
    def is_ip_whitelisted(self, ip: str) -> bool:
        """Verifica se um IP está na whitelist (exacto ou em range CIDR)."""
        if not ip or ip == "":
            return False
            
        # Verificar IP exacto
        if ip in self.exact_ips:
            return True
        
        # Verificar ranges CIDR
        try:
            addr = ipaddress.ip_address(ip)
            return any(addr in net for net in self.cidr_networks)
        except ValueError:
            return False
    
    def add_exact_ip(self, ip: str) -> bool:
        """Adiciona um IP exacto à whitelist."""
        try:
            ipaddress.ip_address(ip)  # validar
            self.exact_ips.add(ip)
            return True
        except ValueError:
            return False
    
    def add_cidr_range(self, cidr: str) -> bool:
        """Adiciona um range CIDR à whitelist."""
        try:
            self.cidr_networks.append(ipaddress.ip_network(cidr, strict=False))
            return True
        except ValueError:
            return False
    
    def remove_exact_ip(self, ip: str) -> bool:
        """Remove um IP exacto da whitelist."""
        if ip in self.exact_ips:
            self.exact_ips.discard(ip)
            return True
        return False
    
    def get_all_ips(self) -> Set[str]:
        """Retorna todos os IPs exact na whitelist."""
        return self.exact_ips.copy()
    
    def get_all_cidrs(self) -> List[str]:
        """Retorna todos os ranges CIDR na whitelist."""
        return [str(net) for net in self.cidr_networks]


# Instância global
_whitelist_instance = None


def get_whitelist() -> Whitelist:
    """Retorna a instância singleton da whitelist."""
    global _whitelist_instance
    if _whitelist_instance is None:
        _whitelist_instance = Whitelist()
    return _whitelist_instance
