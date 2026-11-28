from fastapi import APIRouter, HTTPException, status
from app.duration_prediction.schemas import DurationPredictRequest, DurationPredictResponse
from app.duration_prediction.prediction_service import prediction_service
from app.chat_extraction.schemas import ErrorResponse

router = APIRouter(
    prefix="/duration-prediction",
    tags=["Duration Prediction"],
)


@router.post(
    "/predict",
    response_model=DurationPredictResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validasi input gagal"},
        500: {"model": ErrorResponse, "description": "Kesalahan internal saat prediksi"},
    },
    summary="Prediksi Estimasi Durasi Produksi Pesanan",
    description="Menerima rincian item pesanan dan mengembalikan estimasi hari selesai produksi.",
)
async def predict_production_duration(payload: DurationPredictRequest):
    try:
        return prediction_service.predict(payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal memproses prediksi durasi produksi: {str(e)}",
        )