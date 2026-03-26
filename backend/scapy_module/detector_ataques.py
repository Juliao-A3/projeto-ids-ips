# backend/scapy_module/detector_ataques.py
# Detector de tipos de ataque baseado em padrões de tráfego

from scapy.all import TCP, IP
from collections import defaultdict
import time

class DetectorAtaques:
    """
    Identifica o tipo de ataque com base no padrão de pacotes/fluxos
    """
    
    def __init__(self):
        # Contadores para deteção de padrões
        self.syn_count = defaultdict(int)           # SYN flood
        self.port_scan_ports = defaultdict(set)     # Port scan
        self.brute_force_count = defaultdict(int)   # Brute force
        self.icmp_count = defaultdict(int)          # ICMP flood
        self.udp_count = defaultdict(int)           # UDP flood
        self.http_slow_count = defaultdict(int)     # Slowloris
        
        # Limiares
        self.SYN_FLOOD_THRESHOLD = 100
        self.PORT_SCAN_THRESHOLD = 20
        self.BRUTE_FORCE_THRESHOLD = 10
        self.ICMP_FLOOD_THRESHOLD = 50
        self.UDP_FLOOD_THRESHOLD = 50
        self.SLOWLORIS_THRESHOLD = 50
        
        # Janela de tempo (segundos)
        self.time_window = 10
    
    def detectar(self, fluxo):
        """
        Detecta o tipo de ataque baseado no fluxo
        
        Returns:
            str: tipo de ataque ou None
        """
        # Verificar XMAS scan (flags FIN+PSH+URG)
        if self._is_xmas_scan(fluxo):
            return "XMAS_SCAN"
        
        # Verificar NULL scan (sem flags)
        if self._is_null_scan(fluxo):
            return "NULL_SCAN"
        
        # Verificar SYN flood (muitos pacotes SYN)
        if self._is_syn_flood(fluxo):
            return "SYN_FLOOD"
        
        # Verificar ACK scan
        if self._is_ack_scan(fluxo):
            return "ACK_SCAN"
        
        # Verificar FIN scan
        if self._is_fin_scan(fluxo):
            return "FIN_SCAN"
        
        # Verificar port scan (muitas portas diferentes)
        if self._is_port_scan(fluxo):
            return "PORT_SCAN"
        
        # Verificar brute force (muitas tentativas de login)
        if self._is_brute_force(fluxo):
            return "BRUTE_FORCE"
        
        # Verificar UDP flood
        if self._is_udp_flood(fluxo):
            return "UDP_FLOOD"
        
        # Verificar ICMP flood
        if self._is_icmp_flood(fluxo):
            return "ICMP_FLOOD"
        
        # Verificar ataque HTTP (Slowloris)
        if self._is_http_attack(fluxo):
            return self._get_http_attack_type(fluxo)
        
        # Verificar DDoS (muitos pacotes de várias origens)
        if self._is_ddos(fluxo):
            return "DDOS"
        
        # Verificar ping of death
        if self._is_ping_of_death(fluxo):
            return "PING_OF_DEATH"
        
        # Verificar fragmentação anormal
        if self._is_fragmentation_attack(fluxo):
            return "FRAGMENTATION_ATTACK"
        
        # Verificar túnel DNS
        if self._is_dns_tunnel(fluxo):
            return "DNS_TUNNEL"
        
        # Verificar exfiltração de dados
        if self._is_data_exfiltration(fluxo):
            return "DATA_EXFILTRATION"
        
        return None
    
    # ========== SCANS ==========
    
    def _is_xmas_scan(self, fluxo):
        """XMAS scan: flags FIN, PSH e URG ativas"""
        if fluxo.packets:
            pkt = fluxo.packets[0]
            if TCP in pkt:
                flags = pkt[TCP].flags
                if (flags & 0x01) and (flags & 0x08) and (flags & 0x20):
                    return True
        return False
    
    def _is_null_scan(self, fluxo):
        """NULL scan: sem flags TCP"""
        if fluxo.packets:
            pkt = fluxo.packets[0]
            if TCP in pkt:
                flags = pkt[TCP].flags
                if flags == 0:
                    return True
        return False
    
    def _is_ack_scan(self, fluxo):
        """ACK scan: flag ACK ativa sem conexão estabelecida"""
        if fluxo.packets:
            pkt = fluxo.packets[0]
            if TCP in pkt:
                flags = pkt[TCP].flags
                if (flags & 0x10) and not (flags & 0x02):
                    return True
        return False
    
    def _is_fin_scan(self, fluxo):
        """FIN scan: flag FIN ativa"""
        if fluxo.packets:
            pkt = fluxo.packets[0]
            if TCP in pkt:
                flags = pkt[TCP].flags
                if (flags & 0x01) and not (flags & 0x02) and not (flags & 0x04):
                    return True
        return False
    
    # ========== FLOODS ==========
    
    def _is_syn_flood(self, fluxo):
        """SYN flood: muitas tentativas SYN"""
        if fluxo.protocol == 6:  # TCP
            total_syn = fluxo.fwd_syn_count + fluxo.bwd_syn_count
            if total_syn > self.SYN_FLOOD_THRESHOLD:
                return True
        return False
    
    def _is_udp_flood(self, fluxo):
        """UDP flood: muitos pacotes UDP"""
        if fluxo.protocol == 17:  # UDP
            if fluxo.total_packets > self.UDP_FLOOD_THRESHOLD:
                return True
        return False
    
    def _is_icmp_flood(self, fluxo):
        """ICMP flood: muitos pacotes ICMP"""
        if fluxo.protocol == 1:  # ICMP
            if fluxo.total_packets > self.ICMP_FLOOD_THRESHOLD:
                return True
        return False
    
    # ========== SCANS ==========
    
    def _is_port_scan(self, fluxo):
        """Port scan: muitas portas diferentes do mesmo IP"""
        # Esta deteção precisa de contexto global
        return False
    
    # ========== BRUTE FORCE ==========
    
    def _is_brute_force(self, fluxo):
        """Brute force: muitas tentativas na mesma porta"""
        if fluxo.protocol == 6:  # TCP
            if fluxo.total_packets > self.BRUTE_FORCE_THRESHOLD:
                # Verificar se são tentativas de login (portas comuns)
                if fluxo.dst_port in [21, 22, 23, 25, 80, 443, 3389]:
                    return True
        return False
    
    # ========== HTTP ATTACKS ==========
    
    def _is_http_attack(self, fluxo):
        """Ataque HTTP (Slowloris, etc.)"""
        if fluxo.dst_port in [80, 443, 8080]:
            duration = fluxo.end_time - fluxo.start_time if fluxo.start_time else 0
            # Fluxo longo com poucos dados
            if duration > 60 and fluxo.total_bytes < 1000:
                return True
        return False
    
    def _get_http_attack_type(self, fluxo):
        """Retorna tipo específico de ataque HTTP"""
        duration = fluxo.end_time - fluxo.start_time if fluxo.start_time else 0
        packet_rate = fluxo.total_packets / duration if duration > 0 else 0
        
        if packet_rate < 0.5:  # Muito lento
            return "SLOWLORIS"
        elif packet_rate > 100:  # Muito rápido
            return "HTTP_FLOOD"
        else:
            return "HTTP_ATTACK"
    
    # ========== DDOS ==========
    
    def _is_ddos(self, fluxo):
        """DDoS: muitos pacotes de várias origens (detecção simplificada)"""
        # Precisa de contexto global (vários fluxos)
        return False
    
    # ========== ICMP ATTACKS ==========
    
    def _is_ping_of_death(self, fluxo):
        """Ping of death: pacote ICMP muito grande"""
        if fluxo.protocol == 1:  # ICMP
            if fluxo.total_bytes > 65535:
                return True
        return False
    
    # ========== FRAGMENTATION ==========
    
    def _is_fragmentation_attack(self, fluxo):
        """Ataque por fragmentação"""
        # Verificar se há muitos fragmentos
        # (simplificado)
        return False
    
    # ========== DNS ATTACKS ==========
    
    def _is_dns_tunnel(self, fluxo):
        """Túnel DNS: muitos pacotes DNS com payload grande"""
        if fluxo.dst_port == 53 or fluxo.src_port == 53:
            # DNS normal tem payload pequeno
            if fluxo.total_packets > 100 and fluxo.total_bytes / fluxo.total_packets > 200:
                return True
        return False
    
    # ========== DATA EXFILTRATION ==========
    
    def _is_data_exfiltration(self, fluxo):
        """Exfiltração de dados: fluxo longo com muitos dados"""
        duration = fluxo.end_time - fluxo.start_time if fluxo.start_time else 0
        if duration > 300 and fluxo.total_bytes > 1000000:  # 5 minutos, 1MB
            return True
        return False


# Instância global
detector = DetectorAtaques()