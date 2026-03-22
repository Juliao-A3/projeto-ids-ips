# backend/testar_routes.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import uuid
import pickle
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from backend.dependencies import require_role

import sys
PROJECT_PATH = Path(__file__).parent.parent
sys.path.append(str(PROJECT_PATH))

from backend.scapy_module.predictor import ModelPredictor

testar_router = APIRouter(prefix="/sniffer", tags=["Testar Modelo"])

MODELS_DIR   = PROJECT_PATH / "models"
UPLOAD_DIR   = PROJECT_PATH / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ── Guarda resultados em memória 
_resultados: dict = {}


def get_modelo_recente():
    modelos = list(MODELS_DIR.glob("modelo_scapy_*.pkl"))
    if modelos:
        return max(modelos, key=lambda x: x.stat().st_mtime)
    best = MODELS_DIR / "best_model.pkl"
    return best if best.exists() else None


# ── ROTAS 

@testar_router.post("/testar/upload")
async def upload_e_testar(
    ficheiro: UploadFile = File(...),
    modelo: str = Query(None, description="Nome do modelo .pkl (opcional)"),
    usuario = Depends(require_role(["admin", "analista"]))
):
    """Faz upload de um ficheiro PCAP e testa com o modelo."""

    # valida extensão
    nome = ficheiro.filename or ""
    if not (nome.endswith(".pcap") or nome.endswith(".pcapng")):
        raise HTTPException(
            status_code=400,
            detail="Apenas ficheiros .pcap ou .pcapng são aceites."
        )

    # determina modelo
    if modelo:
        modelo_path = MODELS_DIR / modelo
    else:
        modelo_path = get_modelo_recente()

    if not modelo_path or not modelo_path.exists():
        raise HTTPException(status_code=404, detail="Nenhum modelo disponível.")

    # guarda o ficheiro uploaded
    teste_id  = str(uuid.uuid4())[:8]
    pcap_path = UPLOAD_DIR / f"{teste_id}_{nome}"

    try:
        conteudo = await ficheiro.read()
        with open(pcap_path, "wb") as f:
            f.write(conteudo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao guardar ficheiro: {e}")

    # corre o modelo
    try:
        predictor = ModelPredictor(modelo_path)
        resultado = predictor.predict_pcap(str(pcap_path))
    except Exception as e:
        pcap_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=f"Erro ao testar modelo: {e}")

    # guarda resultado
    _resultados[teste_id] = {
        "id":          teste_id,
        "ficheiro":    nome,
        "modelo":      modelo_path.name,
        "resultado":   resultado,
        "tamanho_kb":  round(len(conteudo) / 1024, 2),
    }

    # apaga ficheiro temporário
    pcap_path.unlink(missing_ok=True)

    return {
        "id":       teste_id,
        "message":  "Teste concluído com sucesso!",
        "ficheiro": nome,
        "modelo":   modelo_path.name,
        "resultado": resultado,
    }


@testar_router.get("/testar/resultado/{teste_id}")
async def get_resultado(
    teste_id: str,
    usuario = Depends(require_role(["admin", "analista"]))
):
    """Devolve o resultado de um teste anterior pelo ID."""

    if teste_id not in _resultados:
        raise HTTPException(
            status_code=404,
            detail=f"Resultado '{teste_id}' não encontrado."
        )

    return _resultados[teste_id]