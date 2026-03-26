# backend/scapy_module/estatisticas_modelo.py
# Estatísticas do modelo (agora com 78 features)

import pickle
import json
from pathlib import Path
import sys
from datetime import datetime

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

def carregar_metricas_sessao():
    """Carrega métricas da última sessão do IPS"""
    logs_dir = PROJECT_PATH / "data" / "logs"
    sessoes_file = logs_dir / "sessoes.json"
    
    if sessoes_file.exists():
        try:
            with open(sessoes_file, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

def analisar_modelo(caminho_modelo=None):
    """
    Analisa o modelo e mostra estatísticas detalhadas
    """
    print("="*80)
    print("📊 ESTATÍSTICAS DO MODELO (FLUXOS - 78 FEATURES)")
    print("="*80)
    
    # Converter para Path se for string
    if caminho_modelo is not None:
        caminho_modelo = Path(caminho_modelo)
    
    # Se não especificar modelo, procura o mais recente
    if caminho_modelo is None:
        models_dir = PROJECT_PATH / "models"
        modelos = list(models_dir.glob("modelo_fluxo_*.pkl")) + list(models_dir.glob("modelo_principal.pkl"))
        if modelos:
            caminho_modelo = max(modelos, key=lambda x: x.stat().st_mtime)
            print(f"📂 Usando modelo mais recente: {caminho_modelo.name}")
        else:
            print("❌ Nenhum modelo encontrado!")
            return
    else:
        print(f"📂 Analisando modelo: {caminho_modelo.name}")
    
    # Carregar modelo
    try:
        with open(caminho_modelo, 'rb') as f:
            modelo_data = pickle.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        return
    
    print(f"\n📦 INFORMAÇÕES DO MODELO")
    print("-" * 40)
    
    # Se for dicionário
    if isinstance(modelo_data, dict):
        print(f"📋 Nome: {caminho_modelo.name}")
        print(f"📅 Data treino: {modelo_data.get('data_treino', 'Desconhecida')}")
        print(f"🎯 Acurácia: {modelo_data.get('acuracia', 'Desconhecida')}")
        print(f"🔢 Versão: {modelo_data.get('versao', '1.0')}")
        print(f"📊 Features: {modelo_data.get('n_features', 'Desconhecido')}")
        
        # Mostrar primeiras features
        if 'feature_names' in modelo_data:
            features = modelo_data['feature_names']
            print(f"\n📋 PRIMEIRAS 15 FEATURES (de {len(features)})")
            print("-" * 40)
            for i, feat in enumerate(features[:15]):
                print(f"   {i:2d}. {feat}")
            if len(features) > 15:
                print(f"   ... e mais {len(features)-15} features")
    
    # Carregar histórico de sessões
    sessoes = carregar_metricas_sessao()
    if sessoes:
        print(f"\n📊 HISTÓRICO DE SESSÕES (últimas 5)")
        print("-" * 40)
        
        for sessao in sessoes[-5:]:
            inicio = sessao.get('inicio', '')[:16]
            resumo = sessao.get('resumo', {})
            print(f"   📅 {inicio}")
            print(f"      📦 Fluxos: {resumo.get('fluxos', 0)}")
            print(f"      ⚠️ Anomalias: {resumo.get('anomalias', 0)}")
            print(f"      🔒 Bloqueios: {resumo.get('bloqueios', 0)}")
            print(f"      🚫 IPs: {resumo.get('ips', 0)}")
    
    print("\n" + "="*80)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Estatísticas do modelo')
    parser.add_argument('--modelo', '-m', help='Caminho específico do modelo .pkl')
    
    args = parser.parse_args()
    
    analisar_modelo(args.modelo)

if __name__ == "__main__":
    main()