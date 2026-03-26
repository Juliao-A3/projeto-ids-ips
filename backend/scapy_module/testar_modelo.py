# backend/scapy_module/testar_modelo.py
# Testa um PCAP específico com análise por fluxos (78 features)

import sys
from pathlib import Path
import argparse

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.predictor import ModelPredictor
from backend.scapy_module.extractor import FlowExtractor
from scapy.all import rdpcap

def testar_pcap_especifico(pcap_path, modelo_path=None, max_packets=None):
    """
    Testa um PCAP específico com análise por fluxos
    """
    print("\n" + "="*80)
    print(f"🔍 TESTAR PCAP: {pcap_path}")
    print("="*80)
    
    # 1. Carregar modelo
    predictor = ModelPredictor(modelo_path)
    
    # 2. Ler PCAP
    pcap_path = Path(pcap_path)
    if not pcap_path.exists():
        print(f"❌ PCAP não encontrado: {pcap_path}")
        return None
    
    packets = rdpcap(str(pcap_path))
    print(f"📦 Pacotes lidos: {len(packets)}")
    
    if max_packets and len(packets) > max_packets:
        packets = packets[:max_packets]
        print(f"   Usando {max_packets} pacotes")
    
    # 3. Extrair fluxos
    print("\n🔄 A extrair fluxos...")
    flow_extractor = FlowExtractor()
    
    for i, pkt in enumerate(packets):
        flow_extractor.process_packet(pkt, pkt.time)
        if (i+1) % 1000 == 0:
            print(f"   Processados {i+1} pacotes...")
    
    # 4. Obter fluxos completados
    flows = flow_extractor.get_completed_flows()
    print(f"📊 Fluxos extraídos: {len(flows)}")
    
    # 5. Classificar fluxos
    print("\n🤖 A classificar fluxos...")
    
    resultados = {
        'total_fluxos': 0,
        'normais': 0,
        'anomalias': 0,
        'detalhes': []
    }
    
    for flow in flows:
        pred, score = predictor.predict_flow(flow)
        
        resultados['total_fluxos'] += 1
        if pred == 1:  # normal
            resultados['normais'] += 1
        else:  # anomalia
            resultados['anomalias'] += 1
            resultados['detalhes'].append({
                'src_ip': flow.src_ip,
                'dst_ip': flow.dst_ip,
                'src_port': flow.src_port,
                'dst_port': flow.dst_port,
                'protocolo': flow.protocol,
                'duration': flow.end_time - flow.start_time if flow.start_time else 0,
                'packets': flow.total_packets,
                'bytes': flow.total_bytes,
                'score': float(score)
            })
    
    # 6. Mostrar resultados
    print("\n" + "="*80)
    print("📊 RESULTADOS DA ANÁLISE")
    print("="*80)
    print(f"📦 Total fluxos: {resultados['total_fluxos']}")
    print(f"✅ Normais: {resultados['normais']} ({resultados['normais']/resultados['total_fluxos']*100:.2f}%)")
    print(f"⚠️ Anomalias: {resultados['anomalias']} ({resultados['anomalias']/resultados['total_fluxos']*100:.2f}%)")
    
    if resultados['detalhes']:
        print("\n🔍 Primeiras 5 anomalias:")
        for i, anom in enumerate(resultados['detalhes'][:5]):
            print(f"   {i+1}. {anom['src_ip']}:{anom['src_port']} → {anom['dst_ip']}:{anom['dst_port']} "
                  f"[{anom['protocolo']}] - {anom['packets']} pacotes, {anom['bytes']} bytes")
    
    return resultados

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Testar PCAP com análise por fluxos')
    parser.add_argument('pcap', help='Caminho do arquivo PCAP')
    parser.add_argument('--modelo', '-m', help='Caminho do modelo .pkl')
    parser.add_argument('--limite', '-l', type=int, help='Limite de pacotes')
    
    args = parser.parse_args()
    
    testar_pcap_especifico(args.pcap, args.modelo, args.limite)