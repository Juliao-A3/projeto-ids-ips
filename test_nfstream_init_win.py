import pickle
from pathlib import Path

modelo_path = Path("models/random_forest_server_model_20.pkl")
if modelo_path.exists():
    with open(modelo_path, 'rb') as f:
        dados = pickle.load(f)
    
    print("📂 Feature names no modelo:")
    features = dados.get('feature_names', [])
    print(f"   Total: {len(features)}")
    for i, f in enumerate(features, 1):
        print(f"      {i:2d}. {f}")
    
    print("\n📊 Modelo info:")
    print(f"   Acurácia: {dados.get('acuracia', '?')}")
    print(f"   Tiene scaler: {'Sim' if dados.get('scaler') else 'Não'}")
else:
    print("❌ Modelo não encontrado")