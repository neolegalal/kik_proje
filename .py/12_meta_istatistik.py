import sqlite3
import os

print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - META İSTATİSTİK MOTORU")
print("="*70)


# DB yolu
BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "kik.db")


conn = sqlite3.connect(DB)
cursor = conn.cursor()


# ======================================================
# YENİ META ALANLARI
# ======================================================

alanlar = {

"ihale_turu":"TEXT",
"ihale_usulu":"TEXT",
"idare":"TEXT",
"idare_turu":"TEXT",
"il":"TEXT",
"ihale_yili":"TEXT",
"karar_yili":"TEXT",
"sektor":"TEXT",
"ikn":"TEXT",
"kanun_maddeleri":"TEXT",
"karar_sonucu":"TEXT",
"basvuru_turu":"TEXT",
"basvuran_tipi":"TEXT",
"uyusmazlik_asamasi":"TEXT",
"haklilik_durumu":"TEXT"

}


# kolon kontrol

cursor.execute("PRAGMA table_info(kararlar)")
mevcut = [x[1] for x in cursor.fetchall()]


for kolon,tur in alanlar.items():

    if kolon not in mevcut:

        cursor.execute(
        f"""
        ALTER TABLE kararlar
        ADD COLUMN {kolon} {tur}
        """
        )

        print("Eklendi:", kolon)



conn.commit()



# ======================================================
# İSTATİSTİK FONKSİYONU
# ======================================================


def analiz(baslik, kolon):

    print("\n")
    print(baslik)
    print("-"*40)

    cursor.execute(
    f"""
    SELECT {kolon}, COUNT(*)
    FROM kararlar
    WHERE {kolon} IS NOT NULL
    AND {kolon}!=''
    GROUP BY {kolon}
    ORDER BY COUNT(*) DESC
    """
    )


    sonuc = cursor.fetchall()


    if not sonuc:
        print("Henüz veri yok")
        return


    for veri,sayi in sonuc:

        print(veri,":",sayi)



# ======================================================
# GENEL
# ======================================================


cursor.execute(
"""
SELECT COUNT(*)
FROM kararlar
"""
)

toplam = cursor.fetchone()[0]


print("\nGENEL")
print("-"*40)
print("Toplam kayıt:", toplam)



# ======================================================
# META ANALİZLER
# ======================================================


analiz(
"İHALE TÜRÜ ANALİZİ",
"ihale_turu"
)


analiz(
"İHALE USULÜ ANALİZİ",
"ihale_usulu"
)


analiz(
"İDARE ANALİZİ",
"idare"
)


analiz(
"İDARE TÜRÜ ANALİZİ",
"idare_turu"
)


analiz(
"İL ANALİZİ",
"il"
)


analiz(
"İHALE YILI ANALİZİ",
"ihale_yili"
)


analiz(
"KARAR YILI ANALİZİ",
"karar_yili"
)


analiz(
"SEKTÖR ANALİZİ",
"sektor"
)


analiz(
"KARAR SONUCU ANALİZİ",
"karar_sonucu"
)


analiz(
"BAŞVURU TÜRÜ ANALİZİ",
"basvuru_turu"
)


analiz(
"HAKLILIK ANALİZİ",
"haklilik_durumu"
)



print("\n")
print("="*70)
print(" META İSTATİSTİK TAMAMLANDI")
print("="*70)



conn.close()