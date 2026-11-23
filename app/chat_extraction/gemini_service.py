import json
import logging
from typing import Any, Dict, Tuple

from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.chat_extraction.schemas import ChatExtractResponse
from app.core.config import settings 

logger = logging.getLogger('oms_ai_service.gemini')

PRIMARY_MODEL = settings.GEMINI_PRIMARY_MODEL
FALLBACK_MODEL = settings.GEMINI_FALLBACK_MODEL
FALLBACK_MODEL_2 = settings.GEMINI_FALLBACK_MODEL_2

client = genai.Client(api_key=settings.GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
Kamu adalah asisten ekstraksi data pesanan untuk PT QA'OS Kreasi Indonesia (bisnis sablon dan bordir).
Tugasmu mengekstrak teks percakapan mentah atau ringkasan percakapan dengan pelanggan di WhatsApp menjadi objek JSON terstruktur.

ATURAN WAJIB:
1. ANTI-HALUSINASI: Jangan pernah mengarang data. Jika informasi (seperti nama pelanggan (customer name), nama perusahaan (company name), nomor HP, alamat pengiriman, bahan/material, warna, tanggal deadline, atau catatan tambahan) tidak disebutkan, wajib isi dengan `null`.
2. Buat objek terpisah di dalam `items` untuk setiap kombinasi unik dari 5 atribut berikut:
   - `product_type`
   - `material`
   - `color`
   - `customization_type`
   - `customization_notes`
   Jika salah satu saja dari kelima atribut tersebut berbeda (misal produk dan warna sama, tetapi desain/posisi sablonnya berbeda), wajib dipisah menjadi objek key items baru.
3. ATURAN UKURAN (`size_breakdown`):
Hanya cantumkan ukuran yang benar-benar dipesan dengan `quantity` > 0.
4. Apabila teks input sama sekali tidak memuat rincian pemesanan produk, kembalikan array `items` kosong `[]`.
""".strip()

# convention PEP 8 _namafunction artinya ini function internal/private atau helper function lah gampangnya
def _sanitize_size_breakdown(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Membersihkan key ukuran bernilai < 0 dan memastikan seluruh nilai kuantitas bertipe int.
    """
    for item in data.get("items", []):
        raw_sizes = item.get('size_breakdown', {})
        if isinstance(raw_sizes, list):
            item["size_breakdown"] = [
                {"size": str(entry["size"]), "quantity": int(entry["quantity"])}
                for entry in raw_sizes if isinstance(entry, dict) 
                and entry.get("size") 
                and isinstance(entry.get("quantity"), (int, float))
                and int(entry["quantity"]) > 0
            ]
    return data

def _invoke_gemini(model_name: str, raw_chat:str) -> Dict[str, Any]:
    response = client.models.generate_content(
        model=model_name, 
        contents=f'Ekstrak informasi pesanan dari percakapan berikut:\n\n{raw_chat}',
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type='application/json',
            response_schema=ChatExtractResponse,
            temperature=0.1,
        )
    )

    if not response.text:
        raise ValueError(f'Model {model_name} mengembalikan respons kosong.')

    parsed_data = json.loads(response.text)       
    return _sanitize_size_breakdown(parsed_data)

def extract_order_from_chat(raw_chat: str) -> Tuple[Dict[str, Any], str]:
    models_to_try = []
    for m in (PRIMARY_MODEL, FALLBACK_MODEL, FALLBACK_MODEL_2):
        if m and m not in models_to_try:
            models_to_try.append(m)

    for idx, model_name in enumerate(models_to_try):
        try:
            logger.info("Mengekstrak chat menggunakan model: %s", model_name)
            result = _invoke_gemini(model_name, raw_chat)
            return result, model_name
        except APIError as err:
            is_last_model = idx == len(models_to_try) - 1
            if err.code in (429, 503) and not is_last_model:
                logger.warning(
                    "Model %s terkena status %s (%s). Melakukan fallback ke %s...",
                    model_name,
                    err.code,
                    err.message,
                    models_to_try[idx + 1],
                )
                continue
            raise

