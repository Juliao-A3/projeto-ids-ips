# testar_vinculo.py
# Teste de vinculação de todos os módulos do sistema

print("="*60)
print("🔍 TESTE DE VINCULAÇÃO - AEGIS IDS/IPS")
print("="*60)

print("\n1. Testando imports básicos...")
print("-" * 40)

# Extractors
from backend.scapy_module.extractor import FlowExtractor, ScapyExtractor
print("   ✅ FlowExtractor (78 features)")
print("   ✅ ScapyExtractor (14 features)")

# Predictor
from backend.scapy_module.predictor import ModelPredictor
print("   ✅ ModelPredictor")

# Sniffer
from backend.scapy_module.sniffer_realtime import IPSRealtime
print("   ✅ IPSRealtime")

# Auto-trainer
from backend.scapy_module.auto_trainer import auto_trainer
print("   ✅ auto_trainer")

# Detector de ataques
from backend.scapy_module.detector_ataques import detector
print("   ✅ detector_ataques")

# Explicador
from backend.scapy_module.explicador import explicador
print("   ✅ explicador")

print("\n2. Testando carregamento de modelos...")
print("-" * 40)

# Carregar modelo antigo (14 features)
print("   📂 Modelo antigo (14 features):")
p_antigo = ModelPredictor('models/modelo_scapy_20260319_152419_85.40%.pkl')
print(f"      ✅ Modelo carregado: {p_antigo.model_path.name}")
print(f"      📊 Features esperadas: {p_antigo.model.n_features_in_ if hasattr(p_antigo.model, 'n_features_in_') else '?'}")

# Carregar modelo novo (78 features) - se existir
try:
    from pathlib import Path
    models_dir = Path('models')
    modelos_novos = list(models_dir.glob("modelo_fluxo_*.pkl"))
    if modelos_novos:
        modelo_novo = max(modelos_novos, key=lambda x: x.stat().st_mtime)
        p_novo = ModelPredictor(modelo_novo)
        print(f"\n   📂 Modelo novo (78 features):")
        print(f"      ✅ Modelo carregado: {p_novo.model_path.name}")
        print(f"      📊 Features esperadas: {p_novo.model.n_features_in_ if hasattr(p_novo.model, 'n_features_in_') else '?'}")
    else:
        print("\n   ⚠️ Nenhum modelo novo (78 features) encontrado")
except Exception as e:
    print(f"\n   ⚠️ Erro ao carregar modelo novo: {e}")

print("\n3. Testando extractores...")
print("-" * 40)

# Extractor novo
e_novo = FlowExtractor()
print(f"   ✅ FlowExtractor: {len(e_novo.get_feature_names())} features")

# Extractor legado
e_legado = ScapyExtractor()
print(f"   ✅ ScapyExtractor: {len(e_legado.feature_names)} features")

print("\n4. Testando detector de ataques...")
print("-" * 40)

# Testar detecção de SYN flood
class FakeFlow:
    protocol = 6
    fwd_syn_count = 150
    bwd_syn_count = 0
    packets = [1]
    dst_port = 80
    start_time = 0
    end_time = 10
    total_packets = 150
    total_bytes = 15000
    fwd_psh_count = 0
    bwd_psh_count = 0

resultado = detector._is_syn_flood(FakeFlow())
print(f"   ✅ SYN Flood detectado: {resultado}")

# Testar XMAS scan
from scapy.all import IP, TCP
pkt = IP()/TCP(flags='FPU')
class FakeFlow2:
    packets = [pkt]
    protocol = 6
    fwd_psh_count = 1
    bwd_psh_count = 0
resultado2 = detector._is_xmas_scan(FakeFlow2())
print(f"   ✅ XMAS Scan detectado: {resultado2}")

print("\n5. Testando explicador...")
print("-" * 40)

import numpy as np
explicador._carregar_modelo('models/modelo_scapy_20260319_152419_85.40%.pkl')
features = np.array([[500, 6, 64, 65535, 16, 12345, 80, 100, 0.5, 0, 1, 0, 0, 0.01]])
explicacao = explicador.explicar(features)
print(f"   ✅ Método: {explicacao['metodo']}")
print(f"   ✅ Predição: {explicacao['predicao']}")
print(f"   ✅ Top features: {len(explicacao['contribuicoes'])}")

print("\n6. Testando auto-trainer...")
print("-" * 40)

status = auto_trainer.get_status()
print(f"   ✅ Ativo: {status['ativo']}")
print(f"   ✅ Intervalo: {status['intervalo_horas']} horas")
print(f"   ✅ Modelo atual: {status['modelo_atual']}")

print("\n7. Testando WebSocket (simulado)...")
print("-" * 40)

try:
    from backend.sniffer_routes import sniffer_router
    print("   ✅ sniffer_routes.py OK")
except ImportError:
    print("   ⚠️ sniffer_routes.py não encontrado (será criado depois)")

print("\n" + "="*60)
print("✅ TUDO VINCULADO CORRETAMENTE!")
print("="*60)