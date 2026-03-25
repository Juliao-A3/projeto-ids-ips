# backend/testar_routes.py
# Adicionar estes imports ao ficheiro existente:
#   from fastapi import UploadFile, File, Query
#   import pandas as pd, io, numpy as np

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import Optional
import io

from dependencies import require_role

PROJECT_PATH = Path(__file__).parent.parent
sys.path.append(str(PROJECT_PATH))

testar_router = APIRouter(prefix="/testar", tags=["Testar"])

# ── features esperadas (mesma ordem do extractor.py)
FEATURE_COLS = [
    "duration", "packet_count", "byte_count",
    "src_port", "dst_port", "protocol",
    "flag_syn", "flag_ack", "flag_fin", "flag_rst",
    "pkt_size_mean", "pkt_size_std",
    "inter_arrival_mean", "inter_arrival_std",
]


# ─────────────────────────────────────────────────────────────
# POST /testar/upload-csv
# Recebe um CSV com as 14 features, corre o predictor e retorna
# total de linhas, normais, anomalias e taxa.
# ─────────────────────────────────────────────────────────────
@testar_router.post("/upload-csv")
async def testar_csv(
    ficheiro: UploadFile = File(...),
    modelo:   Optional[str] = Query(None, description="Nome do ficheiro .pkl (opcional)"),
    usuario = Depends(require_role(["admin", "analista"]))
):
    """Analisa um CSV com features pré-extraídas usando o modelo ativo."""

    # ── validação de extensão
    if not ficheiro.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Apenas ficheiros .csv são aceites neste endpoint.")

    # ── lê conteúdo
    conteudo = await ficheiro.read()

    try:
        import pandas as pd
        import numpy as np
    except ImportError:
        raise HTTPException(status_code=500, detail="pandas/numpy não instalados no servidor.")

    try:
        df = pd.read_csv(io.BytesIO(conteudo))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler CSV: {e}")

    if df.empty:
        raise HTTPException(status_code=400, detail="O ficheiro CSV está vazio.")

    # ── verifica se as colunas existem (ignora maiúsculas)
    df.columns = [c.strip().lower() for c in df.columns]
    features_lower = [f.lower() for f in FEATURE_COLS]
    ausentes = [f for f in features_lower if f not in df.columns]
    if ausentes:
        raise HTTPException(
            status_code=422,
            detail=f"Colunas em falta no CSV: {ausentes}. "
                   f"Colunas encontradas: {list(df.columns)}"
        )

    # ── prepara matriz X
    try:
        X = df[features_lower].astype(float).values
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Erro ao converter features para float: {e}")

    # ── carrega predictor
    try:
        from scapy_module.predictor import ModelPredictor
        MODELS_DIR = PROJECT_PATH / "models"

        if modelo:
            modelo_path = MODELS_DIR / modelo
        else:
            modelo_path = MODELS_DIR / "best_model.pkl"
            if not modelo_path.exists():
                candidatos = list(MODELS_DIR.glob("modelo_scapy_*.pkl"))
                if candidatos:
                    modelo_path = max(candidatos, key=lambda x: x.stat().st_mtime)

        if not modelo_path.exists():
            raise HTTPException(status_code=404, detail="Nenhum modelo encontrado.")

        predictor = ModelPredictor(modelo_path)
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao importar predictor: {e}")

    # ── predições linha a linha
    resultados = []
    anomalias  = 0
    normais    = 0

    for i, row in enumerate(X):
        try:
            pred = predictor.predict(row)
            # ModelPredictor.predict devolve dict com 'anomalia' (bool) ou int (-1/1)
            if isinstance(pred, dict):
                is_anomalia = bool(pred.get("anomalia", False))
            else:
                is_anomalia = (pred == -1)
        except Exception:
            is_anomalia = False

        if is_anomalia:
            anomalias += 1
        else:
            normais += 1

        # monta linha de resultado (features + classificação)
        linha = {col: float(row[j]) for j, col in enumerate(features_lower)}
        linha["classificacao"] = "anomalia" if is_anomalia else "normal"
        resultados.append(linha)

    total = len(resultados)
    taxa  = round(anomalias / total * 100, 2) if total > 0 else 0.0

    return {
        "ficheiro":      ficheiro.filename,
        "total_linhas":  total,
        "normais":       normais,
        "anomalias":     anomalias,
        "taxa_anomalia": taxa,
        "modelo_usado":  modelo_path.name,
        "pacotes":       resultados,   # para o botão "EXPORTAR CSV" do frontend
    }