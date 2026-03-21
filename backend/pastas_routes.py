# backend/pastas_routes.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import json
import threading
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from backend.dependencies import require_role

import sys
PROJECT_PATH = Path(__file__).parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.testar_com_pastas import TestadorComPastas

pastas_router = APIRouter(prefix="/sniffer", tags=["Testar com Pastas"])

MODELS_DIR  = PROJECT_PATH / "models"
DATA_DIR    = PROJECT_PATH / "data"

# ── Estado global do teste em curso ─────────────────────────
_teste_estado = {
    "a_correr":  False,
    "mensagem":  "Aguarda",
    "progresso": 0,
    "resultado": None,
    "erro":      None,
}

# ── Schema ───────────────────────────────────────────────────
class TestarPastaSchema(BaseModel):
    pasta:       str = "ambas"   # "normal", "attacks" ou "ambas"
    modelo:      Optional[str] = None
    max_pacotes: int = 5000


def get_modelo_recente():
    modelos = list(MODELS_DIR.glob("modelo_scapy_*.pkl"))
    if modelos:
        return max(modelos, key=lambda x: x.stat().st_mtime)
    best = MODELS_DIR / "best_model.pkl"
    return best if best.exists() else None


# ── Thread de teste ──────────────────────────────────────────
def _executar_teste(dados: TestarPastaSchema):
    global _teste_estado

    try:
        _teste_estado.update({
            "a_correr":  True,
            "progresso": 10,
            "mensagem":  "A inicializar testador...",
            "resultado": None,
            "erro":      None,
        })

        # determina modelo
        if dados.modelo:
            modelo_path = MODELS_DIR / dados.modelo
        else:
            modelo_path = get_modelo_recente()

        if not modelo_path or not modelo_path.exists():
            _teste_estado.update({
                "a_correr":  False,
                "progresso": 0,
                "mensagem":  "Modelo não encontrado",
                "erro":      "Nenhum modelo disponível.",
            })
            return

        testador = TestadorComPastas(modelo_path)

        _teste_estado.update({ "progresso": 30, "mensagem": "A testar PCAPs..." })

        # executa teste conforme pasta escolhida
        if dados.pasta == "normal":
            normais = testador.testar_pasta_normal(max_packets=dados.max_pacotes)
            ataques = []
        elif dados.pasta == "attacks":
            normais = []
            ataques = testador.testar_pasta_attacks(max_packets=dados.max_pacotes)
        else:
            normais, ataques = testador.testar_ambas_pastas(max_packets=dados.max_pacotes)

        _teste_estado.update({ "progresso": 80, "mensagem": "A calcular resumo..." })

        # calcula resumo
        resumo_normais = None
        if normais:
            total_pkt  = sum(r.get("total_pacotes", 0) for r in normais)
            total_anom = sum(r.get("anomalias", 0) for r in normais)
            resumo_normais = {
                "total_pcaps":    len(normais),
                "total_pacotes":  total_pkt,
                "total_anomalias": total_anom,
                "taxa_anomalia":  round(total_anom / total_pkt * 100, 2) if total_pkt > 0 else 0,
                "ficheiros":      [r.get("arquivo", "") for r in normais],
            }

        resumo_ataques = None
        if ataques:
            total_pkt  = sum(r.get("total_pacotes", 0) for r in ataques)
            total_anom = sum(r.get("anomalias", 0) for r in ataques)
            resumo_ataques = {
                "total_pcaps":    len(ataques),
                "total_pacotes":  total_pkt,
                "total_anomalias": total_anom,
                "taxa_anomalia":  round(total_anom / total_pkt * 100, 2) if total_pkt > 0 else 0,
                "ficheiros":      [r.get("arquivo", "") for r in ataques],
            }

        _teste_estado.update({
            "a_correr":  False,
            "progresso": 100,
            "mensagem":  "Teste concluído!",
            "resultado": {
                "modelo":          modelo_path.name,
                "pasta_testada":   dados.pasta,
                "normais":         resumo_normais,
                "ataques":         resumo_ataques,
                "detalhes_normais": normais,
                "detalhes_ataques": ataques,
            },
            "erro": None,
        })

    except Exception as e:
        _teste_estado.update({
            "a_correr":  False,
            "progresso": 0,
            "mensagem":  "Erro inesperado",
            "erro":      str(e),
        })


# ── ROTAS ────────────────────────────────────────────────────

@pastas_router.post("/testar/pasta")
async def testar_pasta(
    dados: TestarPastaSchema,
    usuario = Depends(require_role(["admin", "analista"]))
):
    """Testa o modelo com todos os PCAPs de uma pasta em background."""

    if _teste_estado["a_correr"]:
        raise HTTPException(
            status_code=400,
            detail="Já existe um teste em curso. Aguarda que termine."
        )

    if dados.pasta not in ["normal", "attacks", "ambas"]:
        raise HTTPException(
            status_code=400,
            detail="Pasta inválida. Usa 'normal', 'attacks' ou 'ambas'."
        )

    thread = threading.Thread(
        target=_executar_teste,
        args=(dados,),
        daemon=True
    )
    thread.start()

    return {
        "message":     "Teste iniciado!",
        "pasta":       dados.pasta,
        "max_pacotes": dados.max_pacotes,
        "modelo":      dados.modelo or "modelo mais recente",
    }


@pastas_router.get("/testar/historico")
async def get_historico(
    usuario = Depends(require_role(["admin", "analista"]))
):
    """Lista o histórico de testes guardados em JSON."""

    ficheiros = sorted(
        DATA_DIR.glob("teste_completo_*.json"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    historico = []
    for f in ficheiros[:20]:  # últimos 20
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                dados = json.load(fp)

            normais = dados.get("resultados_normais", [])
            ataques = dados.get("resultados_ataques", [])

            historico.append({
                "ficheiro":    f.name,
                "data_teste":  dados.get("data_teste", ""),
                "modelo":      Path(dados.get("modelo", "")).name,
                "n_normais":   len(normais),
                "n_ataques":   len(ataques),
                "total_pcaps": len(normais) + len(ataques),
            })
        except Exception:
            continue

    # inclui estado do teste atual se estiver a correr
    return {
        "teste_atual": {
            "a_correr":  _teste_estado["a_correr"],
            "progresso": _teste_estado["progresso"],
            "mensagem":  _teste_estado["mensagem"],
            "resultado": _teste_estado["resultado"],
            "erro":      _teste_estado["erro"],
        },
        "historico": historico,
    }