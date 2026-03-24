# backend/inspecionar_routes.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pickle
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from backend.dependencies import require_role

import sys
PROJECT_PATH = Path(__file__).parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.inspecionar_modelo import inspecionar_modelo

inspecionar_router = APIRouter(prefix="/sniffer/ia", tags=["IA Inspecionar"])

MODELS_DIR = PROJECT_PATH / "models"

def get_modelo_recente():
    best = MODELS_DIR / "best_model.pkl"
    if best.exists():
        return best
    modelos = list(MODELS_DIR.glob("modelo_scapy_*.pkl"))
    if modelos:
        return max(modelos, key=lambda x: x.stat().st_mtime)
    return None

@inspecionar_router.get("/inspecionar")
async def inspecionar(
    modelo: str = Query(None, description="Nome do ficheiro .pkl (opcional)"),
    usuario = Depends(require_role(["admin", "analista"]))
):
    """Inspeciona o modelo e retorna informação detalhada sobre features."""

    # determina o caminho
    if modelo:
        modelo_path = MODELS_DIR / modelo
    else:
        # usa o mais recente
        modelos = list(MODELS_DIR.glob("modelo_scapy_*.pkl"))
        if modelos:
            modelo_path = max(modelos, key=lambda x: x.stat().st_mtime)
        else:
            modelo_path = MODELS_DIR / "best_model.pkl"

    if not modelo_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Modelo '{modelo_path.name}' não encontrado."
        )

    try:
        info = inspecionar_modelo(modelo_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao inspecionar modelo: {e}")

    if not info:
        raise HTTPException(status_code=404, detail="Não foi possível inspecionar o modelo.")

    return {
        "nome": modelo_path.name,
        "caminho": str(modelo_path),
        "tipo": info.get("tipo", "Desconhecido"),
        "n_features": info.get("num_features") or info.get("n_features_in"),
        "feature_names": info.get("feature_names", []),
        "acuracia": info.get("acuracia", None),
    }


@inspecionar_router.get("/modelos")
async def listar_modelos(
    usuario = Depends(require_role(["admin", "analista"]))
):
    """Lista todos os modelos .pkl disponíveis."""

    if not MODELS_DIR.exists():
        return {"modelos": []}

    modelos = []

    for f in sorted(MODELS_DIR.glob("*.pkl"), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            with open(f, 'rb') as fp:
                data = pickle.load(fp)

            info = {
                "nome":       f.name,
                "tamanho_kb": round(f.stat().st_size / 1024, 2),
                "modificado": f.stat().st_mtime,
            }

            if isinstance(data, dict):
                info["data_treino"] = data.get("data_treino", "Desconhecida")
                info["acuracia"]    = data.get("acuracia", None)
                info["versao"]      = data.get("versao", "1.0")
                info["n_features"]  = len(data.get("feature_names", []))
                info["tipo"]        = type(data.get("modelo")).__name__ if "modelo" in data else "Desconhecido"
            else:
                info["tipo"]       = type(data).__name__
                info["n_features"] = getattr(data, "n_features_in_", None)
                info["acuracia"]   = None

            modelos.append(info)

        except Exception:
            # ficheiro corrompido ou incompatível — adiciona mesmo assim
            modelos.append({
                "nome":       f.name,
                "tamanho_kb": round(f.stat().st_size / 1024, 2),
                "erro":       "Não foi possível carregar",
            })

    return {
        "total":   len(modelos),
        "modelos": modelos,
    }