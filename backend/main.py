from fastapi import FastAPI  
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# middleware SEMPRE antes dos routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # url do teu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.auth_routes import auth_router
from backend.service_routes import service_router
from backend.monitor_routes import monitor_router
from backend.ai_routes import ai_router
from backend.notification_routes import notification_router
from backend.reports_routes import reports_router
from backend.network_routes import network_router

app.include_router(network_router)
app.include_router(reports_router)
app.include_router(notification_router)
app.include_router(auth_router)
app.include_router(service_router)
app.include_router(monitor_router)
app.include_router(ai_router)