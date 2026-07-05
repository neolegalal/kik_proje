import sqlite3
from datetime import datetime


DB = "kik.db"


print("=" * 70)
print("KAMU IHALE KARAR AI - HUKUKI KART MOTORU")
print("=" * 70)


conn = sqlite3.connect(DB)
cursor = conn.cursor()


# kart tablosu oluştur
cursor.execute("""
CREATE TABLE IF NOT EXISTS hukuki_kartlar (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    karar_no TEXT,

    iddia_no INTEGER,

    baslik TEXT,

    hukuki_soru TEXT,

    kurul_degerlendirmesi TEXT,

    sonuc TEXT,

    emsal_ilke TEXT,

    anahtar_kelime TEXT,

    kart_tarihi TEXT

)
""")


print("Kart tablosu hazır")


# eski kartları temizle
cursor.execute("""
DELETE FROM hukuki_kartlar
""")


# iddiaları çek
cursor.execute("""
SELECT

karar_no,
iddia_no,
konu,
uzman_soru,
kurul_degerlendirmesi,
sonuc,
emsal_ilke,
anahtar_kelime

FROM karar_iddialari

""")


kayitlar = cursor.fetchall()


sayac = 0


for k in kayitlar:

    karar_no = k[0]
    iddia_no = k[1]
    konu = k[2]
    soru = k[3]
    kurul = k[4]
    sonuc = k[5]
    ilke = k[6]
    anahtar = k[7]


    cursor.execute("""
    INSERT INTO hukuki_kartlar
    (

    karar_no,
    iddia_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke,
    anahtar_kelime,
    kart_tarihi

    )

    VALUES (?,?,?,?,?,?,?,?,?)

    """,

    (

    karar_no,
    iddia_no,
    konu,
    soru,
    kurul,
    sonuc,
    ilke,
    anahtar,
    datetime.now().strftime("%Y-%m-%d")

    ))


    sayac += 1


conn.commit()


print()
print("=" * 70)
print("KART OLUŞTURMA TAMAMLANDI")
print("=" * 70)

print("Oluşturulan kart:", sayac)


conn.close()