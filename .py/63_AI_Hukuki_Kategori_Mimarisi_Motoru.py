import sqlite3
from datetime import datetime


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - HUKUKI KATEGORI MIMARISI MOTORU")
print("="*70)



conn = sqlite3.connect(DB)

cursor = conn.cursor()



# -------------------------------------------------
# GEREKLI ALANLARI EKLE
# -------------------------------------------------


alanlar = [

("hukuk_alani","TEXT"),

("yargi_kolu","TEXT"),

("kurum_turu","TEXT"),

("kanun","TEXT"),

("ust_kategori","TEXT"),

("alt_kategori_yeni","TEXT"),

("donem","TEXT")

]



for alan,tip in alanlar:


    try:

        cursor.execute(
        f"""
        ALTER TABLE ai_karar_kartlari
        ADD COLUMN {alan} {tip}
        """
        )


        print("Eklendi:", alan)


    except:


        pass




# -------------------------------------------------
# KATEGORI MOTORU
# -------------------------------------------------



cursor.execute(

"""

SELECT

id,

karar_no,

kategori,

hukuki_konu

FROM ai_karar_kartlari


"""

)



kararlar = cursor.fetchall()



guncellenen = 0




for karar in kararlar:


    id = karar[0]

    karar_no = karar[1]


    kategori = str(karar[2] or "")



    # varsayılan

    hukuk_alani = "İhale Hukuku"

    yargi_kolu = "İdari Yargı"

    kurum = "Kamu İhale Kurumu"

    kanun = "4734"



    ust = "KİK Kararları"

    alt = "Genel İhale Süreci"




    if "A08" in kategori:


        alt = "Aşırı Düşük Teklifler"



    elif "A13" in kategori:


        alt = "Şikayet ve Başvuru Süreçleri"





    cursor.execute(

    """

    UPDATE ai_karar_kartlari


    SET

    hukuk_alani=?,

    yargi_kolu=?,

    kurum_turu=?,

    kanun=?,

    ust_kategori=?,

    alt_kategori_yeni=?,

    donem=?


    WHERE id=?


    """,

    (

    hukuk_alani,

    yargi_kolu,

    kurum,

    kanun,

    ust,

    alt,

    "2006-2026",

    id

    )

    )



    guncellenen += 1


    print(
    "Kategorilendi:",
    karar_no,
    "→",
    alt
    )





conn.commit()

conn.close()



print()

print("="*70)

print("HUKUKI KATEGORI MIMARISI TAMAMLANDI")

print()

print("Guncellenen:", guncellenen)

print("="*70)