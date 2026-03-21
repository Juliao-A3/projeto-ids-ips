# backend/estatisticas_routes.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import pickle
import json
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from backend.dependencies import require_role

import sys
PROJECT_PATH = Path(__file__).parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.estatisticas_modelo import analisar_modelo, carregar_metricas_sessao

estatisticas_router = APIRouter(prefix="/sniffer/ia", tags=["IA Estatísticas"])

MODELS_DIR = PROJECT_PATH / "models"

def get_modelo_recente():
    """Retorna o modelo mais recente disponível."""
    modelos = list(MODELS_DIR.glob("modelo_scapy_*.pkl"))
    if modelos:
        return max(modelos, key=lambda x: x.stat().st_mtime)
    best = MODELS_DIR / "best_model.pkl"
    if best.exists():
        return best
    return None


@estatisticas_router.get("/estatisticas")
async def get_estatisticas(
    usuario = Depends(require_role(["admin", "analista"]))
):
    """Estatísticas completas do modelo ativo."""
    modelo_path = get_modelo_recente()

    if not modelo_path:
        raise HTTPException(status_code=404, detail="Nenhum modelo encontrado.")

    try:
        with open(modelo_path, 'rb') as f:
            modelo_data = pickle.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar modelo: {e}")

    # info do modelo
    info = {
        "nome":        modelo_path.name,
        "caminho":     str(modelo_path),
        "tamanho_kb":  round(modelo_path.stat().st_size / 1024, 2),
    }

    if isinstance(modelo_data, dict):
        info["data_treino"] = modelo_data.get("data_treino", "Desconhecida")
        info["acuracia"]    = modelo_data.get("acuracia", None)
        info["versao"]      = modelo_data.get("versao", "1.0")
        info["features"]    = modelo_data.get("feature_names", [])
        info["tipo"]        = type(modelo_data.get("modelo")).__name__ if "modelo" in modelo_data else "Desconhecido"
    else:
        info["tipo"]     = type(modelo_data).__name__
        info["features"] = list(getattr(modelo_data, "feature_names_in_", []))
        info["n_features"] = getattr(modelo_data, "n_features_in_", None)

    # histórico de sessões
    sessoes = carregar_metricas_sessao()
    historico = []
    for s in sessoes[-10:]:
        resumo = s.get("resumo", {})
        historico.append({
            "inicio":    s.get("inicio", "")[:16],
            "fim":       s.get("fim", "")[:16],
            "pacotes":   resumo.get("pacotes", 0),
            "anomalias": resumo.get("anomalias", 0),
            "bloqueios": resumo.get("bloqueios", 0),
            "ips":       resumo.get("ips", 0),
        })

    # totais acumulados
    total_pacotes   = sum(s["pacotes"]   for s in historico)
    total_anomalias = sum(s["anomalias"] for s in historico)
    total_bloqueios = sum(s["bloqueios"] for s in historico)

    return {
        "modelo":   info,
        "historico": historico,
        "totais": {
            "sessoes":   len(historico),
            "pacotes":   total_pacotes,
            "anomalias": total_anomalias,
            "bloqueios": total_bloqueios,
            "taxa_anomalia": round(
                (total_anomalias / total_pacotes * 100), 2
            ) if total_pacotes > 0 else 0,
        }
    }


@estatisticas_router.get("/modelo")
async def get_modelo_info(
    usuario = Depends(require_role(["admin", "analista"]))
):
    """Informação resumida do modelo ativo."""
    modelo_path = get_modelo_recente()

    if not modelo_path:
        raise HTTPException(status_code=404, detail="Nenhum modelo encontrado.")

    try:
        with open(modelo_path, 'rb') as f:
            modelo_data = pickle.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao carregar modelo: {e}")

    if isinstance(modelo_data, dict):
        return {
            "nome":        modelo_path.name,
            "data_treino": modelo_data.get("data_treino", "Desconhecida"),
            "acuracia":    modelo_data.get("acuracia", None),
            "versao":      modelo_data.get("versao", "1.0"),
            "n_features":  len(modelo_data.get("feature_names", [])),
            "tipo":        type(modelo_data.get("modelo")).__name__ if "modelo" in modelo_data else "Desconhecido",
        }
    else:
        return {
            "nome":       modelo_path.name,
            "tipo":       type(modelo_data).__name__,
            "n_features": getattr(modelo_data, "n_features_in_", None),
        }