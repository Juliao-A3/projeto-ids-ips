from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend.dependencies import require_role

import io as _io

PROJECT_PATH = Path(__file__).parent.parent
treinar_router = APIRouter(prefix="/sniffer/ia", tags=["IA Treinar"])
_treino_estado = {"a_correr": False}

FEATURE_COLS_TREINO = [
    "duration", "packet_count", "byte_count",
    "src_port", "dst_port", "protocol",
    "flag_syn", "flag_ack", "flag_fin", "flag_rst",
    "pkt_size_mean", "pkt_size_std",
    "inter_arrival_mean", "inter_arrival_std",
]


@treinar_router.post("/treinar-csv")
async def treinar_com_csv(
    ficheiros: Optional[List[UploadFile]] = File(None),
    ficheiro: Optional[UploadFile] = File(None),
    contamination: float      = 0.15,
    test_size:     float      = 0.25,
    usuario = Depends(require_role(["admin"]))
):
    """
    Treina um novo modelo Isolation Forest a partir de um CSV com features.
    O CSV pode conter uma coluna 'label' (0=normal, 1=ataque) para calcular
    a acurácia no conjunto de teste — se não existir, usa unsupervised eval.
    """
    if _treino_estado["a_correr"]:
        raise HTTPException(status_code=400, detail="Já existe um treino em curso.")

    upload_files: List[UploadFile] = list(ficheiros or [])
    if ficheiro is not None:
        upload_files.append(ficheiro)
    if not upload_files:
        raise HTTPException(status_code=400, detail="Envie pelo menos um ficheiro .csv.")

    for f in upload_files:
        if not f.filename or not f.filename.lower().endswith(".csv"):
            raise HTTPException(status_code=400, detail="Apenas ficheiros .csv são aceites.")

    try:
        import pandas as pd
        import numpy as np
    except ImportError:
        raise HTTPException(status_code=500, detail="pandas/numpy não instalados.")

    dataframes = []
    for f in upload_files:
        conteudo = await f.read()
        try:
            df_item = pd.read_csv(_io.BytesIO(conteudo))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao ler CSV '{f.filename}': {e}")
        if df_item.empty:
            raise HTTPException(status_code=400, detail=f"O ficheiro CSV '{f.filename}' está vazio.")
        dataframes.append(df_item)

    df = pd.concat(dataframes, ignore_index=True)

    # ── normaliza nomes das colunas
    df.columns = [c.strip().lower() for c in df.columns]
    features_lower = [f.lower() for f in FEATURE_COLS_TREINO]

    ausentes = [f for f in features_lower if f not in df.columns]
    if ausentes:
        raise HTTPException(
            status_code=422,
            detail=f"Colunas de features em falta: {ausentes}"
        )

    # ── extrai X e y (label opcional)
    try:
        X = df[features_lower].astype(float).values
        y = df["label"].astype(int).values if "label" in df.columns else None
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Erro ao preparar dados: {e}")

    # ── valida parâmetros
    if not (0.01 <= contamination <= 0.5):
        raise HTTPException(status_code=400, detail="contamination deve estar entre 0.01 e 0.50.")
    if not (0.1 <= test_size <= 0.5):
        raise HTTPException(status_code=400, detail="test_size deve estar entre 0.1 e 0.50.")

    # ── treino síncrono (CSV é geralmente pequeno, não precisa de thread)
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler
        from datetime import datetime
        import pickle

        # split
        if y is not None:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
        else:
            X_train, X_test = train_test_split(X, test_size=test_size, random_state=42)
            y_train = y_test = None

        # scaler
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train)
        X_test_s  = scaler.transform(X_test)

        # treino
        model = IsolationForest(
            contamination=contamination,
            n_estimators=200,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_train_s)

        # avaliação
        preds = model.predict(X_test_s)   # 1 = normal, -1 = anomalia
        preds_bin = (preds == -1).astype(int)  # 1=anomalia, 0=normal

        if y_test is not None:
            from sklearn.metrics import accuracy_score
            acuracia = float(accuracy_score(y_test, preds_bin))
        else:
            # sem labels → unsupervised: % de "normais" na predição
            acuracia = float((preds == 1).sum() / len(preds))

        # guarda modelo
        MODELS_DIR = PROJECT_PATH / "models"
        MODELS_DIR.mkdir(parents=True, exist_ok=True)

        ts         = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_modelo = f"modelo_scapy_{ts}_csv.pkl"
        modelo_path = MODELS_DIR / nome_modelo

        pacote = {
            "modelo":        model,
            "scaler":        scaler,
            "feature_names": features_lower,
            "acuracia":      acuracia,
            "data_treino":   datetime.now().isoformat(),
            "versao":        "1.0",
            "origem":        "csv",
        }
        with open(modelo_path, "wb") as fp:
            pickle.dump(pacote, fp)

        return {
            "message":   "Treino CSV concluído com sucesso!",
            "modelo":    nome_modelo,
            "ficheiros": [f.filename for f in upload_files],
            "total_ficheiros": len(upload_files),
            "amostras":  len(X),
            "n_features": len(features_lower),
            "acuracia":  round(acuracia * 100, 2),
            "tem_labels": y is not None,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro durante o treino: {e}")