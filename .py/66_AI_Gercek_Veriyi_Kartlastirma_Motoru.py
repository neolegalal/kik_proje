import sqlite3
from datetime import datetime
import re

DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - GERCEK VERI KARTLASTIRMA MOTORU")
print("="*70)


conn = sqlite3.connect(DB)
cursor = conn.cursor()


# AI kart alanlarını kontrol et
columns = [
    ("kart_hukuki_sorun", "TEXT"),
    ("kart_kisa_ozet", "TEXT"),
    ("kart_sonuc", "TEXT"),
    ("kart_emsal_ilke", "TEXT"),
    ("kart_ana_kategori", "TEXT"),
    ("kart_alt_kategori", "TEXT"),
    ("kart_risk", "TEXT"),
    ("kart_uzman_etiket", "TEXT"),
    ("kart_tarih", "TEXT")
]


for col, typ in columns:
    try:
        cursor.execute(
            f"ALTER TABLE kararlar ADD COLUMN {col} {typ}"
        )
        print("Eklendi:", col)

    except:
        pass


conn.commit()



# kararları al

cursor.execute("""
SELECT id,
       karar_no,
       tam_metin,
       ana_kategori,
       anahtar_kelimeler,
       karar_sonucu
FROM kararlar
WHERE kart_hukuki_sorun IS NULL
""")


records = cursor.fetchall()


print()
print("Kart oluşturulacak karar:")
print(len(records))
print()



sayac = 0


for row in records:

    id = row[0]
    karar_no = row[1]
    metin = row[2] or ""
    kategori = row[3] or ""
    kelime = row[4] or ""
    sonuc = row[5] or ""


    # soru başlığı üret

    soru = "Bu kararda hukuki uyuşmazlığın konusu nedir?"


    if "aşırı düşük" in metin.lower():

        soru = (
        "Aşırı düşük teklif açıklaması hangi belgelerle yapılır "
        "ve hangi durumlarda reddedilir?"
        )


    elif "iş deneyim" in metin.lower():

        soru = (
        "İş deneyim belgesinin geçerliliği hangi şartlara bağlıdır?"
        )


    elif "şikayet" in metin.lower():

        soru = (
        "İhale sürecinde şikayet ve itirazen şikayet başvurusu "
        "hangi usullere tabidir?"
        )



    # kısa özet

    temiz = re.sub(
        r"\s+",
        " ",
        metin
    )


    ozet = temiz[:700]



    # sonuç

    if sonuc:

        kart_sonuc = sonuc

    else:

        kart_sonuc = (
        "Karar kapsamında yapılan inceleme sonucunda "
        "idari işlem hakkında değerlendirme yapılmıştır."
        )



    # risk

    risk="Genel ihale hukuku riski"


    if "aşırı düşük" in metin.lower():
        risk="Teklif değerlendirme riski"

    elif "iş deneyim" in metin.lower():
        risk="Yeterlik değerlendirme riski"

    elif "fesih" in metin.lower():
        risk="Sözleşme uygulama riski"



    etiket = kategori + " | " + kelime



    cursor.execute("""
    UPDATE kararlar

    SET

    kart_hukuki_sorun=?,
    kart_kisa_ozet=?,
    kart_sonuc=?,
    kart_emsal_ilke=?,
    kart_ana_kategori=?,
    kart_alt_kategori=?,
    kart_risk=?,
    kart_uzman_etiket=?,
    kart_tarih=?

    WHERE id=?

    """,
    (

    soru,
    ozet,
    kart_sonuc,
    "Kurul uygulaması doğrultusunda değerlendirme yapılmıştır.",
    kategori,
    kategori,
    risk,
    etiket,
    datetime.now().strftime("%Y-%m-%d"),
    id

    ))



    sayac += 1


    print(
        "Kartlandı:",
        karar_no
    )



conn.commit()
conn.close()



print()
print("="*70)
print("GERCEK VERI KARTLASTIRMA TAMAMLANDI")
print()
print("Güncellenen:")
print(sayac)
print("="*70)