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
            """Customer: siang min mau nanya klo bikin kaos lengan pendek warna navy trus sablon logo PT di depan kena brp ya? 
            Admin: Halo kak, untuk kaos short sleeve dan sablon depan kita bisa di dada tengah, kanan atau kiri kak, 
            dan untuk di tengah kita terdapat ukuran 28x10cm jadi memanjang, lalu ukuran A4, dan A3. Customer: bahannya apa ya min? 
            Admin: untuk bahan kita menggunakan cotton combed 30s atau cotton combed 24s kak Customer: oke deh min mau pesen di dada 
            tengah yang memanjang 100 pcs yang combed 30s. terus ukuran M 30 pcs untuk ukuran L 50 pcs dan XL 20 pcs Admin: Siap kak, 
            ada tambahan lain? Customer: Sama sekalian topi item deh min bahannya pake apa ya dan kena berapa per pcs nya? 
            Admin: untuk topi kita pake bahan topi baseball kak dan ada di 30 ribu per pcs kak Customer: oke sekalian pesen juga berarti 100 pcs ya min 
            Admin: baik kak, atas nama siapa dan dikirim ke mana ya kak? 
            Customer: atas nama Yudha PT Indokoin Semesta 081213141516 kirim ke Sequis Tower, Jl. Jenderal Sudirman 
            No. Kav. 71 (Lantai 7 / Lantai 25), RT.5/RW.3, Senayan, Kec. Kebayoran Baru, Kota Jakarta Selatan, DKI Jakarta 12190 
            sama sebelum tanggal 1 udah jadi bisa ya min? Admin: mengingat pesanannya cukup banyak kemungkinan tanggal 2 baru selesai kak gimana? 
            Customer: ya udah deh min"""
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
        default=None, description='Nomor Telepon Pelanggan, biasanya dimulai dari angka `08` atau `+628`, lalu null jika tidak disebutkan'
    )
    shipping_address: Optional[str] = Field(
        default=None, description='Alamat pengiriman lengkap, null jika tidak disebutkan'
    )

class SizeItem(BaseModel):
    size: str = Field(
        ...,
        description="Ukuran produk yang tersedia yaitu `XS`, `S`, `M`, `L`, `XL`, `XXL`, `XXXL`, `XXXXL`, `XXXXXL` dan ukuran `All Size` untuk produk `Topi` dan `Tote Bag`"
    )
    quantity: int = Field(
        ...,
        description="Jumlah pesanan untuk ukuran tersebut (bilangan bulat positif)"
    )

class OrderItem(BaseModel):
    product_type: str = Field(
        ..., description="""Jenis Produk yang tersedia yaitu: `Kaos`, `Kaos Polo`, `Topi` dan `Tote Bag`"""
    )

    sleeve_type: Optional[str] = Field(
        default=None, 
        description="""Tipe panjang lengan pada tipe produk `Kaos` dan `Kaos Polo`. 
        jika permintaan pelanggan di percakapan adalah lengan pendek, maka isi dengan `Short Sleeve`.
        jika permintaan pelanggan di percakapan adalah lengan panjang, maka isi dengan `Long Sleeve`. 
        isi dengan null untuk tipe produk `Topi` dan `Tote Bag`"""
    )

    material: Optional[str] = Field(
        default=None, 
        description="""Jenis bahan yang tersedia yaitu: untuk tipe produk `Kaos` menggunakan bahan `Cotton Combed 24s` dan `Cotton Combed 30s`.
                    Lalu untuk `Kaos Polo` terdapat varian bahan `Polyester` dan `Lacoste Cotton Pique`.
                    Lalu untuk `Topi`, isi bahan/material dengan `Bahan Topi Baseball` dan untuk produk `Tote Bag` menggunakan bahan `Kanvas`"""
    )

    color: Optional[str] = Field(
        default=None, 
        description="""Warna yang tersedia yaitu:
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
        Jika warna yang disepakati di percakapan mirip dengan salah satu warna-warna tersebut, maka pilihlah dari list warna tersebut yang mendekati 
        """
    )

    customization_type: Optional[str] = Field(
        default=None, description="Jenis kustomisasi yang tersedia untuk semua tipe produk (Topi, Kaos, Kaos Polo): `Sablon` dan `Bordir`, kecuali tipe produk `Tote Bag` hanya tersedia kustomisasi `Sablon`. isi dengan null jika jenis kustomisasi yaitu `Sablon` atau `Bordir` tidak disebutkan di percakapan."
    )

    customization_notes: Optional[str] = Field(
        default=None, description="""Detail posisi Sablon atau Bordir: 
        1. jika posisi Sablon atau Bordir yang disebutkan/disepakati di percakapan adalah di depan (spesifik dada kiri/kanan) saja, maka isi key `customization_notes` dengan label `A1`
        2. jika posisi Sablon atau Bordir yang disebutkan/disepakati di percakapan adalah di depan (spesifik dada kiri/kanan) dan dengan ukuran A4 di belakang (punggung), maka isi key `customization_notes` dengan label `A2`
        3. jika posisi Sablon atau Bordir yang disebutkan/disepakati di percakapan adalah di depan (spesifik dada kiri/kanan) dan dengan ukuran A3 di belakang (punggung), maka isi key `customization_notes` dengan label `A3`
        4. jika posisi Sablon atau Bordir yang disebutkan/disepakati di percakapan adalah di depan saja (tanpa Sablon atau Bordir belakang), yaitu di dada tengah dan dengan ukuran 28x10 cm (persis di tengah dada dan memanjang seperti persegi panjang), maka isi key `customization_notes` dengan label `A4`
        5. jika posisi Sablon atau Bordir yang disebutkan/disepakati di percakapan adalah di depan saja (tanpa Sablon atau Bordir belakang), yaitu di dada tengah dan dengan ukuran A4, maka isi key `customization_notes` dengan label `A5`
        6. jika posisi Sablon atau Bordir yang disebutkan/disepakati di percakapan adalah di depan saja (tanpa Sablon atau Bordir belakang), yaitu di dada tengah dan dengan ukuran A3, maka isi key `customization_notes` dengan label `A6`
        7. jika posisi Sablon atau Bordir yang disebutkan/disepakati di percakapan adalah di depan yaitu di dada tengah dan belakang (punggung) dengan ukuran A4, maka isi key `customization_notes` dengan label `A7`
        8. jika posisi Sablon atau Bordir yang disebutkan/disepakati di percakapan adalah di depan yaitu di dada tengah dengan ukuran A4 dan belakang (punggung) dengan ukuran A3, maka isi key `customization_notes` dengan label `A8`
        9. jika posisi Sablon atau Bordir yang disebutkan/disepakati di percakapan adalah di depan yaitu di dada tengah dan belakang (punggung) dengan ukuran A3, maka isi key `customization_notes` dengan label `A9`
        Jika jenis kustomisasi tidak disebutkan atau selain 9 kondisi posisi tadi, maka isi dengan null, jangan mengarang
        """
    )

    size_breakdown: List[SizeItem] = Field(
        ...,
        description="Daftar rincian jumlah per ukuran yang dipesan (gunakan size `All Size` hanya untuk produk `Topi` dan `Tote Bag`)",
    )

# class blueprint supaya response Gemini persis seperti di class ini
class ChatExtractResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_info": {
                    "customer_name": "Verdy",
                    "company_name": "PT Anugra Utama Makmur",
                    "phone_number": "083435383994",
                    "shipping_address": "JALAN PANGERAN JAYAKARTA KOMPLEK 123 NO. 10, RW. 07 RT. 006 Kec. SAWAH BESAR JAKARTA PUSAT - 10730",
                },
                "deadline_requested": "2026-11-24",
                "items": [
                    {
                        "product_type": "Kaos Polo",
                        "sleeve_type": "Short Sleeve",
                        "material": "Cotton Combed 30s",
                        "color": "Navy Tua",
                        "customization_type": "Bordir",
                        "customization_notes": "A2",
                        "size_breakdown": [
                            {"size": "M", "quantity": 30},
                            {"size": "L", "quantity": 50},
                            {"size": "XL", "quantity": 50},
                        ],
                    },
                    {
                        "product_type": "Topi",
                        "sleeve_type": None,
                        "material": "Bahan Topi Baseball",
                        "color": "Hitam Solid",
                        "customization_type": "Bordir",
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
        default=None, 
        description="""Target tanggal selesai pesanan hasil kesepakatan akhir kedua belah pihak dalam format `YYYY-MM-DD`
                    dihitung berdasarkan konteks waktu saat ini pada system instruction. isi dengan null jika tidak disebutkan."""
    )
    items: List[OrderItem]
    notes: Optional[str] = Field(
        default=None, description="Catatan tambahan pesanan misal untuk acara apa"
    )

class ErrorResponse(BaseModel):
    detail: str