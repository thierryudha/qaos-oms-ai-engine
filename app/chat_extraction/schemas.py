from typing import List, Optional 
from pydantic import BaseModel, ConfigDict, Field

class ChatExtractRequest(BaseModel):
    # validasi bahwa harus benar-benar ada karakter huruf sebelum diteruskan ke Gemini
    model_config = ConfigDict(str_strip_whitespace=True)

    raw_chat: str = Field(
        ..., # Field wajib diisi, kalau berupa request kosong, maka tidak akan diteruskan ke Gemini
        min_length=10, # Minimal 10 Karakter, supaya teks asal kayak "tes" tidak terkirim
        description='Raw copy-paste atau ringkasan percakapan dengan pelanggan di WhatsApp',
        examples=[ # contoh buat tes di Swagger UI 
            "Customer: siang min mau nanya klo bikin kaos lengan pendek warna navy trus sablon logo PT di depan kena brp ya? Admin: Halo kak, untuk kaos short sleeve dan sablon depan kita ada di ukuran A4 kak kena di 60 ribu per pcs kak Customer: bahannya apa ya min? Admin: untuk bahan kita menggunakan cotton combed 30s atau cotton combed 24s kak Customer: oke deh min mau pesen 130 pcs yang combed 30s yang ukuran M 30 pcs untuk ukuran L 50 pcs dan XL 20 pcs Admin: Siap kak, ada tambahan lain? Customer: Sama sekalian topi item deh min kena berapa per pcs nya? Admin: untuk topi kita ada di 30 ribu per pcs kak Customer: oke sekalian pesen juga berarti 100 pcs ya min Admin: baik kak, atas nama siapa dan dikirim ke mana ya kak? Customer: atas nama Yudha PT Indokoin Semesta 081219164263 kirim ke Sequis Tower, Jl. Jenderal Sudirman No. Kav. 71 (Lantai 7 / Lantai 25), RT.5/RW.3, Senayan, Kec. Kebayoran Baru, Kota Jakarta Selatan, DKI Jakarta 12190"
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

class SizeItem(BaseModel):
    size: str = Field(
        ...,
        description="Ukuran produk yang tersedia yaitu 'XS', 'S', 'M', 'L', 'XL', 'XXL' 'XXXL', 'XXXXL', 'XXXXXL' dan ukuran 'All Size' untuk produk Topi dan Tote Bag"
    )
    quantity: int = Field(
        ...,
        description="Jumlah pesanan untuk ukuran tersebut (bilangan bulat positif)"
    )

class OrderItem(BaseModel):
    product_type: str = Field(
        ..., description="""Jenis Produk yang tersedia yaitu: Kaos dan Kaos Polo dengan varian Short Sleeve & Long Sleeve, 
                            jadi tulis secara detail, jika disebutkan variannya Short Sleeve atau Long Sleeve. Misal:
                            'Kaos (Short Sleeve)' atau 'Kaos Polo (Long Sleeve)'. Selain itu juga terdapat produk Topi dan Tote Bag"""
    )
    material: Optional[str] = Field(
        default=None, description="""Jenis bahan yang tersedia yaitu: untuk Kaos (Short Sleeve) menggunakan bahan Cotton Combed 24s, 
                                    tersedia juga untuk Kaos (Short Sleeve & Long Sleeve) dengan bahan Cotton Combed 30s.
                                    Lalu untuk Kaos Polo (Short Sleeve & Long Sleeve) terdapat varian bahan Polyester atau Lacoste Cotton Pique.
                                    Lalu untuk Topi, isi bahan/material dengan 'Bahan Topi Baseball' dan untuk produk Tote Bag menggunakan bahan Kanvas"""
    )
    color: Optional[str] = Field(
        default=None, description="""
        Warna yang tersedia yaitu:
        Abu Tua
        Merah Maron
        Putih Bersih
        Hitam Solid
        Mustard
        Navy Tua
        Hijau Army
        Merah Solid
        Abu Misty M71
        Biru Turkish
        Biru Benhur
        Hijau Botol
        Orange
        Pink Baby
        Kuning Kenari
        Coklat Tua
        Biru Baby
        Hijau Tosca
        Cream
        Pink Fanta
        Ungu Lilac
        Teracota
        Dusty Pink
        Hijau Neon
        Ungu Violet
        Khaki
        Sage Green
        Steel Blue
        Salem
        Classic Blue
        Mint
        Caramel
        Pale Yellow
        Forest Green
        Light Gray
        Hijau Fuji
        Jika warna yang disebutkan pelanggan mirip dengan salah satu warna-warna tersebut, maka pilihlah dari list warna tersebut yang mendekati 
        """
    )
    customization_type: Optional[str] = Field(
        default=None, description="Jenis kustomisasi yang tersedia: Sablon dan Bordir"
    )
    customization_notes: Optional[str] = Field(
        default=None, description="""
        Detail posisi sablon: 
        1. jika pelanggan menyebutkan posisi di depan (spesifik dada kiri), maka isi key `customization_notes` dengan label `A1`
        2. jika pelanggan menyebutkan posisi di depan (spesifik dada kiri) dan dengan ukuran A4 di belakang (punggung), maka isi key `customization_notes` dengan label `A2`
        3. jika pelanggan menyebutkan posisi di depan (spesifik dada kiri) dan dengan ukuran A3 di belakang (punggung), maka isi key `customization_notes` dengan label `A3`
        4. jika pelanggan menyebutkan posisi di depan saja/dada (bukan spesifik di dada kiri) dengan ukuran 28x10 cm, maka isi key `customization_notes` dengan label `A4`
        5. jika pelanggan menyebutkan posisi di depan saja/dada (bukan spesifik di dada kiri) dengan ukuran A4, maka isi key `customization_notes` dengan label `A5`
        6. jika pelanggan menyebutkan posisi di depan saja/dada (bukan spesifik di dada kiri) dengan ukuran A3, maka isi key `customization_notes` dengan label `A6`
        7. jika pelanggan menyebutkan posisi di depan/dada (bukan spesifik di dada kiri) dan belakang (punggung) dengan ukuran A4, maka isi key `customization_notes` dengan label `A7`
        8. jika pelanggan menyebutkan posisi di depan/dada (bukan spesifik di dada kiri) dengan ukuran A4 dan belakang (punggung) dengan ukuran A3, maka isi key `customization_notes` dengan label `A8`
        9. jika pelanggan menyebutkan posisi di depan/dada (bukan spesifik di dada kiri) dan belakang (punggung) dengan ukuran A3, maka isi key `customization_notes` dengan label `A9`
        Jika jenis kustomisasi tidak disebutkan atau selain posisi yang disebutkan tadi, maka isi dengan null
        """
    )
    size_breakdown: List[SizeItem] = Field(
        ...,
        description="Daftar rincian jumlah per ukuran yang dipesan (gunakan size 'All Size' hanya untuk produk Topi dan Tote Bag)",
    )

# class blueprint supaya response Gemini persis seperti di class ini
class ChatExtractResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_info": {
                    "customer_name": "Verdy",
                    "company_name": "PT Anugra Utama Makmur",
                    "phone_number": "081234567890",
                    "shipping_address": "JALAN PANGERAN JAYAKARTA KOMPLEK 123 NO. 10, RW. 07 RT. 006 Kec. SAWAH BESAR JAKARTA PUSAT - 10730",
                },
                "deadline_requested": None,
                "items": [
                    {
                        "product_type": "Kaos Polo (Short Sleeve)",
                        "material": "Cotton Combed 30s",
                        "color": "Hitam Solid",
                        "customization_type": "Bordir",
                        "customization_notes": "A3",
                        "size_breakdown": [
                            {"size": "M", "quantity": 30},
                            {"size": "L", "quantity": 50},
                            {"size": "XL", "quantity": 50},
                        ],
                    },
                    {
                        "product_type": "Topi",
                        "material": "Bahan Topi Baseball",
                        "color": "Hitam Solid",
                        "customization_type": None,
                        "customization_notes": None,
                        "size_breakdown": [
                            {"size": "All Size", "quantity": 100}
                        ],
                    },
                ],
                "notes": None
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
    detail: str