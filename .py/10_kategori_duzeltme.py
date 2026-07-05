import sqlite3
import json
import os


print("==============================")
print(" KATEGORİ DÜZELTME MOTORU V11")
print("==============================")


# DB yolu (aynı klasörde)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "kik.db")
KATEGORI = os.path.join(BASE_DIR, "kategori.json")


# bağlantı
conn = sqlite3.connect(DB)
cursor = conn.cursor()


# -------------------------------
# Kolon kontrol
# -------------------------------

cursor.execute("PRAGMA table_info(karar_konulari)")
kolonlar = [x[1] for x in cursor.fetchall()]


if "etiketler" not in kolonlar:
    cursor.execute("""
    ALTER TABLE karar_konulari
    ADD COLUMN etiketler TEXT
    """)

    print("etiketler kolonu eklendi")


# -------------------------------
# kategori dosyası
# -------------------------------

with open(KATEGORI, "r", encoding="utf-8") as f:
    kategoriler = json.load(f)



# -------------------------------
# Anahtar kelime motoru
# -------------------------------


def kategori_bul(metin):

    metin = metin.lower()


    kurallar = [

        (
        "A13 Şikayet ve Başvuru Süreçleri",
        "İtirazen Şikayet Süreci",
        [
        "itirazen şikayet",
        "başvuru bedeli",
        "şikayet"
        ]
        ),


        (
        "A08 Aşırı Düşük Teklifler",
        "Aşırı Düşük Teklif Açıklaması",
        [
        "aşırı düşük",
        "teklif açıklaması",
        "45.1"
        ]
        ),


        (
        "A03 Mali Yeterlik ve Mali Durum",
        "Vergi ve SGK Borcu",
        [
        "vergi borcu",
        "sgk",
        "sosyal güvenlik"
        ]
        ),


        (
        "A02 İş Deneyimi ve Mesleki Yeterlik",
        "İş Deneyimi Belgeleri",
        [
        "iş deneyim",
        "benzer iş",
        "iş deneyim belgesi"
        ]
        ),


        (
        "A04 İhale Dokümanı ve Şartnameler",
        "Fiyat Dışı Unsurlar",
        [
        "fiyat dışı",
        "puanlama",
        "puan"
        ]
        ),


        (
        "A10 Fiyat ve Maliyet Unsurları",
        "Yaklaşık Maliyet",
        [
        "yaklaşık maliyet",
        "birim fiyat",
        "rayiç"
        ]
        ),


        (
        "A07 Tekliflerin Değerlendirilmesi",
        "Teklif Değerlendirme",
        [
        "teklif değerlendirme",
        "analiz",
        "fiyat teklifi"
        ]
        ),


        (
        "A01 İhaleye Katılım ve Yeterlik",
        "Yetki ve Yeterlik Belgeleri",
        [
        "yetki",
        "e-teklif",
        "belge"
        ]
        )

    ]


    for ana, alt, kelimeler in kurallar:

        for kelime in kelimeler:

            if kelime in metin:

                return ana, alt


    return (
        "A24 Diğer ve Özel Konular",
        "Genel"
    )



# -------------------------------
# Verileri tara
# -------------------------------


cursor.execute("""
SELECT 
id,
soru_basligi,
karar_ozeti,
karar_sonucu
FROM karar_konulari
""")


kayitlar = cursor.fetchall()



sayac = 0


for row in kayitlar:

    id = row[0]

    metin = " ".join(
        [
        str(row[1] or ""),
        str(row[2] or ""),
        str(row[3] or "")
        ]
    )


    ana, alt = kategori_bul(metin)


    etiketler = ",".join(
        list(
            set(
                [
                x.strip()
                for x in metin.lower().split()
                if len(x)>5
                ]
            )
        )[:8]
    )


    cursor.execute("""
    UPDATE karar_konulari

    SET

    ana_kategori=?,
    alt_kategori=?,
    etiketler=?

    WHERE id=?

    """,
    (
    ana,
    alt,
    etiketler,
    id
    ))


    sayac += 1

    print(
    f"Güncellendi: {sayac} | {ana} | {alt}"
    )



conn.commit()
conn.close()



print("==============================")
print("KATEGORİ DÜZELTME TAMAMLANDI")
print("Toplam:",sayac)
print("==============================")