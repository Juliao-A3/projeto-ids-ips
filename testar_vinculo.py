# testar_vinculo.py
print("1. Testando imports...")
from backend.scapy_module.extractor import ScapyExtractor
print("   ✅ extractor.py OK")

from backend.scapy_module.predictor import ModelPredictor
print("   ✅ predictor.py OK")

from backend.scapy_module.sniffer_realtime import IPSRealtime
print("   ✅ sniffer_realtime.py OK")

# from backend.notification_service import notification_service
# print("   ✅ notification_service.py OK")

print("\n2. Testando carregamento do modelo...")
p = ModelPredictor()
print(f"   ✅ Modelo carregado: {p.model_path}")

print("\n3. Testando extrator...")
e = ScapyExtractor()
print(f"   ✅ Extrator configurado com {len(e.feature_names)} features")

print("\n✅ TUDO VINCULADO CORRETAMENTE!")