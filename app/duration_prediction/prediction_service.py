import os
import math
from datetime import datetime, timedelta
import joblib
import pandas as pd
from app.duration_prediction.schemas import DurationPredictRequest, DurationPredictResponse

MODEL_PATH = os.path.join("models", "duration_model.joblib")


class DurationPredictionService:
    def __init__(self):
        self.model = None
        self.model_version = "baseline-heuristic-v0"
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH):
            self.model = joblib.load(MODEL_PATH)
            self.model_version = "sklearn-regressor-v1"

    def predict(self, payload: DurationPredictRequest) -> DurationPredictResponse:
        total_qty = sum(
            size_item.quantity
            for item in payload.items
            for size_item in item.size_breakdown
        )

        # Hitung estimasi tanggal mulai
        if payload.order_date:
            try:
                start_date = datetime.strptime(payload.order_date, "%Y-%m-%d")
            except ValueError:
                start_date = datetime.now()
        else:
            start_date = datetime.now()

        if self.model is not None:
            # TODO: Sesuaikan nama kolom DataFrame ini dengan fitur final hasil training DS & AE
            features_df = self._prepare_features(payload, total_qty)
            raw_pred = self.model.predict(features_df)[0]
            estimated_days = max(1, math.ceil(float(raw_pred)))
        else:
            # Baseline sementara sebelum file .joblib selesai dilatih
            has_embroidery = any(
                (item.customization_type or "").lower() == "bordir"
                for item in payload.items
            )
            base_days = math.ceil(total_qty / 40) + (2 if has_embroidery else 1)
            estimated_days = max(2, base_days)

        completion_date = (start_date + timedelta(days=estimated_days)).strftime("%Y-%m-%d")

        return DurationPredictResponse(
            estimated_days=estimated_days,
            estimated_completion_date=completion_date,
            total_quantity=total_qty,
            model_version=self.model_version,
        )

    def _prepare_features(self, payload: DurationPredictRequest, total_qty: int) -> pd.DataFrame:
        # Placeholder feature engineering
        primary_item = payload.items[0]
        return pd.DataFrame([{
            "product_type": primary_item.product_type,
            "customization_type": primary_item.customization_type or "Polos",
            "total_quantity": total_qty,
            "item_variants_count": len(payload.items)
        }])


prediction_service = DurationPredictionService()