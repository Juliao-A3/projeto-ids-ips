import pandas as pd
import numpy as np
import tensorflow as tf
import pickle
import os
import warnings
from sklearn.metrics import classification_report, accuracy_score

# 1. Configurações de Ambiente
# Desativa mensagens de log do TensorFlow para o terminal ficar limpo
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore")

def executar_sistema_ids():
    # --- CAMINHOS DOS COMPONENTES SALVOS NO NOTEBOOK ---
    model_path = 'ids_deep_learning_model.keras'
    scaler_path = 'ids_scaler.pkl'
    encoder_path = 'ids_label_encoder.pkl'
    features_path = 'ids_features.pkl'
    
    # Caminho do arquivo inédito para teste
    test_csv = 'dataset_test/02-16-2018.csv'

    print("\n" + "="*60)
    print("      SISTEMA DE DETECÇÃO DE INTRUSÃO - DEEP LEARNING")
    print("="*60)

    # 2. CARREGAMENTO DOS ARQUIVOS
    if not os.path.exists(model_path):
        print(f"❌ ERRO: O arquivo do modelo ({model_path}) não foi encontrado.")
        return

    try:
        # Carregar a Rede Neural
        model = tf.keras.models.load_model(model_path)
        # Carregar os objetos de pré-processamento
        with open(scaler_path, 'rb') as f: scaler = pickle.load(f)
        with open(encoder_path, 'rb') as f: le = pickle.load(f)
        with open(features_path, 'rb') as f: feature_names = pickle.load(f)
        print("✅ Modelo e tradutores carregados com sucesso!")
    except Exception as e:
        print(f"❌ ERRO ao carregar componentes: {e}")
        return

    # 3. CARREGAMENTO E LIMPEZA DOS DADOS DE TESTE
    print(f"-> Analisando tráfego do arquivo: {test_csv}...")
    try:
        df = pd.read_csv(test_csv, low_memory=False)
        
        # Padronização de nomes (igual ao treino)
        df.columns = df.columns.str.strip()
        if 'Timestamp' in df.columns:
            df.drop(columns=['Timestamp'], inplace=True)
            
        # Selecionar as 78 colunas exatas que o modelo conhece
        X = df[feature_names].copy()
        
        # Converter para numérico e tratar lixo/infinitos
        X = X.apply(pd.to_numeric, errors='coerce').replace([np.inf, -np.inf], np.nan).fillna(0)
    except Exception as e:
        print(f"❌ ERRO ao processar dados do CSV: {e}")
        return

    # 4. NORMALIZAÇÃO E PREDIÇÃO
    print("-> Aplicando normalização e processando na Rede Neural...")
    X_scaled = scaler.transform(X)
    
    # Faz as predições (retorna probabilidades para cada uma das 8 classes)
    preds_prob = model.predict(X_scaled, batch_size=4096, verbose=0)
    # Pega o índice da classe com maior probabilidade
    preds = np.argmax(preds_prob, axis=1)

    # 5. RELATÓRIO DE SEGURANÇA
    if 'Label' in df.columns:
        print("\n" + "-"*60)
        print("           RELATÓRIO DE PERFORMANCE DA IA")
        print("-"*60)
        
        # Limpar as labels reais do CSV
        y_true_text = df['Label'].astype(str).str.strip().values
        classes_treinadas = list(le.classes_)
        
        # Traduz nomes (Benign, Bot...) para os números (0, 1, 2...)
        y_true = np.array([classes_treinadas.index(l) if l in classes_treinadas else -1 for l in y_true_text])
        
        # Filtrar apenas o que o modelo conhece
        mask = y_true != -1
        y_final = y_true[mask]
        p_final = preds[mask]

        if len(y_final) > 0:
            acc = accuracy_score(y_final, p_final)
            print(f"Acurácia Geral Detectada: {acc:.4f}")
            
            print("\nDetecção Detalhada (IDS Report):")
            # Forçamos o relatório a mostrar as 8 classes (0 a 7)
            indices_labels = np.arange(len(le.classes_))
            print(classification_report(
                y_final, 
                p_final, 
                labels=indices_labels, 
                target_names=le.classes_, 
                zero_division=0
            ))
            
            # Resumo visual para a apresentação
            print("\nContagem de Eventos Identificados:")
            classes_identificadas, contagem = np.unique(preds, return_counts=True)
            for idx, qtd in zip(classes_identificadas, contagem):
                print(f"  [{le.classes_[idx]}]: {qtd} fluxos detectados")
        else:
            print("❌ Nenhuma etiqueta do CSV corresponde às classes que a IA conhece.")
    else:
        print("\nArquivo sem coluna 'Label'. Primeiras 5 detecções da IA:")
        print(le.inverse_transform(preds[:5]))

    print("\n" + "="*60)
    print("                FIM DO PROCESSAMENTO")
    print("="*60)

if __name__ == "__main__":
    executar_sistema_ids()