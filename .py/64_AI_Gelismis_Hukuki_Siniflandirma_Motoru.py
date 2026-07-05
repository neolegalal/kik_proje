import sqlite3
from datetime import datetime


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - GELISMIS HUKUKI SINIFLANDIRMA MOTORU")
print("="*70)



conn = sqlite3.connect(DB)

cursor = conn.cursor()



# -------------------------------------------------
# YENI ALANLAR
# -------------------------------------------------

alanlar = [

("kanun_detay","TEXT"),

("uyusmazlik_turu","TEXT"),

("karar_sonucu_tipi","TEXT"),

("emsal_seviyesi","TEXT"),

("risk_alani","TEXT"),

("uzman_etiket","TEXT")

]


for alan, tip in alanlar:


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
# KARARLARI AL
# -------------------------------------------------


cursor.execute("""

SELECT

id,
karar_no,
kategori,
hukuki_konu,
sonuc,
ai_cevap


FROM ai_karar_kartlari


""")


kararlar = cursor.fetchall()



guncellenen = 0




for k in kararlar:


    id = k[0]

    karar_no = k[1]

    kategori = str(k[2] or "")

    konu = str(k[3] or "")

    sonuc = str(k[4] or "")

    cevap = str(k[5] or "")



    # -----------------------------
    # VARSAYILAN
    # -----------------------------


    kanun_detay = "4734 sayılı Kamu İhale Kanunu"


    uyusmazlik = "İhale Süreci Uyuşmazlığı"


    sonuc_tipi = "Değerlendirme"


    emsal = "Orta"


    risk = "İhale işlemleri"


    etiket = "Kamu İhale Kararı"




    metin = (

        kategori +

        " " +

        konu +

        " " +

        sonuc +

        " " +

        cevap

    ).lower()



    # -----------------------------
    # SINIFLANDIRMA
    # -----------------------------


    if "aşırı" in metin or "düşük" in metin:


        uyusmazlik = "Aşırı Düşük Teklif Açıklaması"

        risk = "Teklif değerlendirme riski"

        etiket = "Aşırı Düşük Teklif"

        emsal = "Yüksek"



    elif "şikayet" in metin:


        uyusmazlik = "İtirazen Şikayet Başvurusu"

        risk = "Başvuru süreci riski"

        etiket = "Şikayet Süreci"




    elif "yeterlik" in metin:


        uyusmazlik = "Yeterlik Değerlendirmesi"

        risk = "Yeterlik riski"

        etiket = "Yeterlik Kontrolü"





    if "4735" in metin:

        kanun_detay = "4735 sayılı Kamu İhale Sözleşmeleri Kanunu"


        uyusmazlik = "Sözleşme Uyuşmazlığı"



    if "2886" in metin:


        kanun_detay = "2886 sayılı Devlet İhale Kanunu"




    if "iptal" in metin:


        sonuc_tipi = "İhale İptali / İşlem Sonucu"

        risk = "İdari işlem riski"




    # -----------------------------
    # UPDATE
    # -----------------------------


    cursor.execute("""


    UPDATE ai_karar_kartlari


    SET


    kanun_detay=?,

    uyusmazlik_turu=?,

    karar_sonucu_tipi=?,

    emsal_seviyesi=?,

    risk_alani=?,

    uzman_etiket=?


    WHERE id=?


    """,

    (

    kanun_detay,

    uyusmazlik,

    sonuc_tipi,

    emsal,

    risk,

    etiket,

    id

    ))



    print(

    "Sınıflandırıldı:",

    karar_no,

    "→",

    etiket

    )


    guncellenen += 1





conn.commit()

conn.close()



print()

print("="*70)

print("GELISMIS HUKUKI SINIFLANDIRMA TAMAMLANDI")

print()

print("Güncellenen:", guncellenen)

print("="*70)