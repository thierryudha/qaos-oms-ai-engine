from fastapi import APIRouter 
from app.chat_extraction.router import router as chat_extraction_router

api_router = APIRouter()
api_router.include_router(chat_extraction_router)