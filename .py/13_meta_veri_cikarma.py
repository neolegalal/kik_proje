import sqlite3
import os
import re


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - META VERİ ÇIKARMA MOTORU")
print("="*70)



BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE,"kik.db")


conn = sqlite3.connect(DB)
cursor = conn.cursor()



# =====================================================
# META TABLOSU
# =====================================================


cursor.execute("""
CREATE TABLE IF NOT EXISTS karar_meta (

id INTEGER PRIMARY KEY AUTOINCREMENT,

karar_id INTEGER,

ikn TEXT,
ihale_turu TEXT,
ihale_usulu TEXT,

idare TEXT,
idare_turu TEXT,

il TEXT,

ihale_yili TEXT,
karar_yili TEXT,

sektor TEXT,

basvuru_turu TEXT,

basvuran_tipi TEXT,

kanun_maddeleri TEXT,

uyusmazlik_asamasi TEXT,

haklilik_durumu TEXT,

karar_sonucu TEXT

)

""")


conn.commit()



# =====================================================
# KARARLARI AL
# =====================================================


cursor.execute("""
SELECT id, karar_no, ihale_konusu, karar_ozeti, karar_sonucu
FROM kararlar
""")


kararlar = cursor.fetchall()



print("Analiz edilen karar:",len(kararlar))



# =====================================================
# ÇIKARIM FONKSİYONLARI
# =====================================================


def bul(text, pattern):

    sonuc = re.search(pattern,text,re.I)

    if sonuc:
        return sonuc.group(1)

    return ""




for k in kararlar:


    id = k[0]


    metin = " ".join(
        [
        str(x) 
        for x in k 
        if x
        ]
    )



    # -----------------------------
    # IKN
    # -----------------------------


    ikn = bul(
        metin,
        r'(\d{4}/\d+)'
    )



    # -----------------------------
    # İhale türü
    # -----------------------------


    if "yapım işi" in metin.lower():

        ihale_turu="Yapım"

    elif "hizmet alımı" in metin.lower():

        ihale_turu="Hizmet"

    elif "mal alımı" in metin.lower():

        ihale_turu="Mal"

    else:

        ihale_turu=""



    # -----------------------------
    # Usul
    # -----------------------------


    if "açık ihale" in metin.lower():

        ihale_usulu="Açık İhale"

    elif "belli istekliler" in metin.lower():

        ihale_usulu="Belli İstekliler"

    elif "pazarlık" in metin.lower():

        ihale_usulu="Pazarlık"

    else:

        ihale_usulu=""



    # -----------------------------
    # İKN yılı
    # -----------------------------


    ihale_yili=""

    if ikn:

        ihale_yili=ikn[:4]



    # -----------------------------
    # Karar yılı
    # -----------------------------


    karar_yili=bul(
        str(k[1]),
        r'(20\d{2})'
    )



    # -----------------------------
    # İl
    # -----------------------------


    iller=[

    "İstanbul",
    "Ankara",
    "İzmir",
    "Erzurum",
    "Samsun",
    "Bursa",
    "Konya",
    "Antalya"

    ]


    il=""


    for x in iller:

        if x.lower() in metin.lower():

            il=x
            break



    # -----------------------------
    # İdare
    # -----------------------------


    idare=""


    bulunan=re.search(
    r'([A-ZÇĞİÖŞÜ][A-Za-zÇĞİÖŞÜçğıöşü ]+İdaresi)',
    metin
    )


    if bulunan:

        idare=bulunan.group(1)



    # -----------------------------
    # İdare türü
    # -----------------------------


    if "belediye" in metin.lower():

        idare_turu="Belediye"

    elif "bakanlık" in metin.lower():

        idare_turu="Bakanlık"

    elif "üniversite" in metin.lower():

        idare_turu="Üniversite"

    else:

        idare_turu=""



    # -----------------------------
    # Sektör
    # -----------------------------


    if "su" in metin.lower():

        sektor="Su / Altyapı"

    elif "yol" in metin.lower():

        sektor="Yol"

    elif "bina" in metin.lower():

        sektor="Bina"

    else:

        sektor=""



    # -----------------------------
    # Başvuru
    # -----------------------------


    if "itirazen şikayet" in metin.lower():

        basvuru="İtirazen Şikayet"

    elif "şikayet" in metin.lower():

        basvuru="Şikayet"

    else:

        basvuru=""



    # -----------------------------
    # Başvuran tipi
    # -----------------------------


    if "iş ortaklığı" in metin.lower():

        basvuran="İş Ortaklığı"

    else:

        basvuran="Firma"



    # -----------------------------
    # Kanun maddesi
    # -----------------------------


    maddeler = re.findall(
        r'(\d{1,2})[’\']?uncu maddesi',
        metin
    )


    kanun=",".join(
        [
        "4734/"+x 
        for x in maddeler
        ]
    )



    # -----------------------------
    # Haklılık
    # -----------------------------


    if "iddiasının yerinde olduğu" in metin.lower():

        haklilik="İstekli Haklı"

    elif "yerinde olmadığı" in metin.lower():

        haklilik="İdare Haklı"

    else:

        haklilik=""



    # -----------------------------
    # Kaydet
    # -----------------------------


    cursor.execute("""
    INSERT INTO karar_meta
    (
    karar_id,
    ikn,
    ihale_turu,
    ihale_usulu,
    idare,
    idare_turu,
    il,
    ihale_yili,
    karar_yili,
    sektor,
    basvuru_turu,
    basvuran_tipi,
    kanun_maddeleri,
    haklilik_durumu
    )

    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)

    """,

    (

    id,
    ikn,
    ihale_turu,
    ihale_usulu,
    idare,
    idare_turu,
    il,
    ihale_yili,
    karar_yili,
    sektor,
    basvuru,
    basvuran,
    kanun,
    haklilik

    ))



    print(
    "Analiz:",
    k[1]
    )




conn.commit()

conn.close()



print()
print("="*70)
print(" META VERİ ÇIKARMA TAMAMLANDI")
print("="*70)