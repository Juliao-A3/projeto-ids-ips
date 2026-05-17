import tensorflow as tf
import pickle
import pandas as pd
import numpy as np
import time
import os

# Carregar o cérebro do IDS
model = tf.keras.models.load_model('ids_deep_learning_model.keras')
with open('ids_scaler.pkl', 'rb') as f: scaler = pickle.load(f)
with open('ids_label_encoder.pkl', 'rb') as f: le = pickle.load(f)
with open('ids_features.pkl', 'rb') as f: feature_names = pickle.load(f)

def monitorar_rede(arquivo_csv):
    print(f"\n[SISTEMA IDS ATIVADO] Monitorando: {arquivo_csv}")
    print("Pressione Ctrl+C para parar...\n")
    
    # Ler o arquivo em pedaços (chunks) para simular fluxo de dados
    for chunk in pd.read_csv(arquivo_csv, chunksize=1, low_memory=False):
        # Limpeza rápida
        chunk.columns = chunk.columns.str.strip()
        X = chunk[feature_names].apply(pd.to_numeric, errors='coerce').fillna(0)
        
        # Predição
        X_scaled = scaler.transform(X)
        pred_prob = model.predict(X_scaled, verbose=0)
        classe_idx = np.argmax(pred_prob)
        nome_classe = le.classes_[classe_idx]
        confianca = np.max(pred_prob) * 100

        # Mostrar resultado
        if nome_classe == 'Benign':
            print(f"[OK] Tráfego Normal - Confiança: {confianca:.2f}%")
        else:
            print(f"⚠️  [ALERTA DE INTRUSÃO] Detectado: {nome_classe.upper()}! - Confiança: {confianca:.2f}%")
        
        time.sleep(0.1) # Simula a velocidade da rede

if __name__ == "__main__":
    # Teste com uma amostra do arquivo de teste
    monitorar_rede('dataset_test/02-16-2018.csv')