from fastapi import APIRouter 
from app.chat_extraction.router import router as chat_extraction_router
from app.duration_prediction.router import router as duration_prediction_router

api_router = APIRouter()
api_router.include_router(chat_extraction_router)
api_router.include_router(duration_prediction_router)