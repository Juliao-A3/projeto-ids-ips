# backend/scapy_module/extractor.py
# Extrator de features por FLUXO - 78 features + compatibilidade com modelo antigo

import numpy as np
from scapy.all import IP, TCP, UDP, ICMP, Raw
from collections import defaultdict
import time
import math

# ============================================
# CLASSE FLOW - REPRESENTA UM FLUXO DE REDE
# ============================================

class Flow:
    """Representa um fluxo de rede (5-tuple)"""
    
    def __init__(self, src_ip, dst_ip, src_port, dst_port, protocol):
        self.key = (src_ip, dst_ip, src_port, dst_port, protocol)
        
        # Informações básicas
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.src_port = src_port
        self.dst_port = dst_port
        self.protocol = protocol
        
        # Timestamps
        self.start_time = None
        self.end_time = None
        self.first_packet_time = None
        self.last_packet_time = None
        self.packets = []  # Lista de pacotes do fluxo
        
        # Contadores
        self.total_packets = 0
        self.total_bytes = 0
        
        # Contadores direcionais
        self.fwd_packets = 0
        self.bwd_packets = 0
        self.fwd_bytes = 0
        self.bwd_bytes = 0
        
        # Listas para estatísticas
        self.fwd_packet_sizes = []
        self.bwd_packet_sizes = []
        self.all_packet_sizes = []
        
        # IAT (Inter-Arrival Time)
        self.iat_list = []
        self.fwd_iat_list = []
        self.bwd_iat_list = []
        
        # Timestamps individuais
        self.fwd_timestamps = []
        self.bwd_timestamps = []
        
        # Flags TCP
        self.fwd_psh_count = 0
        self.bwd_psh_count = 0
        self.fwd_urg_count = 0
        self.bwd_urg_count = 0
        self.fwd_syn_count = 0
        self.bwd_syn_count = 0
        self.fwd_fin_count = 0
        self.bwd_fin_count = 0
        self.fwd_rst_count = 0
        self.bwd_rst_count = 0
        self.fwd_ack_count = 0
        self.bwd_ack_count = 0
        
        # Tamanhos de cabeçalho
        self.fwd_header_bytes = 0
        self.bwd_header_bytes = 0
        
        # Windows size
        self.fwd_win_bytes = 0
        self.bwd_win_bytes = 0
        self.fwd_win_count = 0
        self.bwd_win_count = 0
        
        # Inicialização
        self.previous_timestamp = None
        self.previous_fwd_timestamp = None
        self.previous_bwd_timestamp = None
        self.forward_direction = None
        
        # Subflows
        self.subflow_fwd_packets = []
        self.subflow_fwd_bytes = []
        self.subflow_bwd_packets = []
        self.subflow_bwd_bytes = []
        self.current_subflow_start = None
        self._temp_fwd_packets = 0
        self._temp_fwd_bytes = 0
        self._temp_bwd_packets = 0
        self._temp_bwd_bytes = 0
        
        # Active/Idle
        self.active_times = []
        self.idle_times = []
        self.last_active_time = None
        
        # Segment sizes
        self.fwd_seg_size_min = float('inf')
        self.fwd_seg_size_max = 0
        self.fwd_seg_size_sum = 0
        self.fwd_seg_size_count = 0
        self.bwd_seg_size_min = float('inf')
        self.bwd_seg_size_max = 0
        self.bwd_seg_size_sum = 0
        self.bwd_seg_size_count = 0
    
    def _determine_direction(self, pkt):
        """Determina se o pacote é forward ou backward"""
        if IP not in pkt:
            return None
        
        ip = pkt[IP]
        
        if self.forward_direction is None:
            self.forward_direction = ip.src
            return 'forward'
        
        if ip.src == self.forward_direction:
            return 'forward'
        else:
            return 'backward'
    
    def _update_subflow(self, timestamp):
        """Atualiza subflows (segmentos de 1 segundo)"""
        if self.current_subflow_start is None:
            self.current_subflow_start = timestamp
            return
        
        if timestamp - self.current_subflow_start >= 1.0:
            self.subflow_fwd_packets.append(self._temp_fwd_packets)
            self.subflow_fwd_bytes.append(self._temp_fwd_bytes)
            self.subflow_bwd_packets.append(self._temp_bwd_packets)
            self.subflow_bwd_bytes.append(self._temp_bwd_bytes)
            
            self.current_subflow_start = timestamp
            self._temp_fwd_packets = 0
            self._temp_fwd_bytes = 0
            self._temp_bwd_packets = 0
            self._temp_bwd_bytes = 0
    
    def add_packet(self, pkt, timestamp):
        """Adiciona um pacote ao fluxo"""
        
        if self.first_packet_time is None:
            self.first_packet_time = timestamp
            self.start_time = timestamp
            self.last_active_time = timestamp
            self.current_subflow_start = timestamp
        
        self.last_packet_time = timestamp
        self.end_time = timestamp
        self.packets.append(pkt)
        
        direction = self._determine_direction(pkt)
        packet_size = len(pkt)
        self.total_packets += 1
        self.total_bytes += packet_size
        self.all_packet_sizes.append(packet_size)
        
        if direction == 'forward':
            self.fwd_packets += 1
            self.fwd_bytes += packet_size
            self.fwd_packet_sizes.append(packet_size)
            self.fwd_timestamps.append(timestamp)
            
            self._temp_fwd_packets += 1
            self._temp_fwd_bytes += packet_size
            
            if self.previous_fwd_timestamp:
                iat = timestamp - self.previous_fwd_timestamp
                self.fwd_iat_list.append(iat)
            self.previous_fwd_timestamp = timestamp
            
            self.fwd_seg_size_sum += packet_size
            self.fwd_seg_size_count += 1
            if packet_size < self.fwd_seg_size_min:
                self.fwd_seg_size_min = packet_size
            if packet_size > self.fwd_seg_size_max:
                self.fwd_seg_size_max = packet_size
            
            if self.last_active_time:
                idle = timestamp - self.last_active_time
                if idle > 0:
                    self.idle_times.append(idle)
            self.last_active_time = timestamp
            
        else:
            self.bwd_packets += 1
            self.bwd_bytes += packet_size
            self.bwd_packet_sizes.append(packet_size)
            self.bwd_timestamps.append(timestamp)
            
            self._temp_bwd_packets += 1
            self._temp_bwd_bytes += packet_size
            
            if self.previous_bwd_timestamp:
                iat = timestamp - self.previous_bwd_timestamp
                self.bwd_iat_list.append(iat)
            self.previous_bwd_timestamp = timestamp
            
            self.bwd_seg_size_sum += packet_size
            self.bwd_seg_size_count += 1
            if packet_size < self.bwd_seg_size_min:
                self.bwd_seg_size_min = packet_size
            if packet_size > self.bwd_seg_size_max:
                self.bwd_seg_size_max = packet_size
        
        if self.previous_timestamp:
            iat = timestamp - self.previous_timestamp
            self.iat_list.append(iat)
        self.previous_timestamp = timestamp
        
        if self.last_active_time:
            active = timestamp - self.last_active_time
            if active > 0:
                self.active_times.append(active)
        self.last_active_time = timestamp
        
        self._update_subflow(timestamp)
        
        # Processar flags TCP
        if TCP in pkt:
            tcp = pkt[TCP]
            flags = tcp.flags
            
            if direction == 'forward':
                if flags.PSH: self.fwd_psh_count += 1
                if flags.URG: self.fwd_urg_count += 1
                if flags.S: self.fwd_syn_count += 1
                if flags.F: self.fwd_fin_count += 1
                if flags.R: self.fwd_rst_count += 1
                if flags.A: self.fwd_ack_count += 1
                self.fwd_win_bytes += tcp.window
                self.fwd_win_count += 1
                self.fwd_header_bytes += (tcp.dataofs * 4)
            else:
                if flags.PSH: self.bwd_psh_count += 1
                if flags.URG: self.bwd_urg_count += 1
                if flags.S: self.bwd_syn_count += 1
                if flags.F: self.bwd_fin_count += 1
                if flags.R: self.bwd_rst_count += 1
                if flags.A: self.bwd_ack_count += 1
                self.bwd_win_bytes += tcp.window
                self.bwd_win_count += 1
                self.bwd_header_bytes += (tcp.dataofs * 4)
    
    def _calculate_stats(self, values):
        if not values:
            return 0, 0, 0, 0
        return np.mean(values), np.std(values), np.min(values), np.max(values)
    
    def get_features(self):
        """Retorna dicionário com todas as 78 features"""
        
        duration = (self.end_time - self.start_time) if self.start_time else 0
        
        fwd_mean, fwd_std, fwd_min, fwd_max = self._calculate_stats(self.fwd_packet_sizes)
        bwd_mean, bwd_std, bwd_min, bwd_max = self._calculate_stats(self.bwd_packet_sizes)
        all_mean, all_std, all_min, all_max = self._calculate_stats(self.all_packet_sizes)
        
        iat_mean, iat_std, iat_min, iat_max = self._calculate_stats(self.iat_list)
        fwd_iat_mean, fwd_iat_std, fwd_iat_min, fwd_iat_max = self._calculate_stats(self.fwd_iat_list)
        bwd_iat_mean, bwd_iat_std, bwd_iat_min, bwd_iat_max = self._calculate_stats(self.bwd_iat_list)
        
        fwd_iat_total = sum(self.fwd_iat_list) if self.fwd_iat_list else 0
        bwd_iat_total = sum(self.bwd_iat_list) if self.bwd_iat_list else 0
        
        packet_rate = self.total_packets / duration if duration > 0 else 0
        byte_rate = self.total_bytes / duration if duration > 0 else 0
        fwd_packet_rate = self.fwd_packets / duration if duration > 0 else 0
        bwd_packet_rate = self.bwd_packets / duration if duration > 0 else 0
        
        down_up_ratio = self.bwd_packets / self.fwd_packets if self.fwd_packets > 0 else 0
        
        fwd_avg_seg_size = self.fwd_seg_size_sum / self.fwd_seg_size_count if self.fwd_seg_size_count > 0 else 0
        bwd_avg_seg_size = self.bwd_seg_size_sum / self.bwd_seg_size_count if self.bwd_seg_size_count > 0 else 0
        
        fwd_avg_win = self.fwd_win_bytes / self.fwd_win_count if self.fwd_win_count > 0 else 0
        bwd_avg_win = self.bwd_win_bytes / self.bwd_win_count if self.bwd_win_count > 0 else 0
        
        subflow_fwd_avg_packets = np.mean(self.subflow_fwd_packets) if self.subflow_fwd_packets else 0
        subflow_fwd_avg_bytes = np.mean(self.subflow_fwd_bytes) if self.subflow_fwd_bytes else 0
        subflow_bwd_avg_packets = np.mean(self.subflow_bwd_packets) if self.subflow_bwd_packets else 0
        subflow_bwd_avg_bytes = np.mean(self.subflow_bwd_bytes) if self.subflow_bwd_bytes else 0
        
        active_mean, active_std, active_min, active_max = self._calculate_stats(self.active_times)
        idle_mean, idle_std, idle_min, idle_max = self._calculate_stats(self.idle_times)
        
        return {
            'Flow Duration': duration,
            'Total Fwd Packets': self.fwd_packets,
            'Total Backward Packets': self.bwd_packets,
            'Total Length of Fwd Packets': self.fwd_bytes,
            'Total Length of Bwd Packets': self.bwd_bytes,
            'Fwd Packet Length Max': fwd_max,
            'Fwd Packet Length Min': fwd_min,
            'Fwd Packet Length Mean': fwd_mean,
            'Fwd Packet Length Std': fwd_std,
            'Bwd Packet Length Max': bwd_max,
            'Bwd Packet Length Min': bwd_min,
            'Bwd Packet Length Mean': bwd_mean,
            'Bwd Packet Length Std': bwd_std,
            'Packet Length Max': all_max,
            'Packet Length Min': all_min,
            'Packet Length Mean': all_mean,
            'Packet Length Std': all_std,
            'Packet Length Variance': all_std ** 2,
            'Flow IAT Mean': iat_mean,
            'Flow IAT Std': iat_std,
            'Flow IAT Max': iat_max,
            'Flow IAT Min': iat_min,
            'Fwd IAT Total': fwd_iat_total,
            'Fwd IAT Mean': fwd_iat_mean,
            'Fwd IAT Std': fwd_iat_std,
            'Fwd IAT Max': fwd_iat_max,
            'Fwd IAT Min': fwd_iat_min,
            'Bwd IAT Total': bwd_iat_total,
            'Bwd IAT Mean': bwd_iat_mean,
            'Bwd IAT Std': bwd_iat_std,
            'Bwd IAT Max': bwd_iat_max,
            'Bwd IAT Min': bwd_iat_min,
            'Fwd PSH Flags': self.fwd_psh_count,
            'Bwd PSH Flags': self.bwd_psh_count,
            'Fwd URG Flags': self.fwd_urg_count,
            'Bwd URG Flags': self.bwd_urg_count,
            'FIN Flag Count': self.fwd_fin_count + self.bwd_fin_count,
            'SYN Flag Count': self.fwd_syn_count + self.bwd_syn_count,
            'RST Flag Count': self.fwd_rst_count + self.bwd_rst_count,
            'PSH Flag Count': self.fwd_psh_count + self.bwd_psh_count,
            'ACK Flag Count': self.fwd_ack_count + self.bwd_ack_count,
            'URG Flag Count': self.fwd_urg_count + self.bwd_urg_count,
            'Flow Bytes/s': byte_rate,
            'Flow Packets/s': packet_rate,
            'Fwd Packets/s': fwd_packet_rate,
            'Bwd Packets/s': bwd_packet_rate,
            'Down/Up Ratio': down_up_ratio,
            'Average Packet Size': all_mean,
            'Avg Fwd Segment Size': fwd_avg_seg_size,
            'Avg Bwd Segment Size': bwd_avg_seg_size,
            'Fwd Header Length': self.fwd_header_bytes,
            'Bwd Header Length': self.bwd_header_bytes,
            'Init_Win_bytes_forward': fwd_avg_win,
            'Init_Win_bytes_backward': bwd_avg_win,
            'Subflow Fwd Packets': subflow_fwd_avg_packets,
            'Subflow Fwd Bytes': subflow_fwd_avg_bytes,
            'Subflow Bwd Packets': subflow_bwd_avg_packets,
            'Subflow Bwd Bytes': subflow_bwd_avg_bytes,
            'Active Mean': active_mean,
            'Active Std': active_std,
            'Active Max': active_max,
            'Active Min': active_min,
            'Idle Mean': idle_mean,
            'Idle Std': idle_std,
            'Idle Max': idle_max,
            'Idle Min': idle_min,
            'min_seg_size_forward': self.fwd_seg_size_min if self.fwd_seg_size_min != float('inf') else 0,
            'Src Port': self.src_port,
            'Dst Port': self.dst_port,
            'Protocol': self.protocol
        }
    
    def get_legado_features(self):
        """Extrai as 14 features do modelo antigo a partir do fluxo"""
        if not self.packets:
            return [0] * 14
        
        pkt = self.packets[0]
        last_time = self.packets[-1].time if len(self.packets) > 1 else None
        
        feat = [0] * 14
        
        feat[0] = len(pkt)
        
        if IP in pkt:
            ip = pkt[IP]
            feat[1] = ip.proto
            feat[2] = ip.ttl
            try:
                last_octet = int(ip.src.split('.')[-1])
                feat[8] = last_octet / 255.0
            except:
                feat[8] = 0
        
        if TCP in pkt:
            tcp = pkt[TCP]
            feat[3] = tcp.window
            feat[4] = int(tcp.flags)
            feat[5] = tcp.sport
            feat[6] = tcp.dport
            feat[9] = 1 if tcp.flags.S else 0
            feat[10] = 1 if tcp.flags.A else 0
            feat[11] = 1 if tcp.flags.F else 0
            feat[12] = 1 if tcp.flags.R else 0
        
        elif UDP in pkt:
            udp = pkt[UDP]
            feat[5] = udp.sport
            feat[6] = udp.dport
        
        if Raw in pkt:
            feat[7] = len(pkt[Raw].load)
        
        if last_time:
            feat[13] = pkt.time - last_time
        
        return feat


# ============================================
# CLASSE FLOWEXTRACTOR - GERENCIA FLUXOS
# ============================================

class FlowExtractor:
    """Extrator de features por fluxo - suporta modo legado (14 features)"""
    
    def __init__(self, timeout=60, modo_legado=False):
        self.flows = {}
        self.timeout = timeout
        self.completed_flows = []
        self.modo_legado = modo_legado
        self.global_src_ports = defaultdict(set)
        self.global_dst_ports = defaultdict(set)
    
    def get_flow_key(self, pkt):
        if IP not in pkt:
            return None
        
        ip = pkt[IP]
        src_ip = ip.src
        dst_ip = ip.dst
        
        if TCP in pkt:
            proto = 6
            src_port = pkt[TCP].sport
            dst_port = pkt[TCP].dport
        elif UDP in pkt:
            proto = 17
            src_port = pkt[UDP].sport
            dst_port = pkt[UDP].dport
        elif ICMP in pkt:
            proto = 1
            src_port = 0
            dst_port = 0
        else:
            proto = 0
            src_port = 0
            dst_port = 0
        
        if src_ip < dst_ip:
            return (src_ip, dst_ip, src_port, dst_port, proto)
        else:
            return (dst_ip, src_ip, dst_port, src_port, proto)
    
    def process_packet(self, pkt, timestamp):
        key = self.get_flow_key(pkt)
        if key is None:
            return None
        
        if key not in self.flows:
            self.flows[key] = Flow(
                src_ip=key[0], dst_ip=key[1],
                src_port=key[2], dst_port=key[3],
                protocol=key[4]
            )
        
        flow = self.flows[key]
        flow.add_packet(pkt, timestamp)
        self._cleanup_old_flows(timestamp)
        
        return flow
    
    def _cleanup_old_flows(self, current_time):
        to_remove = []
        for key, flow in self.flows.items():
            if flow.last_packet_time and (current_time - flow.last_packet_time) > self.timeout:
                self.completed_flows.append(flow)
                to_remove.append(key)
        
        for key in to_remove:
            del self.flows[key]
    
    def get_completed_flows(self):
        """Retorna fluxos completados (como objetos Flow)"""
        flows = self.completed_flows.copy()
        self.completed_flows = []
        return flows
    
    def get_completed_legado_features(self):
        """Retorna features legado (14) para fluxos completados"""
        features = []
        for flow in self.completed_flows:
            features.append(flow.get_legado_features())
        
        self.completed_flows = []
        return np.array(features, dtype=np.float32)
    
    def get_feature_names(self):
        """Retorna nomes das 78 features"""
        return [
            'Flow Duration', 'Total Fwd Packets', 'Total Backward Packets',
            'Total Length of Fwd Packets', 'Total Length of Bwd Packets',
            'Fwd Packet Length Max', 'Fwd Packet Length Min',
            'Fwd Packet Length Mean', 'Fwd Packet Length Std',
            'Bwd Packet Length Max', 'Bwd Packet Length Min',
            'Bwd Packet Length Mean', 'Bwd Packet Length Std',
            'Packet Length Max', 'Packet Length Min', 'Packet Length Mean',
            'Packet Length Std', 'Packet Length Variance',
            'Flow IAT Mean', 'Flow IAT Std', 'Flow IAT Max', 'Flow IAT Min',
            'Fwd IAT Total', 'Fwd IAT Mean', 'Fwd IAT Std', 'Fwd IAT Max', 'Fwd IAT Min',
            'Bwd IAT Total', 'Bwd IAT Mean', 'Bwd IAT Std', 'Bwd IAT Max', 'Bwd IAT Min',
            'Fwd PSH Flags', 'Bwd PSH Flags', 'Fwd URG Flags', 'Bwd URG Flags',
            'FIN Flag Count', 'SYN Flag Count', 'RST Flag Count', 'PSH Flag Count',
            'ACK Flag Count', 'URG Flag Count',
            'Flow Bytes/s', 'Flow Packets/s', 'Fwd Packets/s', 'Bwd Packets/s',
            'Down/Up Ratio', 'Average Packet Size', 'Avg Fwd Segment Size',
            'Avg Bwd Segment Size', 'Fwd Header Length', 'Bwd Header Length',
            'Init_Win_bytes_forward', 'Init_Win_bytes_backward',
            'Subflow Fwd Packets', 'Subflow Fwd Bytes',
            'Subflow Bwd Packets', 'Subflow Bwd Bytes',
            'Active Mean', 'Active Std', 'Active Max', 'Active Min',
            'Idle Mean', 'Idle Std', 'Idle Max', 'Idle Min',
            'min_seg_size_forward', 'Src Port', 'Dst Port', 'Protocol'
        ]


# ============================================
# CLASSE LEGADO PARA COMPATIBILIDADE
# ============================================

class ScapyExtractor:
    """Extrator LEGADO para modelos com 14 features (por pacote)"""
    
    def __init__(self):
        self.feature_names = [
            'packet_size', 'protocol', 'ttl', 'window_size',
            'tcp_flags', 'src_port', 'dst_port', 'payload_size',
            'ip_entropy', 'flag_syn', 'flag_ack', 'flag_fin',
            'flag_rst', 'inter_arrival'
        ]
    
    def extract_from_pcap(self, pcap_path, max_packets=None):
        from scapy.all import rdpcap
        
        packets = rdpcap(str(pcap_path))
        if max_packets and len(packets) > max_packets:
            packets = packets[:max_packets]
        
        features = []
        last_time = None
        
        for pkt in packets:
            feat = self._extract_packet_features(pkt, last_time)
            features.append(feat)
            last_time = pkt.time
        
        return np.array(features, dtype=np.float32)
    
    def _extract_packet_features(self, pkt, last_time):
        feat = [0] * 14
        
        feat[0] = len(pkt)
        
        if IP in pkt:
            ip = pkt[IP]
            feat[1] = ip.proto
            feat[2] = ip.ttl
            try:
                last_octet = int(ip.src.split('.')[-1])
                feat[8] = last_octet / 255.0
            except:
                feat[8] = 0
        
        if TCP in pkt:
            tcp = pkt[TCP]
            feat[3] = tcp.window
            feat[4] = int(tcp.flags)
            feat[5] = tcp.sport
            feat[6] = tcp.dport
            feat[9] = 1 if tcp.flags.S else 0
            feat[10] = 1 if tcp.flags.A else 0
            feat[11] = 1 if tcp.flags.F else 0
            feat[12] = 1 if tcp.flags.R else 0
        
        elif UDP in pkt:
            udp = pkt[UDP]
            feat[5] = udp.sport
            feat[6] = udp.dport
        
        if Raw in pkt:
            feat[7] = len(pkt[Raw].load)
        
        if last_time:
            feat[13] = pkt.time - last_time
        
        return feat