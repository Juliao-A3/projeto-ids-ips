# backend/treinar_routes.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import asyncio
import threading
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from backend.dependencies import require_role

import sys
PROJECT_PATH = Path(__file__).parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.train_new_model import NovoModeloTrainer

treinar_router = APIRouter(prefix="/sniffer/ia", tags=["IA Treino"])

# ── Estado global do treino ──────────────────────────────────
_treino_estado = {
    "a_correr":   False,
    "progresso":  0,
    "mensagem":   "Aguarda",
    "acuracia":   None,
    "erro":       None,
    "modelo":     None,
    "inicio":     None,
    "fim":        None,
}

# ── Schemas ──────────────────────────────────────────────────
class TreinarSchema(BaseModel):
    origem: str = "logs"          # "logs" ou "pcaps"
    contamination: float = 0.15   # percentagem de anomalias esperada
    test_size: float = 0.25       # percentagem para teste
    max_amostras: int = 5000      # máximo de amostras a usar


# ── Thread de treino ─────────────────────────────────────────
def _executar_treino(dados: TreinarSchema):
    global _treino_estado

    try:
        _treino_estado.update({
            "a_correr":  True,
            "progresso": 5,
            "mensagem":  "A inicializar trainer...",
            "erro":      None,
            "acuracia":  None,
            "modelo":    None,
        })

        trainer = NovoModeloTrainer()

        # 1 — carregar dados
        _treino_estado.update({ "progresso": 20, "mensagem": "A carregar dados..." })

        if dados.origem == "pcaps":
            X, y = trainer.preparar_dados_pcaps()
        else:
            X, y = trainer.carregar_logs_sniffer(max_entries=dados.max_amostras)

        if X is None or y is None:
            _treino_estado.update({
                "a_correr":  False,
                "progresso": 0,
                "mensagem":  "Sem dados",
                "erro":      "Não foram encontrados dados para treinar. Verifica se existem logs ou PCAPs.",
            })
            return

        _treino_estado.update({
            "progresso": 50,
            "mensagem":  f"Dados carregados: {len(X)} amostras. A treinar modelo...",
        })

        # 2 — treinar
        resultado = trainer.treinar_novo_modelo(
            X, y,
            contamination = dados.contamination,
            test_size      = dados.test_size,
        )

        if resultado is None:
            _treino_estado.update({
                "a_correr":  False,
                "progresso": 0,
                "mensagem":  "Erro no treino",
                "erro":      "O treino falhou. Verifica os dados.",
            })
            return

        model, acuracia = resultado

        # 3 — encontra o modelo guardado
        modelos = list((PROJECT_PATH / "models").glob("modelo_scapy_*.pkl"))
        modelo_novo = max(modelos, key=lambda x: x.stat().st_mtime).name if modelos else None

        _treino_estado.update({
            "a_correr":  False,
            "progresso": 100,
            "mensagem":  "Treino concluído com sucesso!",
            "acuracia":  round(acuracia * 100, 2),
            "modelo":    modelo_novo,
            "erro":      None,
        })

    except Exception as e:
        _treino_estado.update({
            "a_correr":  False,
            "progresso": 0,
            "mensagem":  "Erro inesperado",
            "erro":      str(e),
        })


# ── ROTAS ────────────────────────────────────────────────────

@treinar_router.post("/treinar")
async def iniciar_treino(
    dados: TreinarSchema,
    usuario = Depends(require_role(["admin"]))
):
    """Inicia o treino de um novo modelo em background."""

    if _treino_estado["a_correr"]:
        raise HTTPException(
            status_code=400,
            detail="Já existe um treino em curso. Aguarda que termine."
        )

    if dados.origem not in ["logs", "pcaps"]:
        raise HTTPException(
            status_code=400,
            detail="Origem inválida. Usa 'logs' ou 'pcaps'."
        )

    if not (0.01 <= dados.contamination <= 0.5):
        raise HTTPException(
            status_code=400,
            detail="Contamination deve estar entre 0.01 e 0.50."
        )

    # arranca treino em thread separada
    thread = threading.Thread(
        target=_executar_treino,
        args=(dados,),
        daemon=True
    )
    thread.start()

    return {
        "message": "Treino iniciado!",
        "origem":        dados.origem,
        "contamination": dados.contamination,
        "test_size":     dados.test_size,
        "max_amostras":  dados.max_amostras,
    }


@treinar_router.get("/treino/status")
async def status_treino(
    usuario = Depends(require_role(["admin", "analista"]))
):
    """Estado atual do treino em curso ou do último treino."""
    return {
        "a_correr":  _treino_estado["a_correr"],
        "progresso": _treino_estado["progresso"],
        "mensagem":  _treino_estado["mensagem"],
        "acuracia":  _treino_estado["acuracia"],
        "modelo":    _treino_estado["modelo"],
        "erro":      _treino_estado["erro"],
    }