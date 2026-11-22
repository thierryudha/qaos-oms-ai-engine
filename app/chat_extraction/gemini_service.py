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

client = genai.Client(api_key=settings.GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
Kamu adalah asisten ekstraksi data pesanan untuk PT QA'OS Kreasi Indonesia (bisnis konveksi, sablon, dan bordir).
Tugasmu mengekstrak teks percakapan mentah atau ringkasan percakapan dengan pelanggan di WhatsApp menjadi objek JSON terstruktur.

ATURAN WAJIB:
1. ANTI-HALUSINASI: Jangan pernah mengarang data. Jika informasi (seperti nama pelanggan (customer name), nama perusahaan (company name), nomor HP, alamat pengiriman, bahan, warna, tanggal deadline, atau catatan tambahan) tidak disebutkan, wajib isi dengan `null`.
2. FORMAT TANGGAL: Jika `deadline_requested` disebutkan, konversi ke format standar `YYYY-MM-DD`. Jika tidak disebutkan, isi `null`.
3. ATURAN PEMECAHAN ARRAY `items` (5 COMPOSITE KEYS):
   Buat elemen objek terpisah di dalam array `items` untuk setiap kombinasi unik dari 5 atribut berikut:
   - `product_type` (jenis produk, misal:  Kaos (Short Sleeve atau Long Sleeve), Kaos Polo (Short Sleeve), Topi (Hat), Hoodie, Tas)
   - `material` (jenis bahan kain pada kaos (Short Sleeve atau Long Sleeve) hanya Cotton Combed 30s, Kaos Polo (Short Sleeve) juga hanya Cotton Combed 30s, dan Hoodie. Jika jenis produk selain kaos dan kaos polo disebutkan yaitu Topi, Hoodie, dan Tas, isi key `material` ini dengan null saja)
   - `color` (warna produk)
   - `customization_type` (teknik kustomisasi: Sablon Plastisol, Sablon DTF, Bordir Komputer, Polos, dll.)
   - `customization_notes` (detail posisi sablon/bordir dengan aturan sebagai berikut:
   1. jika pelanggan menyebutkan posisi di depan (dada kiri), maka isi key `customization_notes` dengan label 1
   2. jika pelanggan menyebutkan posisi di depan (dada kiri) dan dengan ukuran A4 di belakang/punggung, maka isi key `customization_notes` dengan label 2
   3. jika pelanggan menyebutkan posisi di depan (dada kiri) dan dengan ukuran A3 di belakang/punggung, maka isi key `customization_notes` dengan label 3
   4. jika pelanggan menyebutkan posisi di depan saja (bukan di dada kiri) dengan ukuran 28x10 cm, maka isi key `customization_notes` dengan label 4
   5. jika pelanggan menyebutkan posisi di depan saja (bukan di dada kiri) dengan ukuran A4, maka isi key `customization_notes` dengan label 5
   6. jika pelanggan menyebutkan posisi di depan saja (bukan di dada kiri) dengan ukuran A3, maka isi key `customization_notes` dengan label 6
   7. jika pelanggan menyebutkan posisi di depan dan belakang dengan ukuran A4, maka isi key `customization_notes` dengan label 7
   8. jika pelanggan menyebutkan posisi di depan dengan ukuran A4 dan belakang dengan ukuran A3, maka isi key `customization_notes` dengan label 8
   9. jika pelanggan menyebutkan posisi di depan dan belakang dengan ukuran A3, maka isi key `customization_notes` dengan label 9
   )
   Jika salah satu saja dari kelima atribut tersebut berbeda (misal produk dan warna sama, tetapi desain/posisi sablonnya berbeda), wajib dipisah menjadi objek key items baru.
4. ATURAN UKURAN (`size_breakdown`):
   - Hanya cantumkan ukuran yang benar-benar dipesan dengan nilai bilangan bulat positif (jangan sertakan ukuran yang jumlahnya 0).
   - Untuk produk pakaian (Kaos, Kaos Polo, Hoodie, Jaket), gunakan key ukuran seperti "S", "M", "L", "XL", "XXL", dst.
   - Untuk produk tanpa ukuran baju (seperti Topi dan Tas), gunakan key `"All Size"`.
5. Apabila teks input sama sekali tidak memuat rincian pemesanan produk, kembalikan array `items` kosong `[]`.
""".strip()

# convention PEP 8 _ artinya ini function internal/private atau helper function lah gampangnya
def _sanitize_size_breakdown(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Membersihkan key ukuran bernilai < 0 dan memastikan seluruh nilai kuantitas bertipe int.
    """
    for item in data.get('items', []):
        raw_sizes = item.get('size_breakdown', {})
        if isinstance(raw_sizes, dict):
            item['size_breakdown'] = {
                str(size): int(qty)
                for size, qty in raw_sizes.items()
                if isinstance(qty, (int, float)) and int(qty) > 0
            }
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
    """
    Mengekstrak teks pesanan menggunakan model utama dengan automatic fallback
    ke seri Gemini 3.5 Flash-Lite apabila terkena rate limit (429) atau gangguan sementara (503).
    Mengembalikan tuple: (hasil_json_dict, nama_model_yang_digunakan).
    """
    try: 
        logger.info('Mengekstrak chat menggunakan model utama: %s', PRIMARY_MODEL)
        result = _invoke_gemini(PRIMARY_MODEL, raw_chat)
        return result, PRIMARY_MODEL
    except APIError as err:
        if err.code in (429, 503) and FALLBACK_MODEL != PRIMARY_MODEL:
            logger.warning(
                "Model utama %s terkena status %s (%s). Melakukan fallback ke %s...",
                PRIMARY_MODEL,
                err.code,
                err.message,
                FALLBACK_MODEL
            )
            result = _invoke_gemini(FALLBACK_MODEL, raw_chat)
            return result, FALLBACK_MODEL
        raise

