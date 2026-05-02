"""
extractor.py — Mapeamento das chaves do cicflowmeter → nomes do modelo (CIC-IDS 2018)
O cicflowmeter devolve chaves em lowercase_underscore.
O modelo espera "Title Case With Spaces" exactamente como no dataset.
"""

try:
    from . import predictor as _predictor
except ImportError:
    import predictor as _predictor

feature_names = getattr(_predictor, "feature_names", [])  # 78 features do ids_features.pkl

# Mapeamento cicflowmeter → CIC-IDS 2018
_MAP = {
    "dst_port":        "Dst Port",
    "protocol":        "Protocol",
    "flow_duration":   "Flow Duration",
    "tot_fwd_pkts":    "Tot Fwd Pkts",
    "tot_bwd_pkts":    "Tot Bwd Pkts",
    "totlen_fwd_pkts": "TotLen Fwd Pkts",
    "totlen_bwd_pkts": "TotLen Bwd Pkts",
    "fwd_pkt_len_max": "Fwd Pkt Len Max",
    "fwd_pkt_len_min": "Fwd Pkt Len Min",
    "fwd_pkt_len_mean":"Fwd Pkt Len Mean",
    "fwd_pkt_len_std": "Fwd Pkt Len Std",
    "bwd_pkt_len_max": "Bwd Pkt Len Max",
    "bwd_pkt_len_min": "Bwd Pkt Len Min",
    "bwd_pkt_len_mean":"Bwd Pkt Len Mean",
    "bwd_pkt_len_std": "Bwd Pkt Len Std",
    "flow_byts_s":     "Flow Byts/s",
    "flow_pkts_s":     "Flow Pkts/s",
    "flow_iat_mean":   "Flow IAT Mean",
    "flow_iat_std":    "Flow IAT Std",
    "flow_iat_max":    "Flow IAT Max",
    "flow_iat_min":    "Flow IAT Min",
    "fwd_iat_tot":     "Fwd IAT Tot",
    "fwd_iat_mean":    "Fwd IAT Mean",
    "fwd_iat_std":     "Fwd IAT Std",
    "fwd_iat_max":     "Fwd IAT Max",
    "fwd_iat_min":     "Fwd IAT Min",
    "bwd_iat_tot":     "Bwd IAT Tot",
    "bwd_iat_mean":    "Bwd IAT Mean",
    "bwd_iat_std":     "Bwd IAT Std",
    "bwd_iat_max":     "Bwd IAT Max",
    "bwd_iat_min":     "Bwd IAT Min",
    "fwd_psh_flags":   "Fwd PSH Flags",
    "bwd_psh_flags":   "Bwd PSH Flags",
    "fwd_urg_flags":   "Fwd URG Flags",
    "bwd_urg_flags":   "Bwd URG Flags",
    "fwd_header_len":  "Fwd Header Len",
    "bwd_header_len":  "Bwd Header Len",
    "fwd_pkts_s":      "Fwd Pkts/s",
    "bwd_pkts_s":      "Bwd Pkts/s",
    "pkt_len_min":     "Pkt Len Min",
    "pkt_len_max":     "Pkt Len Max",
    "pkt_len_mean":    "Pkt Len Mean",
    "pkt_len_std":     "Pkt Len Std",
    "pkt_len_var":     "Pkt Len Var",
    "fin_flag_cnt":    "FIN Flag Cnt",
    "syn_flag_cnt":    "SYN Flag Cnt",
    "rst_flag_cnt":    "RST Flag Cnt",
    "psh_flag_cnt":    "PSH Flag Cnt",
    "ack_flag_cnt":    "ACK Flag Cnt",
    "urg_flag_cnt":    "URG Flag Cnt",
    "cwr_flag_count":  "CWE Flag Count",
    "ece_flag_cnt":    "ECE Flag Cnt",
    "down_up_ratio":   "Down/Up Ratio",
    "pkt_size_avg":    "Pkt Size Avg",
    "fwd_seg_size_avg":"Fwd Seg Size Avg",
    "bwd_seg_size_avg":"Bwd Seg Size Avg",
    "fwd_byts_b_avg":  "Fwd Byts/b Avg",
    "fwd_pkts_b_avg":  "Fwd Pkts/b Avg",
    "fwd_blk_rate_avg":"Fwd Blk Rate Avg",
    "bwd_byts_b_avg":  "Bwd Byts/b Avg",
    "bwd_pkts_b_avg":  "Bwd Pkts/b Avg",
    "bwd_blk_rate_avg":"Bwd Blk Rate Avg",
    "subflow_fwd_pkts":"Subflow Fwd Pkts",
    "subflow_fwd_byts":"Subflow Fwd Byts",
    "subflow_bwd_pkts":"Subflow Bwd Pkts",
    "subflow_bwd_byts":"Subflow Bwd Byts",
    "init_fwd_win_byts":"Init Fwd Win Byts",
    "init_bwd_win_byts":"Init Bwd Win Byts",
    "fwd_act_data_pkts":"Fwd Act Data Pkts",
    "fwd_seg_size_min": "Fwd Seg Size Min",
    "active_mean":     "Active Mean",
    "active_std":      "Active Std",
    "active_max":      "Active Max",
    "active_min":      "Active Min",
    "idle_mean":       "Idle Mean",
    "idle_std":        "Idle Std",
    "idle_max":        "Idle Max",
    "idle_min":        "Idle Min",
}

# Alias comuns para diferencas de nomes entre versoes do cicflowmeter.
_ALIASES = {
    "cwr_flag_count": "cwr_flag_count",
    "cwe_flag_count": "cwr_flag_count",
    "fwd_header_length": "fwd_header_len",
    "bwd_header_length": "bwd_header_len",
}


def _normalize_key(key: str) -> str:
    return (
        str(key)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
    )


def _safe(val, default=0.0):
    try:
        v = float(val)
        return default if (v != v) else v   # NaN → 0
    except (TypeError, ValueError):
        return default


def extrair_features(flow_data: dict) -> dict:
    """
    Recebe o dicionário do cicflowmeter (chaves lowercase)
    e devolve as 78 features com os nomes exactos do modelo CIC-IDS 2018.
    """
    # ── DEBUG: mostra o que o cicflowmeter enviou ──
    print(f"[Extractor] Chaves recebidas: {list(flow_data.keys())}")
    print(f"[Extractor] src={flow_data.get('src_ip')} dst={flow_data.get('dst_ip')} port={flow_data.get('dst_port')}")
    print(f"[Extractor] tot_fwd_pkts={flow_data.get('tot_fwd_pkts')} tot_bwd_pkts={flow_data.get('tot_bwd_pkts')}")
    print(f"[Extractor] syn_flag_cnt={flow_data.get('syn_flag_cnt')} rst_flag_cnt={flow_data.get('rst_flag_cnt')}")
    print(f"[Extractor] flow_duration={flow_data.get('flow_duration')}")
    # 
    normalized = {
        _normalize_key(k): v
        for k, v in (flow_data or {}).items()
    }

    def _get_flow_value(cic_key: str):
        nkey = _normalize_key(cic_key)
        if nkey in normalized:
            return normalized[nkey]
        alias_key = _ALIASES.get(nkey)
        if alias_key and alias_key in normalized:
            return normalized[alias_key]
        return 0.0

    # Converte chaves cicflowmeter → nomes do modelo
    convertido = {
        cic_nome: _safe(_get_flow_value(cic_key))
        for cic_key, cic_nome in _MAP.items()
    }

    # Garante a ordem exacta das 78 features do modelo
    return {feat: convertido.get(feat, 0.0) for feat in feature_names}


class FlowExtractor:
    """
    Backward-compatible flow extractor for packet-level processing.
    Accumulates packets and computes flow statistics.
    """
    def __init__(self):
        self.flows = {}
    
    def process_packet(self, pkt, pkt_time):
        """Process a single packet and accumulate flow statistics."""
        try:
            from scapy.IP import IP
            from scapy.TCP import TCP
            from scapy.UDP import UDP
        except ImportError:
            from scapy.layers.inet import IP, TCP, UDP
        
        if IP not in pkt:
            return
        
        ip_layer = pkt[IP]
        src_ip = ip_layer.src
        dst_ip = ip_layer.dst
        protocol = ip_layer.proto
        
        src_port = 0
        dst_port = 0
        if TCP in pkt:
            src_port = pkt[TCP].sport
            dst_port = pkt[TCP].dport
        elif UDP in pkt:
            src_port = pkt[UDP].sport
            dst_port = pkt[UDP].dport
        
        flow_key = (src_ip, dst_ip, src_port, dst_port, protocol)
        
        if flow_key not in self.flows:
            self.flows[flow_key] = {
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'src_port': src_port,
                'dst_port': dst_port,
                'protocol': protocol,
                'packets': [],
                'bytes': 0,
                'start_time': pkt_time,
                'end_time': pkt_time,
            }
        
        self.flows[flow_key]['packets'].append(len(pkt))
        self.flows[flow_key]['bytes'] += len(pkt)
        self.flows[flow_key]['end_time'] = pkt_time
    
    def get_completed_flows(self):
        """Return list of completed flows with computed features."""
        result = []
        for flow_key, flow_data in self.flows.items():
            flow_dict = dict(flow_data)
            flow_dict.pop('packets', None)
            result.append(flow_dict)
        
        self.flows.clear()
        return result
    
    def get_feature_names(self):
        """Return list of feature names."""
        return list(feature_names)