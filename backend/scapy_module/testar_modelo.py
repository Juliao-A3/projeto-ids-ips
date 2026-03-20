# Script simples para testar modelo com um PCAP específico (suporta .pcap e .pcapng)

import sys
from pathlib import Path

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.predictor import ModelPredictor

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python testar_modelo.py <pcap_file> [modelo_path]")
        print("\nExemplos:")
        print("  python testar_modelo.py data/pcaps/normal/teste.pcap")
        print("  python testar_modelo.py data/pcaps/normal/teste.pcapng")
        print("  python testar_modelo.py data/pcaps/attacks/ataque.pcapng models/outro_modelo.pkl")
        sys.exit(1)
    
    pcap_path = sys.argv[1]
    modelo_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    predictor = ModelPredictor(modelo_path)
    predictor.predict_pcap(pcap_path)