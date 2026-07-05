import sqlite3
from datetime import datetime

DB = "kik.db"

conn = sqlite3.connect(DB)
cursor = conn.cursor()


print("="*70)
print("KAMU IHALE KARAR AI - KATEGORI TAMAMLAMA MOTORU")
print("="*70)


kayitlar = cursor.execute("""
SELECT 
id,
karar_no,
soru_basligi,
kisa_ozet
FROM ai_karar_kartlari
WHERE kategori IS NULL
""").fetchall()


guncellenen = 0


for row in kayitlar:

    id = row[0]
    karar_no = row[1]
    baslik = row[2]
    ozet = row[3]


    metin = (baslik + " " + ozet).lower()


    kategori = "A13 Şikayet ve Başvuru Süreçleri"
    alt = "İtirazen şikayet değerlendirmesi"
    etiket = "şikayet, başvuru, KİK incelemesi"


    if "aşırı düşük" in metin:
        kategori = "A08 Aşırı Düşük Teklifler"
        alt = "Aşırı düşük teklif açıklaması değerlendirmesi"
        etiket = "aşırı düşük teklif, analiz, fiyat teklifi, Tebliğ 45"


    elif "iş deneyim" in metin:
        kategori = "A06 Yeterlik Kriterleri"
        alt = "İş deneyim belgesi değerlendirmesi"
        etiket = "iş deneyimi, belge, yeterlik"


    elif "teminat" in metin:
        kategori = "A07 Teklif Değerlendirme"
        alt = "Teminat işlemleri"
        etiket = "geçici teminat, kesin teminat"


    cursor.execute("""
    UPDATE ai_karar_kartlari
    SET 
    kategori=?,
    alt_kategori=?,
    arama_etiketleri=?
    WHERE id=?
    """,
    (
        kategori,
        alt,
        etiket,
        id
    ))


    guncellenen += 1

    print("Güncellendi:", karar_no)



conn.commit()
conn.close()


print()
print("="*70)
print("KATEGORİ TAMAMLAMA BİTTİ")
print("Güncellenen:", guncellenen)
print("="*70)