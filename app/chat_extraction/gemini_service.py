from dataclasses import dataclass
import json
import logging
import time
from typing import Any, Dict, List, Tuple

import httpx2 # HTTP Client-nya Python
from google import genai
from google.genai import types
from google.genai.errors import APIError

from app.chat_extraction.schemas import ChatExtractResponse
from app.core.config import settings 

logger = logging.getLogger('qaos_oms_ai_engine.gemini')

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# status HTTP dari Gemini API
TRANSIENT_API_STATUS_CODES = {408, 429, 500, 502, 503, 504}

class LLMTimeoutError(Exception):
    """Dilempar ketika seluruh model LLM gagal reponse karena batas timeout"""

@dataclass(frozen=True) # decorator @dataclass ada supaya tidak perlu buat function constructor manual
class ModelCandidate:
    name: str
    timeout_ms: int    

def _get_model_candidates() -> List[ModelCandidate]:
    """Untuk menyusun urutan kandidat Model LLM & batas timeout-nya masing-masing"""
    raw_candidates = (
        ModelCandidate(settings.GEMINI_PRIMARY_MODEL, settings.GEMINI_PRIMARY_MODEL_TIMEOUT_MS),
        ModelCandidate(settings.GEMINI_FALLBACK_MODEL_1, settings.GEMINI_FALLBACK_MODEL_1_TIMEOUT_MS),
        ModelCandidate(settings.GEMINI_FALLBACK_MODEL_2, settings.GEMINI_FALLBACK_MODEL_2_TIMEOUT_MS),
    )

    # logic untuk mencegah memanggil 2 nama Model LLM yang sama 
    candidates: List[ModelCandidate] = []
    seen_models = set()

    for candidate in raw_candidates:
        if candidate.name and candidate.name not in seen_models:
            candidates.append(candidate)
            seen_models.add(candidate.name)

    return candidates

SYSTEM_INSTRUCTION = """
Kamu adalah asisten ekstraksi data pesanan untuk PT QA'OS Kreasi Indonesia (bisnis sablon dan bordir).
Tugasmu mengekstrak teks percakapan mentah atau ringkasan percakapan dengan pelanggan dari WhatsApp, menjadi objek JSON terstruktur.

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

def _sanitize_size_breakdown(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Membersihkan key ukuran bernilai < 0 dan memastikan seluruh nilai kuantitas bertipe int.
    """
    for item in data.get("items", []):
        raw_sizes = item.get("size_breakdown", [])
        if isinstance(raw_sizes, list):
            item["size_breakdown"] = [
                {
                "size": str(entry["size"]), 
                "quantity": int(entry["quantity"])
                }
                for entry in raw_sizes if isinstance(entry, dict) 
                and entry.get("size") 
                and isinstance(entry.get("quantity"), int)
                and int(entry["quantity"]) > 0
            ]

    return data

def _invoke_gemini(model_name: str, raw_chat: str, timeout_ms: int) -> Dict[str, Any]:
    response = client.models.generate_content(
        model=model_name, 
        contents=f'Ekstrak informasi pesanan dari percakapan berikut:\n\n{raw_chat}',
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type='application/json',
            response_schema=ChatExtractResponse,
            temperature=0.1,
            http_options=types.HttpOptions(
                timeout=timeout_ms,
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )
    )

    if not response.text:
        raise ValueError(f"Model {model_name} mengembalikan respons kosong.")

    parsed_data = json.loads(response.text) 
    
    return _sanitize_size_breakdown(parsed_data)

def extract_order_from_chat(raw_chat: str) -> Tuple[Dict[str, Any], str]:
    candidates = _get_model_candidates()
    if not candidates:
        raise RuntimeError("Tidak ada model Gemini yang terkonfigurasi.")

    for idx, candidate in enumerate(candidates):
        is_last_model = idx == len(candidates) - 1
        started_at = time.perf_counter()

        try:
            logger.info(
                "Mengekstrak chat menggunakan model: %s (timeout=%dms)",
                candidate.name,
                candidate.timeout_ms, 
            )
            
            result = _invoke_gemini(candidate.name, raw_chat, candidate.timeout_ms)
            elapsed_ms = (time.perf_counter() - started_at) * 1000

            logger.info(
                "Ekstraksi berhasil dengan model %s dalam %.0fms",
                candidate.name,
                elapsed_ms,
            )

            return result, candidate.name
        except httpx2.TimeoutException as timeout_err:
            elapsed_ms = (time.perf_counter() - started_at) * 1000

            # jika bukan last model, jadi is_last_model masih bernilai False
            if not is_last_model:
                next_candidate = candidates[idx + 1]
                logger.warning(
                    "Model %s timeout setelah %.0fms (batas=%dms). Fallback ke model %s (batas=%dms)...",
                    candidate.name,
                    elapsed_ms, 
                    candidate.timeout_ms,
                    next_candidate.name,
                    next_candidate.timeout_ms,
                )
                continue

            logger.error(
                "Model terakhir %s juga timeout setelah %.0fms (batas=%dms). Ekstraksi gagal total.",
                candidate.name,
                elapsed_ms,
                candidate.timeout_ms,
            )

            raise LLMTimeoutError(
                f"Seluruh model Gemini melebihi batas waktu respons (terakhir: {candidate.name}) > {candidate.timeout_ms}ms)."
            ) from timeout_err
        except APIError as err:
            elapsed_ms = (time.perf_counter() - started_at) * 1000 

            if err.code in TRANSIENT_API_STATUS_CODES and not is_last_model:
                next_candidate = candidates[idx + 1]
                logger.warning(
                    "Model %s gagal dengan status %s setelah %.0fms, dengan Message: %s. Fallback ke model %s...",
                    candidate.name,
                    err.code,
                    elapsed_ms,
                    err.message,
                    next_candidate.name,
                )
                continue

            if err.code in (408, 504):
                raise LLMTimeoutError(
                    f"Server AI timeout pada model terakhir {candidate.name} (HTTP {err.code})"
                ) from err 
            raise