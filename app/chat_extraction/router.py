import logging
from fastapi import APIRouter, HTTPException, Response, status
from google.genai.errors import APIError

from app.chat_extraction.gemini_service import extract_order_from_chat
from app.chat_extraction.schemas import ChatExtractRequest, ChatExtractResponse, ErrorResponse

logger = logging.getLogger("oms_ai_service.chat_extraction")
router = APIRouter()

@router.post(
    "/extract-orders",
    response_model=ChatExtractResponse,
    status_code=status.HTTP_200_OK,
    tags=["Order Extraction"],
    summary="Ekstrak Teks Percakapan WhatsApp ke JSON",
    responses={
        400: {"model": ErrorResponse, "description": "Input teks kosong atau terlalu pendek"},
        422: {"model": ErrorResponse, "description": "Tidak ditemukan rincian produk pesanan dalam teks"},
        429: {"model": ErrorResponse, "description": "Kuota API LLM terlampaui (rate limit)"},
        502: {"model": ErrorResponse, "description": "Gangguan komunikasi dengan layanan LLM eksternal"},
    }    
)
def extract_order_endpoint(payload: ChatExtractRequest, response: Response):
    cleaned_chat = payload.raw_chat.strip()
    if len(cleaned_chat) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teks percakapan terlalu pendek atau kosong. Silahkan masukkan ringkasan percakapan.",
        )
    
    try:
        extracted_data, model_used = extract_order_from_chat(cleaned_chat)

        if not extracted_data.get("items"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Tidak ditemukan rincian produk pesanan yang valid pada teks percakapan.",
            )
        
        # catat model yang digunakan di HTTP header agar JSON body tetap bersih
        response.headers["X-Model-Used"] = model_used
        return extracted_data
    
    except HTTPException:
        raise 
    except APIError as api_err:
        logger.error("Gemini API Error [%s]: %s", api_err.code, api_err.message)
        if api_err.code == 429:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Batas frekuensi penggunaan layanan AI tercapai. Silahkan coba sesaat lagi atau isi form pesanan secara manual.",
            )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Layanan AI sedang mengalami gangguan sementara.",
        )
    except Exception as exc:
        logger.exception("Unexpected error saat ekstraksi chat: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan internal pada server AI."
        )