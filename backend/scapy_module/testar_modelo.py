# backend/scapy_module/testar_modelo.py
# Testa um arquivo específico: PCAP, LOG ou CSV
# Suporta modelos antigo (14 features) e novo (70 features)

import sys
from pathlib import Path
import argparse
import json
import pandas as pd
import numpy as np
import pickle

PROJECT_PATH = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.predictor import ModelPredictor
from backend.scapy_module.extractor import FlowExtractor
from scapy.all import rdpcap
from sklearn.preprocessing import StandardScaler

# Modelo antigo padrão
MODELO_PADRAO = PROJECT_PATH / "models" / "modelo_scapy_20260319_152419_85.40%.pkl"

def obter_features_modelo(modelo_path):
    """Obtém os nomes das features que o modelo espera"""
    try:
        with open(modelo_path, 'rb') as f:
            data = pickle.load(f)
        
        if isinstance(data, dict):
            # Modelo salvo como dicionário
            if 'feature_names' in data:
                return data['feature_names']
            elif 'model' in data and hasattr(data['model'], 'feature_names_in_'):
                return list(data['model'].feature_names_in_)
        
        # Se for objeto sklearn direto
        if hasattr(data, 'feature_names_in_'):
            return list(data.feature_names_in_)
        
        # Fallback: número de features
        if hasattr(data, 'n_features_in_'):
            return [f'feature_{i}' for i in range(data.n_features_in_)]
        
    except Exception as e:
        print(f"   ⚠️ Erro ao obter features: {e}")
    
    return None

def selecionar_features_para_modelo(df, modelo_path):
    """Seleciona as features corretas baseado no modelo"""
    
    # Obter features do modelo
    modelo_features = obter_features_modelo(modelo_path)
    
    if modelo_features is None:
        # Fallback: usar número de features
        n_features = obter_numero_features_modelo(modelo_path)
        print(f"   ⚠️ Usando fallback: {n_features} features")
        
        # Selecionar colunas numéricas
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        label_cols = [col for col in df.columns if 'label' in col.lower() or 'Label' in col]
        numeric_cols = [col for col in numeric_cols if col not in label_cols]
        
        X = df[numeric_cols[:n_features]].values
        return X
    
    print(f"   📋 Modelo espera {len(modelo_features)} features")
    
    # Tentar mapear features do CSV para as do modelo
    selected_cols = []
    for feat in modelo_features:
        # Procurar coluna que contenha o nome da feature
        found = False
        for col in df.columns:
            if feat.lower() in col.lower() or col.lower() in feat.lower():
                selected_cols.append(col)
                found = True
                break
        if not found:
            # Se não encontrar, usar uma coluna numérica qualquer
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                selected_cols.append(numeric_cols[0])
    
    # Se não encontrou nenhuma, usar as primeiras N colunas numéricas
    if not selected_cols:
        print("   ⚠️ Nenhuma feature mapeada. Usando colunas numéricas...")
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        label_cols = [col for col in df.columns if 'label' in col.lower() or 'Label' in col]
        numeric_cols = [col for col in numeric_cols if col not in label_cols]
        selected_cols = numeric_cols[:len(modelo_features)]
    
    X = df[selected_cols].values
    
    # Garantir número correto de features
    if X.shape[1] > len(modelo_features):
        X = X[:, :len(modelo_features)]
    elif X.shape[1] < len(modelo_features):
        pad = np.zeros((X.shape[0], len(modelo_features) - X.shape[1]))
        X = np.hstack([X, pad])
    
    print(f"   📊 Features selecionadas: {X.shape[1]}")
    
    return X

def obter_numero_features_modelo(modelo_path):
    """Retorna o número de features que o modelo espera"""
    try:
        predictor = ModelPredictor(modelo_path)
        if hasattr(predictor.model, 'n_features_in_'):
            return predictor.model.n_features_in_
        elif predictor.feature_names:
            return len(predictor.feature_names)
    except:
        pass
    return 14

def testar_arquivo(arquivo_path, modelo_path=None, limite=None):
    """
    Testa um arquivo (PCAP, LOG ou CSV) com o modelo
    """
    print("\n" + "="*80)
    print(f"🔍 TESTAR ARQUIVO: {arquivo_path}")
    print("="*80)
    
    # Usar modelo antigo como padrão
    if modelo_path is None:
        modelo_path = MODELO_PADRAO
        print(f"📂 Usando modelo padrão: {modelo_path.name}")
    
    # 1. Carregar modelo
    predictor = ModelPredictor(modelo_path)
    
    # 2. Identificar tipo de arquivo
    arquivo = Path(arquivo_path)
    extensao = arquivo.suffix.lower()
    
    if extensao in ['.pcap', '.pcapng']:
        # ========== TESTAR PCAP ==========
        print("\n📦 Tipo: PCAP")
        print("-" * 40)
        
        if not arquivo.exists():
            print(f"❌ Arquivo não encontrado: {arquivo}")
            return None
        
        packets = rdpcap(str(arquivo))
        print(f"📦 Pacotes lidos: {len(packets)}")
        
        if limite and len(packets) > limite:
            packets = packets[:limite]
            print(f"   Usando {limite} pacotes")
        
        print("\n🔄 A extrair fluxos...")
        flow_extractor = FlowExtractor()
        for i, pkt in enumerate(packets):
            flow_extractor.process_packet(pkt, pkt.time)
            if (i+1) % 1000 == 0:
                print(f"   Processados {i+1} pacotes...")
        
        flows = flow_extractor.get_completed_flows()
        print(f"📊 Fluxos extraídos: {len(flows)}")
        
        # Classificar fluxos
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
            if pred == 1:
                resultados['normais'] += 1
            else:
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
        
        # Mostrar resultados
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
    
    elif extensao == '.json':
        # ========== TESTAR LOG JSON ==========
        print("\n📊 Tipo: LOG JSON")
        print("-" * 40)
        
        if not arquivo.exists():
            print(f"❌ Arquivo não encontrado: {arquivo}")
            return None
        
        with open(arquivo, 'r') as f:
            linhas = f.readlines()
        
        if limite:
            linhas = linhas[-limite:]
        
        entradas = []
        for linha in linhas:
            try:
                entry = json.loads(linha)
                entradas.append(entry)
            except:
                continue
        
        print(f"📊 Entradas lidas: {len(entradas)}")
        
        # Analisar entradas (já têm classificação do sniffer)
        anomalias = sum(1 for e in entradas if e.get('tipo') == 'anomalia')
        
        print("\n" + "="*80)
        print("📊 RESULTADOS DA ANÁLISE")
        print("="*80)
        print(f"📦 Total entradas: {len(entradas)}")
        print(f"✅ Normais: {len(entradas) - anomalias} ({(len(entradas)-anomalias)/len(entradas)*100:.2f}%)")
        print(f"⚠️ Anomalias: {anomalias} ({anomalias/len(entradas)*100:.2f}%)")
        
        # Mostrar últimas anomalias
        if anomalias > 0:
            print("\n🔍 Últimas 5 anomalias:")
            count = 0
            for e in reversed(entradas):
                if e.get('tipo') == 'anomalia' and count < 5:
                    print(f"   {count+1}. {e.get('timestamp', '')[:19]} - {e.get('src_ip', '?')} → {e.get('dst_ip', '?')} [{e.get('protocolo', '?')}]")
                    count += 1
        
        return {'total': len(entradas), 'anomalias': anomalias}
    
    elif extensao == '.csv':
        # ========== TESTAR CSV ==========
        print("\n📄 Tipo: CSV")
        print("-" * 40)
        
        if not arquivo.exists():
            print(f"❌ Arquivo não encontrado: {arquivo}")
            return None
        
        df = pd.read_csv(arquivo, low_memory=False)
        print(f"📊 Linhas lidas: {len(df)}")
        
        if limite and len(df) > limite:
            df = df.sample(n=limite, random_state=42)
            print(f"   Usando {limite} linhas")
        
        # Tratar valores inválidos
        print("\n🔄 A processar dados...")
        df = df.replace([np.inf, -np.inf], np.nan)
        df = df.fillna(0)
        
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.fillna(0)
        
        print(f"   Dados limpos: {df.shape[0]} linhas, {df.shape[1]} colunas")
        
        # Identificar coluna de label
        label_col = None
        for col in df.columns:
            if 'label' in col.lower() or 'Label' in col:
                label_col = col
                break
        
        # Selecionar features baseado no modelo
        X = selecionar_features_para_modelo(df, modelo_path)
        
        # Verificar valores inválidos
        X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Normalizar
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        if label_col is None:
            # CSV sem label real
            print("\n⚠️ Coluna de label não encontrada. Classificando com o modelo...")
            
            y_pred = predictor.model.predict(X_scaled)
            y_pred_binary = np.where(y_pred == 1, 0, 1)
            anomalias = np.sum(y_pred_binary == 1)
            
            print("\n" + "="*80)
            print("📊 RESULTADOS DA ANÁLISE")
            print("="*80)
            print(f"📦 Total amostras: {len(X)}")
            print(f"⚠️ Anomalias detectadas: {anomalias} ({anomalias/len(X)*100:.2f}%)")
            print(f"✅ Normais: {len(X) - anomalias} ({(len(X)-anomalias)/len(X)*100:.2f}%)")
            
            return {'total': len(X), 'anomalias': anomalias}
        
        else:
            # CSV com label real
            print(f"📋 Coluna de label encontrada: {label_col}")
            
            y_true = df[label_col].apply(
                lambda x: 1 if str(x).upper() not in ['BENIGN', 'NORMAL', 'BENING'] else 0
            ).values
            
            y_pred = predictor.model.predict(X_scaled)
            y_pred_binary = np.where(y_pred == 1, 0, 1)
            
            anomalias_detectadas = np.sum(y_pred_binary == 1)
            anomalias_reais = np.sum(y_true == 1)
            acertos = np.sum(y_pred_binary == y_true)
            acuracia = acertos / len(y_true) * 100
            
            print("\n" + "="*80)
            print("📊 RESULTADOS DA ANÁLISE")
            print("="*80)
            print(f"📦 Total amostras: {len(X)}")
            print(f"\n📊 LABEL REAL:")
            print(f"   Normais: {len(y_true) - anomalias_reais} ({(len(y_true)-anomalias_reais)/len(y_true)*100:.2f}%)")
            print(f"   Anomalias: {anomalias_reais} ({anomalias_reais/len(y_true)*100:.2f}%)")
            print(f"\n🤖 CLASSIFICAÇÃO DO MODELO:")
            print(f"   Normais: {len(X) - anomalias_detectadas} ({(len(X)-anomalias_detectadas)/len(X)*100:.2f}%)")
            print(f"   Anomalias: {anomalias_detectadas} ({anomalias_detectadas/len(X)*100:.2f}%)")
            print(f"\n🎯 ACURÁCIA DO MODELO NESTE CSV: {acuracia:.2f}%")
            
            return {
                'total': len(X),
                'anomalias_detectadas': int(anomalias_detectadas),
                'anomalias_reais': int(anomalias_reais),
                'acuracia': acuracia
            }
    
    else:
        print(f"❌ Formato não suportado: {extensao}")
        print("   Formatos suportados: .pcap, .pcapng, .json, .csv")
        return None


def main():
    parser = argparse.ArgumentParser(description='Testar arquivo (PCAP, LOG ou CSV) com o modelo')
    parser.add_argument('arquivo', help='Caminho do arquivo (.pcap, .pcapng, .json, .csv)')
    parser.add_argument('--modelo', '-m', help='Caminho do modelo .pkl')
    parser.add_argument('--limite', '-l', type=int, help='Limite de pacotes/entradas/linhas')
    
    args = parser.parse_args()
    
    testar_arquivo(args.arquivo, args.modelo, args.limite)

if __name__ == "__main__":
    main()