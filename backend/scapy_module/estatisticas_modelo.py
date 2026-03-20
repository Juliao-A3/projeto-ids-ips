# backend/scapy_module/estatisticas_modelo.py
# Script para ver estatísticas detalhadas do modelo

import pickle
import numpy as np
from pathlib import Path
import sys
from datetime import datetime
import json

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.predictor import ModelPredictor
from backend.scapy_module.extractor import ScapyExtractor

def carregar_metricas_sessao():
    """Carrega métricas da última sessão do IPS"""
    logs_dir = PROJECT_PATH / "data" / "logs"
    sessoes_file = logs_dir / "sessoes.json"
    
    if sessoes_file.exists():
        with open(sessoes_file, 'r') as f:
            return json.load(f)
    return []

def analisar_modelo(caminho_modelo=None):
    """
    Analisa o modelo e mostra estatísticas detalhadas
    """
    print("="*80)
    print("📊 ESTATÍSTICAS DO MODELO")
    print("="*80)
    
    # Converter para Path se for string
    if caminho_modelo is not None:
        caminho_modelo = Path(caminho_modelo)
    
    # Se não especificar modelo, procura o mais recente
    if caminho_modelo is None or not caminho_modelo.exists():
        models_dir = PROJECT_PATH / "models"
        modelos = list(models_dir.glob("modelo_scapy_*.pkl"))
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
    
    # Se for dicionário (como o teu)
    if isinstance(modelo_data, dict):
        print(f"📋 Nome: {caminho_modelo.name}")
        print(f"📅 Data treino: {modelo_data.get('data_treino', 'Desconhecida')}")
        print(f"🎯 Acurácia: {modelo_data.get('acuracia', 'Desconhecida')}")
        print(f"🔢 Versão: {modelo_data.get('versao', '1.0')}")
        
        # Features
        if 'feature_names' in modelo_data:
            features = modelo_data['feature_names']
            print(f"\n📋 FEATURES USADAS ({len(features)})")
            print("-" * 40)
            for i, feat in enumerate(features):
                print(f"   {i:2d}. {feat}")
        
        # Extrair modelo interno para mais info
        if 'modelo' in modelo_data:
            modelo_interno = modelo_data['modelo']
            if hasattr(modelo_interno, 'n_features_in_'):
                print(f"\n📊 Features esperadas: {modelo_interno.n_features_in_}")
    
    # Se for modelo direto
    else:
        print(f"📋 Nome: {caminho_modelo.name}")
        print(f"📦 Tipo: {type(modelo_data).__name__}")
        
        if hasattr(modelo_data, 'n_features_in_'):
            print(f"📊 Features esperadas: {modelo_data.n_features_in_}")
        
        if hasattr(modelo_data, 'feature_names_in_'):
            features = list(modelo_data.feature_names_in_)
            print(f"\n📋 FEATURES USADAS ({len(features)})")
            print("-" * 40)
            for i, feat in enumerate(features):
                print(f"   {i:2d}. {feat}")
    
    # Carregar histórico de sessões
    sessoes = carregar_metricas_sessao()
    if sessoes:
        print(f"\n📊 HISTÓRICO DE SESSÕES (últimas 5)")
        print("-" * 40)
        
        for sessao in sessoes[-5:]:
            inicio = sessao.get('inicio', '')[:16]
            resumo = sessao.get('resumo', {})
            print(f"   📅 {inicio}")
            print(f"      📦 Pacotes: {resumo.get('pacotes', 0)}")
            print(f"      ⚠️ Anomalias: {resumo.get('anomalias', 0)}")
            print(f"      🔒 Bloqueios: {resumo.get('bloqueios', 0)}")
            print(f"      🚫 IPs: {resumo.get('ips', 0)}")
    
    print("\n" + "="*80)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Estatísticas do modelo')
    parser.add_argument('--modelo', '-m', help='Caminho específico do modelo .pkl')
    parser.add_argument('--detalhes', '-d', action='store_true', help='Mostrar detalhes completos')
    
    args = parser.parse_args()
    
    analisar_modelo(args.modelo)

if __name__ == "__main__":
    main()