from typing import Dict, List, Optional 
from pydantic import BaseModel, ConfigDict, Field

class ChatExtractRequest(BaseModel):
    # validasi bahwa harus benar-benar ada karakter huruf sebelum diteruskan ke Gemini
    model_config = ConfigDict(str_strip_whitespace=True)

    raw_chat: str = Field(
        ..., # Field wajib diisi, kalau berupa request kosong, maka tidak akan diteruskan ke Gemini
        min_length=10, # Minimal 10 Karakter, supaya teks asal kayak "tes" tidak terkirim
        description='Raw copy-paste atau ringkasan percakapan dengan pelanggan di WhatsApp',
        examples=[ # contoh buat tes di Swagger UI 
            "Customer: siang min mau nanya klo bikin kaos warna item trus sablon logo PT di depan belakang kena brp ya? Admin: Halo kak, buat sablon depan belakang dengan depan ukuran A4 dan belakang ukuran A3 kena di 80 ribu per pcs kak Customer: bahannya apa ya min? Admin: untuk bahan kita menggunakan cotton combed 30s kak Customer: oke deh min mau pesen 130 pcs yang ukuran M 30 pcs untuk ukuran L 50 pcs dan XL 50 pcs Admin: Siap kak, ada tambahan lain? Customer: Sama sekalian topi item deh min kena berapa per pcs nya? Admin: untuk topi kita all size ada di 30 ribu per pcs kak Customer: oke sekalian pesen juga berarti 100 pcs ya min Admin: baik kak, atas nama siapa dan dikirim ke mana ya kak? Customer: atas nama Verdy PT ANUGRA UTAMA MAKMUR Kirim ke JALAN PANGERAN JAYAKARTA KOMPLEK 123 NO. 10, RW. 07 RT. 006 Kec. SAWAH BESAR JAKARTA PUSAT - 10730"
        ] 
    )

class CustomerInfo(BaseModel):
    customer_name: Optional[str] = Field(
        default=None, description='Nama Pelanggan/PIC Pesanan, null jika tidak disebutkan'
    )
    company_name: Optional[str] = Field(
        default=None, description='Nama Perusahaan/instansi/komunitas pelanggan, null jika tidak disebutkan'
    )
    phone_number: Optional[str] = Field(
        default=None, description='Nomor Telepon Pelanggan, null jika tidak disebutkan'
    )
    shipping_address: Optional[str] = Field(
        default=None, description='Alamat pengiriman lengkap, null jika tidak disebutkan'
    )

class OrderItem(BaseModel):
    product_type: str = Field(
        ..., description='Jenis Produk, misal: Kaos (Short Sleeve, Long Sleeve), Kaos Polo, Topi, Hoodie, Topi, Tas'
    )
    material: Optional[str] = Field(
        default=None, description="Jenis bahan, misal: Cotton Combed 24s, Lacoste CVC, Topi Jaring (Trucker)"
    )
    color: Optional[str] = Field(
        default=None, description="Warna produk, misal: Hitam Solid, Navy Tua, Hijau Army"
    )
    customization_type: Optional[str] = Field(
        default=None, description="Jenis kustomisasi: Sablon Plastisol, Sablon DTF, Bordir Komputer, Polos"
    )
    customization_notes: Optional[str] = Field(
        default=None, description="""
        Detail posisi sablon: 
        1. jika pelanggan menyebutkan posisi di depan (dada kiri), maka isi key `customization_notes` dengan label 1
        2. jika pelanggan menyebutkan posisi di depan (dada kiri) dan dengan ukuran A4 di belakang/punggung, maka isi key `customization_notes` dengan label 2
        3. jika pelanggan menyebutkan posisi di depan (dada kiri) dan dengan ukuran A3 di belakang/punggung, maka isi key `customization_notes` dengan label 3
        4. jika pelanggan menyebutkan posisi di depan saja (bukan di dada kiri) dengan ukuran 28x10 cm, maka isi key `customization_notes` dengan label 4
        5. jika pelanggan menyebutkan posisi di depan saja (bukan di dada kiri) dengan ukuran A4, maka isi key `customization_notes` dengan label 5
        6. jika pelanggan menyebutkan posisi di depan saja (bukan di dada kiri) dengan ukuran A3, maka isi key `customization_notes` dengan label 6
        7. jika pelanggan menyebutkan posisi di depan dan belakang dengan ukuran A4, maka isi key `customization_notes` dengan label 7
        8. jika pelanggan menyebutkan posisi di depan dengan ukuran A4 dan belakang dengan ukuran A3, maka isi key `customization_notes` dengan label 8
        9. jika pelanggan menyebutkan posisi di depan dan belakang dengan ukuran A3, maka isi key `customization_notes` dengan label 9
        """
    )
    size_breakdown: Dict[str, int] = Field(
        ...,
        description="Rincian jumlah per ukuran yang dipesan saja (misal {'M': 30, 'L': 40}) atau {'All Size': 50} untuk produk tanpa ukuran baju",
    )

# class blueprint supaya response Gemini persis seperti di class ini
class ChatExtractResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_info": {
                    "customer_name": "Budi Santoso",
                    "company_name": "PT Maju Bersama Sejahtera",
                    "phone_number": "081234567890",
                    "shipping_address": "Jl. Sudirman Kav. 45, Gedung Graha Mandiri Lt. 8, Jakarta Selatan",
                },
                "deadline_requested": "2026-12-05",
                "items": [
                    {
                        "product_type": "Kaos",
                        "material": "Cotton Combed 24s",
                        "color": "Hitam",
                        "customization_type": "Sablon Plastisol",
                        "customization_notes": "Logo perusahaan di dada kiri (8x8 cm) + tulisan 'Family Gathering 2026' di punggung",
                        "size_breakdown": {"M": 30, "L": 40, "XL": 15},
                    },
                    {
                        "product_type": "Kaos",
                        "material": "Cotton Combed 24s",
                        "color": "Hitam",
                        "customization_type": "Sablon Plastisol",
                        "customization_notes": "Logo dada kiri",
                        "size_breakdown": {"M": 10, "L": 20, "XL": 15},
                    },
                    {
                        "product_type": "Kaos Polo",
                        "material": "Cotton Combed 24s",
                        "color": "Navy",
                        "customization_type": "Bordir Komputer",
                        "customization_notes": "Bordir logo dada kiri + bordir teks kecil di lengan kanan",
                        "size_breakdown": {"M": 10, "L": 15, "XL": 5},
                    },
                    {
                        "product_type": "Topi",
                        "material": None,
                        "color": "Hitam-Putih",
                        "customization_type": "Bordir Komputer",
                        "customization_notes": "Bordir logo di bagian depan tengah topi",
                        "size_breakdown": {"All Size": 50},
                    },
                ],
                "notes": "Pesanan untuk acara Company Gathering akhir tahun. Sudah deal harga nego via WA."
            }
        }
    )

    customer_info: CustomerInfo
    deadline_requested: Optional[str] = Field(
        default=None, description="Target tanggal selesai harus anda konversi ke dalam format YYYY-MM-DD jika disebutkan, atau null jika tidak disebutkan"
    )
    items: List[OrderItem]
    notes: Optional[str] = Field(
        default=None, description="Catatan tambahan pesanan misal untuk acara apa"
    )

class ErrorResponse(BaseModel):
    status: str = "Error"
    detail: str