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
            "Customer: siang min mau nanya klo bikin kaos warna item trus sablon logo PT di depan belakang kena brp ya? Admin: Halo kak, buat sablon depan belakang dengan depan ukuran A4 dan belakang ukuran A3 kena di 80 ribu per pcs kak Customer: bahannya apa ya min? Admin: untuk bahan kita menggunakan cotton combed 30s atau cotton combed 24s kak Customer: oke deh min mau pesen 130 pcs yang combed 30s yang ukuran M 30 pcs untuk ukuran L 50 pcs dan XL 50 pcs Admin: Siap kak, ada tambahan lain? Customer: Sama sekalian topi item deh min kena berapa per pcs nya? Admin: untuk topi kita all size ada di 30 ribu per pcs kak Customer: oke sekalian pesen juga berarti 100 pcs ya min Admin: baik kak, atas nama siapa dan dikirim ke mana ya kak? Customer: atas nama Verdy PT ANUGRA UTAMA MAKMUR 081234567890 Kirim ke JALAN PANGERAN JAYAKARTA KOMPLEK 123 NO. 10, RW. 07 RT. 006 Kec. SAWAH BESAR JAKARTA PUSAT - 10730"
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
        description="Ukuran produk, misal 'S', 'M', 'L', 'XL', 'XXL' 'XXXL', 'XXXXL', atau 'All Size' untuk produk Topi dan Tas"
    )
    quantity: int = Field(
        ...,
        description="Jumlah pesanan untuk ukuran tersebut (bilangan bulat positif)"
    )

class OrderItem(BaseModel):
    product_type: str = Field(
        ..., description='Jenis Produk yang tersedia yaitu: Kaos (Short Sleeve, Long Sleeve), Kaos Polo, Topi, Hoodie, Tas'
    )
    material: Optional[str] = Field(
        default=None, description="Jenis bahan yang tersedia yaitu: Cotton Combed 30s dan Cotton Combed 24s. Untuk produk selain Kaos (Short Sleeve, Long Sleeve) dan Kaos Polo, yaitu Topi, Hoodie, Tas, isi bahan/material dengan null"
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
        1. jika pelanggan menyebutkan posisi di depan (dada kiri), maka isi key `customization_notes` dengan label 1
        2. jika pelanggan menyebutkan posisi di depan (dada kiri) dan dengan ukuran A4 di belakang/punggung, maka isi key `customization_notes` dengan label 2
        3. jika pelanggan menyebutkan posisi di depan (dada kiri) dan dengan ukuran A3 di belakang/punggung, maka isi key `customization_notes` dengan label 3
        4. jika pelanggan menyebutkan posisi di depan saja (bukan di dada kiri) dengan ukuran 28x10 cm, maka isi key `customization_notes` dengan label 4
        5. jika pelanggan menyebutkan posisi di depan saja (bukan di dada kiri) dengan ukuran A4, maka isi key `customization_notes` dengan label 5
        6. jika pelanggan menyebutkan posisi di depan saja (bukan di dada kiri) dengan ukuran A3, maka isi key `customization_notes` dengan label 6
        7. jika pelanggan menyebutkan posisi di depan dan belakang dengan ukuran A4, maka isi key `customization_notes` dengan label 7
        8. jika pelanggan menyebutkan posisi di depan dengan ukuran A4 dan belakang dengan ukuran A3, maka isi key `customization_notes` dengan label 8
        9. jika pelanggan menyebutkan posisi di depan dan belakang dengan ukuran A3, maka isi key `customization_notes` dengan label 9
        Jika jenis kustomisasi tidak disebutkan, maka isi dengan null
        """
    )
    size_breakdown: List[SizeItem] = Field(
        ...,
        description="Daftar rincian jumlah per ukuran yang dipesan (gunakan size 'All Size' untuk produk selain Kaos, Kaos Polo, dan Hoodie yaitu Topi dan Tas)",
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
                        "product_type": "Kaos Polo",
                        "material": "Cotton Combed 30s",
                        "color": "Hitam Solid",
                        "customization_type": "Bordir",
                        "customization_notes": "3",
                        "size_breakdown": [
                            {"size": "M", "quantity": 30},
                            {"size": "L", "quantity": 50},
                            {"size": "XL", "quantity": 50},
                        ],
                    },
                    {
                        "product_type": "Topi",
                        "material": None,
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
    status: str = "Error"
    detail: str