#Script para INSPECIONAR o teu modelo .pkl e descobrir as features usadas

import pickle
from pathlib import Path
import sys

PROJECT_PATH = Path(__file__).parent.parent.parent
MODELO_PATH = PROJECT_PATH / "models" / "best_model.pkl"

def inspecionar_modelo(caminho_modelo=None):
    """
    Inspeciona um modelo .pkl e mostra informações sobre as features
    """
    if caminho_modelo is None:
        caminho_modelo = MODELO_PATH
    
    print("="*80)
    print("🔍 INSPEÇÃO DO MODELO")
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
    
    # CASO 1: É um dicionário (mais comum)
    if isinstance(modelo, dict):
        print("\n📋 Chaves encontradas no dicionário:")
        for chave in modelo.keys():
            print(f"   🔑 {chave}")
            if chave == 'feature_names':
                features = modelo[chave]
                info['feature_names'] = features
                info['num_features'] = len(features)
                print(f"      → {len(features)} features encontradas!")
                for i, f in enumerate(features[:10]):
                    print(f"         {i:2d}. {f}")
                if len(features) > 10:
                    print(f"         ... e mais {len(features)-10}")
            
            elif chave == 'acuracia':
                info['acuracia'] = modelo[chave]
                print(f"      → Acurácia: {modelo[chave]}")
            
            elif chave == 'modelo' and hasattr(modelo[chave], 'n_features_in_'):
                info['n_features_in'] = modelo[chave].n_features_in_
                print(f"      → Modelo interno espera: {modelo[chave].n_features_in_} features")
    
    # CASO 2: É objeto sklearn direto
    elif hasattr(modelo, 'n_features_in_'):
        info['n_features_in'] = modelo.n_features_in_
        print(f"\n✅ Modelo sklearn direto")
        print(f"   Número de features esperadas: {modelo.n_features_in_}")
        
        if hasattr(modelo, 'feature_names_in_'):
            info['feature_names'] = list(modelo.feature_names_in_)
            print(f"   Nomes das features: {list(modelo.feature_names_in_)}")
    
    # CASO 3: Não tem informação direta
    else:
        print("\n⚠️ Modelo não contém informação de features diretamente")
        print("   Atributos disponíveis:")
        for attr in dir(modelo):
            if not attr.startswith('_') and not callable(getattr(modelo, attr)):
                print(f"   - {attr}")
    
    print("\n" + "="*80)
    print("📊 RESUMO DA INSPEÇÃO")
    print("="*80)
    
    if 'num_features' in info:
        print(f"✅ O teu modelo usa {info['num_features']} features")
        print(f"\n📋 Para usar este modelo no extractor.py, copia estas linhas:")
        print("\n```python")
        print("self.feature_names = [")
        for i, f in enumerate(info['feature_names']):
            print(f"    '{f}',      # {i}")
        print("]")
        print("```")
    elif 'n_features_in' in info:
        print(f"✅ O teu modelo espera {info['n_features_in']} features")
        print(f"\n⚠️ Mas não temos os nomes das features.")
        print(f"   Precisas verificar no teu código de treino original.")
    else:
        print("❌ Não foi possível determinar as features do modelo")
        print("   Vais precisar do teu código de treino original para saber")
    
    if 'acuracia' in info:
        print(f"\n🎯 Acurácia: {info['acuracia']}")
    
    return info

if __name__ == "__main__":
    # Se passarem um caminho como argumento
    if len(sys.argv) > 1:
        caminho = Path(sys.argv[1])
        inspecionar_modelo(caminho)
    else:
        inspecionar_modelo()