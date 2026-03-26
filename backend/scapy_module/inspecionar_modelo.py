# backend/scapy_module/inspecionar_modelo.py
# Inspeciona modelos com 78 features (fluxos)

import pickle
from pathlib import Path
import sys

PROJECT_PATH = Path(__file__).parent.parent.parent
MODELO_PATH = PROJECT_PATH / "models" / "modelo_principal.pkl"

def inspecionar_modelo(caminho_modelo=None):
    """
    Inspeciona um modelo .pkl e mostra informações sobre as features
    """
    if caminho_modelo is None:
        caminho_modelo = MODELO_PATH
    
    print("="*80)
    print("🔍 INSPEÇÃO DO MODELO (FLUXOS - 78 FEATURES)")
    print("="*80)
    
    if not caminho_modelo.exists():
        print(f"❌ Modelo não encontrado em: {caminho_modelo}")
        print(f"\n📁 Pastas disponíveis em {PROJECT_PATH/'models'}:")
        for f in (PROJECT_PATH / "models").glob("*.pkl"):
            print(f"   - {f.name}")
        return None
    
    print(f"📂 A analisar: {caminho_modelo}")
    
    # Carregar modelo
    with open(caminho_modelo, 'rb') as f:
        modelo = pickle.load(f)
    
    print(f"\n📦 Tipo do objeto: {type(modelo)}")
    print("-" * 50)
    
    info = {
        'caminho': str(caminho_modelo),
        'tipo': str(type(modelo))
    }
    
    # CASO 1: É um dicionário
    if isinstance(modelo, dict):
        print("\n📋 Chaves encontradas no dicionário:")
        for chave in modelo.keys():
            print(f"   🔑 {chave}")
            
            if chave == 'feature_names':
                features = modelo[chave]
                info['feature_names'] = features
                info['num_features'] = len(features)
                print(f"      → {len(features)} features encontradas!")
                print("\n   📋 FEATURES:")
                # Mostrar primeiras 20 e últimas 20
                for i, f in enumerate(features[:20]):
                    print(f"      {i:2d}. {f}")
                if len(features) > 40:
                    print(f"      ...")
                    for i, f in enumerate(features[-20:], start=len(features)-20):
                        print(f"      {i:2d}. {f}")
                elif len(features) > 20:
                    for i, f in enumerate(features[20:], start=20):
                        print(f"      {i:2d}. {f}")
            
            elif chave == 'acuracia':
                info['acuracia'] = modelo[chave]
                print(f"      → Acurácia: {modelo[chave]}")
            
            elif chave == 'versao':
                print(f"      → Versão: {modelo[chave]}")
            
            elif chave == 'data_treino':
                print(f"      → Data treino: {modelo[chave]}")
            
            elif chave == 'n_features':
                info['n_features'] = modelo[chave]
                print(f"      → Número de features: {modelo[chave]}")
    
    # CASO 2: É objeto sklearn direto
    elif hasattr(modelo, 'n_features_in_'):
        info['n_features_in'] = modelo.n_features_in_
        print(f"\n✅ Modelo sklearn direto")
        print(f"   Número de features esperadas: {modelo.n_features_in_}")
        
        if hasattr(modelo, 'feature_names_in_'):
            info['feature_names'] = list(modelo.feature_names_in_)
            print(f"   Features: {info['feature_names'][:10]}...")
    
    print("\n" + "="*80)
    print("📊 RESUMO DA INSPEÇÃO")
    print("="*80)
    
    if 'num_features' in info:
        print(f"✅ O teu modelo usa {info['num_features']} features")
        print(f"\n📋 Para usar este modelo no extractor.py, as features devem corresponder")
    elif 'n_features_in' in info:
        print(f"✅ O teu modelo espera {info['n_features_in']} features")
    
    if 'acuracia' in info:
        print(f"\n🎯 Acurácia: {info['acuracia']}")
    
    if 'versao' in info:
        print(f"🔢 Versão: {info['versao']}")
    
    return info

if __name__ == "__main__":
    if len(sys.argv) > 1:
        caminho = Path(sys.argv[1])
        inspecionar_modelo(caminho)
    else:
        inspecionar_modelo()