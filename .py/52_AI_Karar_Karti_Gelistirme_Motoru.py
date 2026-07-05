import sqlite3
from datetime import datetime


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - KARAR KARTI GELISTIRME MOTORU")
print("="*70)



conn = sqlite3.connect(DB)
cursor = conn.cursor()



# yeni alanları ekle

kolonlar = [

("hukuki_konu","TEXT"),

("karar_tipi","TEXT"),

("uyusmazlik_turu","TEXT"),

("risk_alani","TEXT"),

("gelismis_etiket","TEXT")

]



for kolon,tip in kolonlar:

    try:

        cursor.execute(
            f"""
            ALTER TABLE ai_karar_kartlari
            ADD COLUMN {kolon} {tip}
            """
        )

        print("Eklendi:", kolon)


    except:

        pass




# mevcut kayıtları doldur


cursor.execute("""
SELECT 
id,
soru_basligi,
kategori,
anahtar_kelimeler

FROM ai_karar_kartlari

"""
)


kayitlar = cursor.fetchall()



guncel=0



for kayit in kayitlar:


    id = kayit[0]

    baslik = kayit[1] or ""

    kategori = kayit[2] or ""

    anahtar = kayit[3] or ""



    konu = kategori


    karar_tipi="Kamu İhale Kurulu Kararı"



    uyusmazlik=""

    risk=""



    metin = (
        baslik+
        " "+
        anahtar
    ).lower()



    if "aşırı düşük" in metin:

        uyusmazlik="Aşırı Düşük Teklif"


        risk="Teklif Değerlendirme Riski"



    elif "ihale iptal" in metin:

        uyusmazlik="İhale İptali"

        risk="İdari İşlem Riski"



    elif "yeterlik" in metin:

        uyusmazlik="Yeterlik Değerlendirmesi"

        risk="Katılım Riski"




    etiket = ",".join([

        kategori,

        uyusmazlik,

        risk

    ])




    cursor.execute("""
    
    UPDATE ai_karar_kartlari

    SET

    hukuki_konu=?,

    karar_tipi=?,

    uyusmazlik_turu=?,

    risk_alani=?,

    gelismis_etiket=?

    WHERE id=?

    """,
    (
    konu,
    karar_tipi,
    uyusmazlik,
    risk,
    etiket,
    id
    )
    )



    guncel+=1




conn.commit()
conn.close()



print()
print("="*70)

print("KARAR KARTI GELISTIRME TAMAMLANDI")

print("Güncellenen:",guncel)

print("="*70)