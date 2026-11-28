from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PredictionSizeItem(BaseModel):
    size: str = Field(..., description="Ukuran produk (misal: M, L, XL, All Size)")
    quantity: int = Field(..., gt=0, description="Jumlah pesanan untuk ukuran tersebut")


class PredictionOrderItem(BaseModel):
    product_type: str = Field(
        ...,
        description="Jenis produk: `Kaos`, `Kaos Polo`, `Topi`, atau `Tote Bag`"
    )
    sleeve_type: Optional[str] = Field(
        default=None,
        description="Tipe lengan: `Short Sleeve`, `Long Sleeve`, atau null"
    )
    material: Optional[str] = Field(
        default=None,
        description="Jenis bahan produk (misal: `Cotton Combed 30s`, `Lacoste Cotton Pique`, dll)"
    )
    customization_type: Optional[str] = Field(
        default=None,
        description="Jenis kustomisasi: `Sablon`, `Bordir`, atau null"
    )
    customization_notes: Optional[str] = Field(
        default=None,
        description="Kode posisi sablon/bordir: `A1` s/d `A9`, atau null"
    )
    size_breakdown: List[PredictionSizeItem] = Field(
        ...,
        min_length=1,
        description="Rincian jumlah per ukuran"
    )


class DurationPredictRequest(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "order_date": "2026-11-28",
                "items": [
                    {
                        "product_type": "Kaos",
                        "sleeve_type": "Short Sleeve",
                        "material": "Cotton Combed 30s",
                        "customization_type": "Sablon",
                        "customization_notes": "A4",
                        "size_breakdown": [
                            {"size": "M", "quantity": 30},
                            {"size": "L", "quantity": 50},
                            {"size": "XL", "quantity": 20}
                        ]
                    },
                    {
                        "product_type": "Topi",
                        "sleeve_type": None,
                        "material": "Bahan Topi Baseball",
                        "customization_type": "Bordir",
                        "customization_notes": None,
                        "size_breakdown": [
                            {"size": "All Size", "quantity": 100}
                        ]
                    }
                ]
            }
        }
    )

    order_date: Optional[str] = Field(
        default=None,
        description="Tanggal pesanan dibuat dalam format `YYYY-MM-DD` (opsional, default hari ini)"
    )
    items: List[PredictionOrderItem] = Field(
        ...,
        min_length=1,
        description="Daftar item yang dipesan dalam satu transaksi"
    )


class DurationPredictResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "estimated_days": 5,
                "estimated_completion_date": "2026-12-03",
                "total_quantity": 200,
                "model_version": "random-forest-v1"
            }
        }
    )

    estimated_days: int = Field(..., description="Estimasi durasi pengerjaan dalam hari kerja")
    estimated_completion_date: str = Field(..., description="Tanggal perkiraan selesai (YYYY-MM-DD)")
    total_quantity: int = Field(..., description="Total keseluruhan pcs dalam pesanan")
    model_version: str = Field(..., description="Identitas versi model ML yang digunakan")