import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("qaos_oms_ai_engine.api")

app = FastAPI(
    title="OMS AI Service API - PT QA'OS Kreasi Indonesia",
    description=(
        "REST API layanan AI untuk ekstraksi teks percakapan WhatsApp berbasis LLM "
        "ke format JSON terstruktur dan estimasi durasi produksi berbasis Machine Learning."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Model-Used"],
)

@app.get(
    "/health",
    tags=["System"],
    summary="Health Check Layanan AI"
)
def health_check():
    return {"status": "healthy", "service": "oms-AI-service"}

app.include_router(api_router, prefix="/api/v1")