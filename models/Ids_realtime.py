import time
import pickle
import argparse
import numpy as np
from collections import defaultdict
from datetime import datetime
from scapy.all import sniff, IP, TCP, UDP, ICMP

# ─────────────────────────────────────────────
# Configurações
# ─────────────────────────────────────────────

FLOW_TIMEOUT   = 120   # segundos sem pacote → encerra o flow
ACTIVE_TIMEOUT = 5
IDLE_TIMEOUT   = 5
ALERT_THRESHOLD = 0.7  # confiança mínima para alertar


# ─────────────────────────────────────────────
# Cores para o terminal
# ─────────────────────────────────────────────

class Color:
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    RED    = '\033[91m'
    BLUE   = '\033[94m'
    BOLD   = '\033[1m'
    RESET  = '\033[0m'

def colorize(text, color):
    return f"{color}{text}{Color.RESET}"


# ─────────────────────────────────────────────
# Estrutura de Flow
# ─────────────────────────────────────────────

class Flow:
    def __init__(self, key, timestamp):
        self.key        = key
        self.start_time = timestamp
        self.last_seen  = timestamp

        self.fwd_packets    = []
        self.bwd_packets    = []
        self.fwd_timestamps = []
        self.bwd_timestamps = []
        self.all_timestamps = [timestamp]

        self.flag_counts = {
            "FIN": 0, "SYN": 0, "RST": 0, "PSH": 0,
            "ACK": 0, "URG": 0, "CWE": 0, "ECE": 0
        }
        self.fwd_psh_flags = 0
        self.bwd_psh_flags = 0
        self.fwd_urg_flags = 0
        self.bwd_urg_flags = 0
        self.init_win_fwd  = None
        self.init_win_bwd  = None
        self.active_periods = []
        self.idle_periods   = []
        self._active_start  = timestamp

    def add_packet(self, pkt, direction, timestamp):
        size = len(pkt)
        self.last_seen = timestamp
        self.all_timestamps.append(timestamp)

        if direction == "fwd":
            self.fwd_packets.append(size)
            self.fwd_timestamps.append(timestamp)
        else:
            self.bwd_packets.append(size)
            self.bwd_timestamps.append(timestamp)

        if pkt.haslayer(TCP):
            flags = pkt[TCP].flags
            if flags & 0x01: self.flag_counts["FIN"] += 1
            if flags & 0x02: self.flag_counts["SYN"] += 1
            if flags & 0x04: self.flag_counts["RST"] += 1
            if flags & 0x08: self.flag_counts["PSH"] += 1
            if flags & 0x10: self.flag_counts["ACK"] += 1
            if flags & 0x20: self.flag_counts["URG"] += 1
            if flags & 0x40: self.flag_counts["ECE"] += 1
            if flags & 0x80: self.flag_counts["CWE"] += 1

            if flags & 0x08:
                if direction == "fwd": self.fwd_psh_flags += 1
                else: self.bwd_psh_flags += 1
            if flags & 0x20:
                if direction == "fwd": self.fwd_urg_flags += 1
                else: self.bwd_urg_flags += 1

            if direction == "fwd" and self.init_win_fwd is None:
                self.init_win_fwd = pkt[TCP].window
            if direction == "bwd" and self.init_win_bwd is None:
                self.init_win_bwd = pkt[TCP].window

        if len(self.all_timestamps) >= 2:
            gap = self.all_timestamps[-1] - self.all_timestamps[-2]
            if gap > IDLE_TIMEOUT:
                active_dur = self.all_timestamps[-2] - self._active_start
                if active_dur > 0:
                    self.active_periods.append(active_dur)
                self.idle_periods.append(gap)
                self._active_start = timestamp


# ─────────────────────────────────────────────
# Extração de Features (69 features do modelo)
# ─────────────────────────────────────────────

def safe_stats(lst):
    if not lst:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    arr = np.array(lst, dtype=float)
    return float(np.mean(arr)), float(np.std(arr)), float(np.max(arr)), float(np.min(arr)), float(np.var(arr))

def iat(timestamps):
    if len(timestamps) < 2:
        return [0.0]
    ts = sorted(timestamps)
    return list(np.diff(ts))

def extract_features(flow: Flow, feature_cols: list) -> np.ndarray:
    fwd      = flow.fwd_packets
    bwd      = flow.bwd_packets
    all_pkts = fwd + bwd

    if not all_pkts:
        return None

    duration = max(flow.last_seen - flow.start_time, 1e-9)

    flow_iat_vals = iat(flow.all_timestamps)
    fwd_iat_vals  = iat(flow.fwd_timestamps)
    bwd_iat_vals  = iat(flow.bwd_timestamps)

    flow_iat_mean, flow_iat_std, flow_iat_max, flow_iat_min, _ = safe_stats(flow_iat_vals)
    fwd_iat_mean,  fwd_iat_std,  fwd_iat_max,  fwd_iat_min,  _ = safe_stats(fwd_iat_vals)
    bwd_iat_mean,  bwd_iat_std,  bwd_iat_max,  bwd_iat_min,  _ = safe_stats(bwd_iat_vals)

    all_mean, all_std, all_max, all_min, all_var = safe_stats(all_pkts)
    fwd_mean, fwd_std, fwd_max, fwd_min, _       = safe_stats(fwd)
    bwd_mean, bwd_std, bwd_max, bwd_min, _       = safe_stats(bwd)

    total_fwd_pkts  = len(fwd)
    total_bwd_pkts  = len(bwd)
    total_fwd_bytes = sum(fwd)
    total_bwd_bytes = sum(bwd)
    total_pkts      = total_fwd_pkts + total_bwd_pkts
    total_bytes     = total_fwd_bytes + total_bwd_bytes

    act = flow.active_periods
    idle = flow.idle_periods
    act_mean,  act_std,  act_max,  act_min,  _ = safe_stats(act)  if act  else (0,0,0,0,0)
    idle_mean, idle_std, idle_max, idle_min, _ = safe_stats(idle) if idle else (0,0,0,0,0)

    proto_map = {"TCP": 6, "UDP": 17, "ICMP": 1}
    proto_num = proto_map.get(flow.key[4], 0)

    feat_dict = {
        "Protocol":                  proto_num,
        "Flow Duration":             duration * 1e6,
        "Total Fwd Packets":         total_fwd_pkts,
        "Total Backward Packets":    total_bwd_pkts,
        "Fwd Packets Length Total":  total_fwd_bytes,
        "Bwd Packets Length Total":  total_bwd_bytes,
        "Fwd Packet Length Max":     fwd_max,
        "Fwd Packet Length Min":     fwd_min,
        "Fwd Packet Length Mean":    fwd_mean,
        "Fwd Packet Length Std":     fwd_std,
        "Bwd Packet Length Max":     bwd_max,
        "Bwd Packet Length Min":     bwd_min,
        "Bwd Packet Length Mean":    bwd_mean,
        "Bwd Packet Length Std":     bwd_std,
        "Flow Bytes/s":              total_bytes  / duration,
        "Flow Packets/s":            total_pkts   / duration,
        "Flow IAT Mean":             flow_iat_mean,
        "Flow IAT Std":              flow_iat_std,
        "Flow IAT Max":              flow_iat_max,
        "Flow IAT Min":              flow_iat_min,
        "Fwd IAT Total":             sum(fwd_iat_vals),
        "Fwd IAT Mean":              fwd_iat_mean,
        "Fwd IAT Std":               fwd_iat_std,
        "Fwd IAT Max":               fwd_iat_max,
        "Fwd IAT Min":               fwd_iat_min,
        "Bwd IAT Total":             sum(bwd_iat_vals),
        "Bwd IAT Mean":              bwd_iat_mean,
        "Bwd IAT Std":               bwd_iat_std,
        "Bwd IAT Max":               bwd_iat_max,
        "Bwd IAT Min":               bwd_iat_min,
        "Fwd PSH Flags":             flow.fwd_psh_flags,
        "Bwd PSH Flags":             flow.bwd_psh_flags,
        "Fwd URG Flags":             flow.fwd_urg_flags,
        "Bwd URG Flags":             flow.bwd_urg_flags,
        "Fwd Header Length":         total_fwd_pkts * 40,
        "Bwd Header Length":         total_bwd_pkts * 40,
        "Fwd Packets/s":             total_fwd_pkts / duration,
        "Bwd Packets/s":             total_bwd_pkts / duration,
        "Packet Length Min":         all_min,
        "Packet Length Max":         all_max,
        "Packet Length Mean":        all_mean,
        "Packet Length Std":         all_std,
        "Packet Length Variance":    all_var,
        "FIN Flag Count":            flow.flag_counts["FIN"],
        "SYN Flag Count":            flow.flag_counts["SYN"],
        "RST Flag Count":            flow.flag_counts["RST"],
        "PSH Flag Count":            flow.flag_counts["PSH"],
        "ACK Flag Count":            flow.flag_counts["ACK"],
        "URG Flag Count":            flow.flag_counts["URG"],
        "CWE Flag Count":            flow.flag_counts["CWE"],
        "ECE Flag Count":            flow.flag_counts["ECE"],
        "Down/Up Ratio":             total_bwd_bytes / total_fwd_bytes if total_fwd_bytes > 0 else 0,
        "Avg Packet Size":           all_mean,
        "Avg Fwd Segment Size":      max(fwd_mean - 40, 0),
        "Avg Bwd Segment Size":      max(bwd_mean - 40, 0),
        "Subflow Fwd Packets":       total_fwd_pkts,
        "Subflow Fwd Bytes":         total_fwd_bytes,
        "Subflow Bwd Packets":       total_bwd_pkts,
        "Subflow Bwd Bytes":         total_bwd_bytes,
        "Init Fwd Win Bytes":        flow.init_win_fwd or 0,
        "Init Bwd Win Bytes":        flow.init_win_bwd or 0,
        "Fwd Act Data Packets":      sum(1 for s in fwd if s > 40),
        "Fwd Seg Size Min":          max(fwd_min - 40, 0),
        "Active Mean":               act_mean,
        "Active Std":                act_std,
        "Active Max":                act_max,
        "Active Min":                act_min,
        "Idle Mean":                 idle_mean,
        "Idle Std":                  idle_std,
        "Idle Max":                  idle_max,
        "Idle Min":                  idle_min,
    }

    # Ordenar features exatamente como o modelo foi treinado
    return np.array([feat_dict.get(col, 0.0) for col in feature_cols], dtype=float)


# ─────────────────────────────────────────────
# Motor de Inferência
# ─────────────────────────────────────────────

class IDSEngine:
    def __init__(self, model_path, block_mode=False):
        print(colorize(f"\n[*] Carregando modelo: {model_path}", Color.BLUE))
        with open(model_path, "rb") as f:
            data = pickle.load(f)

        self.model         = data["model"]
        self.scaler        = data["scaler"]
        self.label_encoder = data["label_encoder"]
        self.feature_cols  = data["feature_cols"]
        self.block_mode    = block_mode

        self.flows         = {}
        self.stats         = defaultdict(int)
        self.alert_count   = 0

        print(colorize(f"[✓] Modelo carregado: {data['model_name']}", Color.GREEN))
        print(colorize(f"[✓] Classes: {list(self.label_encoder.classes_)}", Color.GREEN))
        print(colorize(f"[✓] Features: {len(self.feature_cols)}", Color.GREEN))
        if block_mode:
            print(colorize("[⚠️] Modo IPS ativo — flows maliciosos serão bloqueados!", Color.YELLOW))

    def get_flow_key(self, pkt):
        if not pkt.haslayer(IP):
            return None, None
        src = pkt[IP].src
        dst = pkt[IP].dst

        if pkt.haslayer(TCP):
            sport, dport, proto = pkt[TCP].sport, pkt[TCP].dport, "TCP"
        elif pkt.haslayer(UDP):
            sport, dport, proto = pkt[UDP].sport, pkt[UDP].dport, "UDP"
        elif pkt.haslayer(ICMP):
            sport, dport, proto = 0, 0, "ICMP"
        else:
            return None, None

        canonical = (src, dst, sport, dport, proto)
        reversed_ = (dst, src, dport, sport, proto)

        if canonical in self.flows:
            return canonical, "fwd"
        elif reversed_ in self.flows:
            return reversed_, "bwd"
        return canonical, "fwd"

    def process_packet(self, pkt):
        if not pkt.haslayer(IP):
            return

        timestamp = float(pkt.time)
        key, direction = self.get_flow_key(pkt)
        if key is None:
            return

        self.check_timeouts(timestamp)

        if key not in self.flows:
            self.flows[key] = Flow(key, timestamp)

        self.flows[key].add_packet(pkt, direction, timestamp)

    def check_timeouts(self, current_time):
        expired = [
            k for k, f in self.flows.items()
            if current_time - f.last_seen > FLOW_TIMEOUT
        ]
        for k in expired:
            self.classify_flow(self.flows[k])
            del self.flows[k]

    def classify_flow(self, flow: Flow):
        features = extract_features(flow, self.feature_cols)
        if features is None:
            return

        # Normalizar
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # Classificar
        prediction = self.model.predict(features_scaled)[0]
        label = self.label_encoder.inverse_transform([prediction])[0]

        self.stats[label] += 1
        src_ip = flow.key[0]
        dst_ip = flow.key[1]
        proto  = flow.key[4]
        now    = datetime.now().strftime("%H:%M:%S")

        if label == "BENIGN":
            # Só mostra benign a cada 100 flows para não poluir o terminal
            if sum(self.stats.values()) % 100 == 0:
                print(colorize(
                    f"[{now}] ✅ BENIGN  {src_ip} → {dst_ip} ({proto})",
                    Color.GREEN
                ))
        else:
            # ALERTA de ataque!
            self.alert_count += 1
            print(colorize(
                f"\n[{now}] 🚨 ATAQUE DETETADO!",
                Color.RED + Color.BOLD
            ))
            print(colorize(
                f"         Tipo:    {label}",
                Color.RED
            ))
            print(colorize(
                f"         Origem:  {src_ip}:{flow.key[2]}",
                Color.RED
            ))
            print(colorize(
                f"         Destino: {dst_ip}:{flow.key[3]}",
                Color.RED
            ))
            print(colorize(
                f"         Proto:   {proto}",
                Color.RED
            ))

            # Modo IPS — bloquear o IP
            if self.block_mode:
                self.block_ip(src_ip, label)

    def block_ip(self, ip, attack_type):
        """Bloqueia o IP usando iptables (requer root)."""
        import subprocess
        cmd = f"iptables -A INPUT -s {ip} -j DROP"
        try:
            subprocess.run(cmd.split(), check=True)
            print(colorize(f"         🔒 IP BLOQUEADO: {ip}", Color.YELLOW))
        except Exception as e:
            print(colorize(f"         ⚠️ Erro ao bloquear {ip}: {e}", Color.YELLOW))

    def print_stats(self):
        print(colorize("\n" + "="*50, Color.BLUE))
        print(colorize("  ESTATÍSTICAS DA SESSÃO", Color.BOLD))
        print(colorize("="*50, Color.BLUE))
        total = sum(self.stats.values())
        print(f"  Total de flows analisados: {total:,}")
        print(f"  Total de alertas:          {self.alert_count:,}\n")
        for label, count in sorted(self.stats.items(), key=lambda x: -x[1]):
            pct = count / total * 100 if total > 0 else 0
            color = Color.GREEN if label == "BENIGN" else Color.RED
            print(colorize(f"  {label:<25} {count:>6,}  ({pct:.1f}%)", color))
        print(colorize("="*50 + "\n", Color.BLUE))

    def start(self, interface, packet_count=0):
        print(colorize(f"\n[*] Iniciando IDS na interface: {interface}", Color.BLUE))
        print(colorize("[*] Pressiona Ctrl+C para parar\n", Color.BLUE))
        print(colorize("="*50, Color.BLUE))

        try:
            sniff(
                iface=interface,
                prn=self.process_packet,
                count=packet_count,
                store=False
            )
        except KeyboardInterrupt:
            print(colorize("\n[*] Captura interrompida.", Color.YELLOW))
        finally:
            # Classificar flows ainda ativos
            for flow in self.flows.values():
                self.classify_flow(flow)
            self.print_stats()


# ─────────────────────────────────────────────
# Execução
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IDS/IPS em tempo real com Scapy + XGBoost")
    parser.add_argument("--interface", "-i", required=True,  help="Interface de rede (ex: eth0)")
    parser.add_argument("--model",     "-m", required=True,  help="Caminho para o best_model.pkl")
    parser.add_argument("--block",     "-b", action="store_true", help="Modo IPS: bloqueia IPs maliciosos")
    args = parser.parse_args()

    engine = IDSEngine(model_path=args.model, block_mode=args.block)
    engine.start(interface=args.interface)