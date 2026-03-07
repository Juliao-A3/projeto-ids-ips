"""
CICIDS 2017 - Pré-processamento
================================
Limpa e prepara o CSV do CICIDS 2017 para treinamento.

Problemas conhecidos do dataset que este script resolve:
  1. Valores infinitos (inf / -inf)
  2. Valores NaN
  3. Nomes de colunas com espaços extras
  4. Labels inconsistentes (ex: "BENIGN" vs "benign")
  5. Features com variância zero (inúteis pro modelo)
  6. Normalização (StandardScaler)
  7. Encoding dos labels

Uso:
    python cicids_preprocessor.py <pasta_com_csvs> <saida.pkl>

    Exemplo:
    python cicids_preprocessor.py ./cicids2017_csvs/ dataset_pronto.pkl
"""

import os
import sys
import glob
import pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split


# ─────────────────────────────────────────────
# Colunas a remover (identificação, não features)
# ─────────────────────────────────────────────
COLS_TO_DROP = [
    "src_ip", "dst_ip", "src_port", "dst_port",
    "Flow ID", "Source IP", "Destination IP",
    "Source Port", "Destination Port", "Timestamp"
]

# Coluna de label no CICIDS 2017
LABEL_COL = "Label"


# ─────────────────────────────────────────────
# 1. Carregar todos os CSVs da pasta
# ─────────────────────────────────────────────
def load_csvs(folder_path):
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"Nenhum CSV encontrado em: {folder_path}")

    print(f"[*] Encontrados {len(csv_files)} arquivos CSV:")
    dfs = []
    for f in csv_files:
        print(f"    → {os.path.basename(f)}")
        df = pd.read_csv(f, low_memory=False)
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    print(f"\n[✓] Total de amostras carregadas: {len(df):,}")
    return df


# ─────────────────────────────────────────────
# 2. Limpeza
# ─────────────────────────────────────────────
def clean(df):
    print("\n[*] Iniciando limpeza...")

    # Remover espaços dos nomes de colunas
    df.columns = df.columns.str.strip()

    # Remover colunas de identificação
    cols_drop = [c for c in COLS_TO_DROP if c in df.columns]
    df.drop(columns=cols_drop, inplace=True, errors="ignore")
    print(f"    → Colunas de identificação removidas: {cols_drop}")

    # Padronizar labels
    df[LABEL_COL] = df[LABEL_COL].str.strip().str.upper()
    print(f"    → Labels encontrados: {df[LABEL_COL].unique().tolist()}")

    # Substituir inf e -inf por NaN
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    nan_count = df.isnull().sum().sum()
    print(f"    → Valores NaN/Inf encontrados: {nan_count:,}")

    # Preencher NaN com a mediana de cada coluna
    num_cols = df.select_dtypes(include=[np.number]).columns
    df[num_cols] = df[num_cols].fillna(df[num_cols].median())
    print(f"    → NaN substituídos pela mediana")

    # Remover features com variância zero (não ajudam o modelo)
    before = df.shape[1]
    feature_cols = [c for c in df.columns if c != LABEL_COL]
    zero_var = [c for c in feature_cols if df[c].std() == 0]
    df.drop(columns=zero_var, inplace=True)
    print(f"    → Features com variância zero removidas: {zero_var}")
    print(f"    → Features restantes: {df.shape[1] - 1}")

    return df


# ─────────────────────────────────────────────
# 3. Distribuição dos labels
# ─────────────────────────────────────────────
def show_label_distribution(df):
    print("\n[*] Distribuição dos labels:")
    counts = df[LABEL_COL].value_counts()
    total = len(df)
    for label, count in counts.items():
        bar = "█" * int(count / total * 40)
        print(f"    {label:<30} {count:>8,}  ({count/total*100:.1f}%)  {bar}")


# ─────────────────────────────────────────────
# 4. Separar features e labels
# ─────────────────────────────────────────────
def split_features_labels(df):
    feature_cols = [c for c in df.columns if c != LABEL_COL]
    X = df[feature_cols].values
    y = df[LABEL_COL].values
    return X, y, feature_cols


# ─────────────────────────────────────────────
# 5. Encoding dos labels
# ─────────────────────────────────────────────
def encode_labels(y):
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    print(f"\n[*] Encoding dos labels:")
    for i, cls in enumerate(le.classes_):
        print(f"    {i} → {cls}")
    return y_encoded, le


# ─────────────────────────────────────────────
# 6. Normalização
# ─────────────────────────────────────────────
def normalize(X_train, X_test):
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test  = scaler.transform(X_test)
    return X_train, X_test, scaler


# ─────────────────────────────────────────────
# 7. Pipeline completo
# ─────────────────────────────────────────────
def preprocess(folder_path, output_path):
    # Carregar
    df = load_csvs(folder_path)

    # Limpar
    df = clean(df)

    # Distribuição
    show_label_distribution(df)

    # Separar X e y
    X, y, feature_cols = split_features_labels(df)

    # Encoding
    y_encoded, label_encoder = encode_labels(y)

    # Split treino/teste (80/20 estratificado)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded,
        test_size=0.2,
        random_state=42,
        stratify=y_encoded
    )
    print(f"\n[*] Split treino/teste:")
    print(f"    → Treino: {len(X_train):,} amostras")
    print(f"    → Teste:  {len(X_test):,} amostras")

    # Normalizar
    X_train, X_test, scaler = normalize(X_train, X_test)
    print(f"\n[✓] Normalização aplicada (StandardScaler)")

    # Salvar tudo em um arquivo .pkl
    output = {
        "X_train":       X_train,
        "X_test":        X_test,
        "y_train":       y_train,
        "y_test":        y_test,
        "feature_cols":  feature_cols,
        "label_encoder": label_encoder,
        "scaler":        scaler,
    }

    with open(output_path, "wb") as f:
        pickle.dump(output, f)

    print(f"\n[✓] Dataset pré-processado salvo em: {output_path}")
    print(f"[✓] Features finais: {len(feature_cols)}")
    print(f"[✓] Classes: {list(label_encoder.classes_)}")

    return output


# ─────────────────────────────────────────────
# Execução
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python cicids_preprocessor.py <pasta_csvs> <saida.pkl>")
        print("Exemplo: python cicids_preprocessor.py ./cicids2017/ dataset.pkl")
        sys.exit(0)

    folder = sys.argv[1]
    output = sys.argv[2]
    preprocess(folder, output)