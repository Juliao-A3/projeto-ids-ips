#Módulo Scapy para extrair features de PCAPs (suporta .pcap e .pcapng)

from scapy.all import rdpcap, IP, TCP, UDP, ICMP, Raw
import numpy as np
import pickle
from pathlib import Path
import sys
from datetime import datetime
import json

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

class ScapyExtractor:
    """
    Extrai features de PCAP para usar com modelos Isolation Forest
    Suporta .pcap e .pcapng
    """
    
    def __init__(self, feature_names=None):
        """
        Inicializa o extrator com as features do modelo
        """
        self.project_root = PROJECT_PATH
        self.data_folder = self.project_root / "data"
        self.models_folder = self.project_root / "models"
        self.pcaps_folder = self.data_folder / "pcaps"
        
        # Criar pastas se não existirem
        self.data_folder.mkdir(exist_ok=True)
        self.models_folder.mkdir(exist_ok=True)
        self.pcaps_folder.mkdir(exist_ok=True)
        (self.pcaps_folder / "normal").mkdir(exist_ok=True)
        (self.pcaps_folder / "attacks").mkdir(exist_ok=True)
        
        print(f"📁 Projeto: {self.project_root}")
        print(f"📁 Data: {self.data_folder}")
        print(f"📁 Models: {self.models_folder}")
        print(f"📁 PCAPs: {self.pcaps_folder}")
        
        # Se não forem fornecidas features, usa um exemplo
        if feature_names is None:
            print("⚠️ Nenhuma feature fornecida! Usando exemplo de 14 features.")
            print("   Executa inspecionar_modelo.py para obter as features corretas!")
            self.feature_names = self._get_example_features()
        else:
            self.feature_names = feature_names
        
        print(f"📋 Extrator configurado com {len(self.feature_names)} features")
    
    def _get_example_features(self):
        """Retorna um exemplo de features (substituir pelas reais)"""
        return [
            'packet_size',      # 0: tamanho do pacote
            'protocol',         # 1: protocolo
            'ttl',              # 2: time to live
            'window_size',      # 3: janela TCP
            'tcp_flags',        # 4: flags TCP
            'src_port',         # 5: porta origem
            'dst_port',         # 6: porta destino
            'payload_size',     # 7: tamanho payload
            'ip_entropy',       # 8: entropia IP
            'flag_syn',         # 9: SYN
            'flag_ack',         # 10: ACK
            'flag_fin',         # 11: FIN
            'flag_rst',         # 12: RST
            'inter_arrival'     # 13: tempo entre pacotes
        ]
    
    def extract_from_pcap(self, pcap_path, max_packets=None):
        """
        Extrai features de um arquivo PCAP (suporta .pcap e .pcapng)
        """
        print(f"📁 A ler: {pcap_path}")
        
        pcap_path = Path(pcap_path)
        if not pcap_path.exists():
            print(f"❌ Ficheiro não encontrado: {pcap_path}")
            return None
        
        # Ler pacotes (rdpcap suporta .pcap e .pcapng automaticamente)
        try:
            packets = rdpcap(str(pcap_path))
        except Exception as e:
            print(f"❌ Erro ao ler PCAP: {e}")
            return None
        
        print(f"📦 Pacotes lidos: {len(packets)}")
        
        if max_packets and len(packets) > max_packets:
            packets = packets[:max_packets]
            print(f"   Usando {max_packets} pacotes")
        
        features = []
        last_time = None
        
        for i, pkt in enumerate(packets):
            feat = self._extract_packet_features(pkt, last_time)
            features.append(feat)
            last_time = pkt.time
            
            if (i+1) % 1000 == 0:
                print(f"   Processados {i+1} pacotes...")
        
        X = np.array(features, dtype=np.float32)
        print(f"✅ Features extraídas: {X.shape}")
        
        return X
    
    def _extract_packet_features(self, pkt, last_time):
        """
        Extrai features de UM pacote
        """
        # Array de features do mesmo tamanho que feature_names
        feat = [0] * len(self.feature_names)
        
        # feature 0: packet_size
        if len(feat) > 0:
            feat[0] = len(pkt)
        
        # feature 1: protocol
        if len(feat) > 1 and IP in pkt:
            feat[1] = pkt[IP].proto
        
        # feature 2: ttl
        if len(feat) > 2 and IP in pkt:
            feat[2] = pkt[IP].ttl
        
        # feature 3: window_size (TCP)
        if len(feat) > 3 and TCP in pkt:
            feat[3] = pkt[TCP].window
        
        # feature 4: tcp_flags
        if len(feat) > 4 and TCP in pkt:
            feat[4] = int(pkt[TCP].flags)
        
        # feature 5: src_port
        if len(feat) > 5:
            if TCP in pkt:
                feat[5] = pkt[TCP].sport
            elif UDP in pkt:
                feat[5] = pkt[UDP].sport
        
        # feature 6: dst_port
        if len(feat) > 6:
            if TCP in pkt:
                feat[6] = pkt[TCP].dport
            elif UDP in pkt:
                feat[6] = pkt[UDP].dport
        
        # feature 7: payload_size
        if len(feat) > 7 and Raw in pkt:
            feat[7] = len(pkt[Raw].load)
        
        # feature 8: ip_entropy
        if len(feat) > 8 and IP in pkt:
            try:
                last_octet = int(pkt[IP].src.split('.')[-1])
                feat[8] = last_octet / 255.0
            except:
                feat[8] = 0
        
        # features 9-12: flags individuais
        if len(feat) > 9 and TCP in pkt:
            flags = pkt[TCP].flags
            feat[9] = 1 if flags.S else 0   # SYN
            if len(feat) > 10:
                feat[10] = 1 if flags.A else 0  # ACK
            if len(feat) > 11:
                feat[11] = 1 if flags.F else 0  # FIN
            if len(feat) > 12:
                feat[12] = 1 if flags.R else 0  # RST
        
        # feature 13: inter_arrival
        if len(feat) > 13 and last_time:
            feat[13] = pkt.time - last_time
        
        return feat
    
    def save_features_config(self, output_path=None):
        """
        Guarda a configuração de features num ficheiro JSON
        """
        if output_path is None:
            output_path = self.data_folder / "features_config.json"
        
        config = {
            'feature_names': self.feature_names,
            'num_features': len(self.feature_names),
            'data': datetime.now().isoformat()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        print(f"💾 Configuração de features guardada em: {output_path}")