import sys
import os
import warnings
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Silence all sklearn parallel warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.utils.parallel")

# Permite imports "backend.*" mesmo quando o servidor é iniciado dentro de backend/.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import backend.sniffer_routes as sniffer_routes
from backend.ai_routes import ai_router
from backend.auth_routes import auth_router
from backend.dependencies import get_session
from backend.estatisticas_routes import estatisticas_router
from backend.inspecionar_routes import inspecionar_router
from backend.monitor_routes import monitor_router
from backend.network_routes import network_router
from backend.notification_routes import notification_router
from backend.pastas_routes import pastas_router
from backend.reports_routes import reports_router
from backend.service_routes import service_router
from backend.sniffer_routes import sniffer_router
from backend.testar_routes import testar_router
from backend.treinar_routes import treinar_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    sniffer_routes._session_factory = get_session
    yield
    if sniffer_routes._ips_instance and sniffer_routes._ips_instance.running:
        sniffer_routes._ips_instance.parar()

app = FastAPI(title="AEGIS IDS/IPS", version="4.0.2", lifespan=lifespan)

_default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]
_env_origins = os.getenv("FRONTEND_ORIGINS", "")
_allowed_origins = [o.strip() for o in _env_origins.split(",") if o.strip()] or _default_origins
_allowed_origin_regex = os.getenv("CORS_ALLOW_ORIGIN_REGEX") or None

app.add_middleware(CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=_allowed_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(monitor_router)
app.include_router(service_router)
app.include_router(ai_router)
app.include_router(notification_router)
app.include_router(network_router)
app.include_router(reports_router)
app.include_router(sniffer_router)
app.include_router(estatisticas_router)
app.include_router(inspecionar_router)
app.include_router(treinar_router)
app.include_router(testar_router)
app.include_router(pastas_router)