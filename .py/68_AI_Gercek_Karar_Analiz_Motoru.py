import sqlite3
import json
import os
from datetime import datetime


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - GERCEK KARAR ANALIZ MOTORU")
print("="*70)


conn = sqlite3.connect(DB)
cursor = conn.cursor()



# Gerekli kolonları oluştur

kolonlar = {

"ai_hukuki_sorun":"TEXT",
"ai_soru_basligi":"TEXT",
"ai_kisa_ozet":"TEXT",
"ai_sonuc":"TEXT",
"ai_emsal_ilke":"TEXT",
"ai_anahtar_kelimeler":"TEXT",
"ai_uzman_notu":"TEXT",
"ai_analiz_tarihi":"TEXT"

}


mevcut = [
x[1] for x in cursor.execute(
"PRAGMA table_info(kararlar)"
).fetchall()
]


for kolon,tur in kolonlar.items():

    if kolon not in mevcut:

        cursor.execute(
            f"ALTER TABLE kararlar ADD COLUMN {kolon} {tur}"
        )

        print("Eklendi:",kolon)



conn.commit()



# Analiz bekleyen kararlar

cursor.execute("""
SELECT id, karar_no, tam_metin
FROM kararlar
WHERE ai_hukuki_sorun IS NULL
""")


kararlar = cursor.fetchall()



print()
print("Analiz edilecek karar:")
print(len(kararlar))



print()



for id, karar_no, metin in kararlar:


    print("-"*60)
    print("Analiz:")
    print(karar_no)



    if not metin:

        metin = ""



    # Basit AI hukuk sınıflandırma altyapısı


    metin_alt = metin.lower()



    if "aşırı düşük" in metin_alt:

        konu = "Aşırı Düşük Teklif Açıklaması"


    elif "şikayet" in metin_alt or "itirazen" in metin_alt:

        konu = "Şikayet ve Başvuru Süreci"


    elif "iş deneyim" in metin_alt:

        konu = "İş Deneyim Belgesi"


    elif "yasaklama" in metin_alt:

        konu = "Yasaklama İşlemleri"


    elif "ihale iptal" in metin_alt:

        konu = "İhale İptali"


    else:

        konu = "İhale Hukuku Genel Uyuşmazlık"



    soru = (
        f"{konu} konusunda Kamu İhale Kurulu değerlendirmesi nedir?"
    )


    ozet = (
        f"{karar_no} sayılı kararda "
        f"{konu} kapsamında inceleme yapılmıştır. "
        "Kararda uyuşmazlığın mevzuata uygunluğu değerlendirilmiştir."
    )


    sonuc = (
        "Karar sonucunda başvuru konusu işlem "
        "mevzuat hükümleri ve Kurul değerlendirmesi "
        "çerçevesinde sonuçlandırılmıştır."
    )


    emsal = (
        f"{konu} konusunda sonraki uyuşmazlıklarda "
        "emsal değerlendirme niteliğinde kullanılabilir."
    )


    kelimeler = json.dumps(
        [
            konu,
            "4734 sayılı Kanun",
            "Kamu İhale Kurulu",
            "ihale uyuşmazlığı"
        ],
        ensure_ascii=False
    )



    cursor.execute("""
    UPDATE kararlar

    SET

    ai_hukuki_sorun=?,
    ai_soru_basligi=?,
    ai_kisa_ozet=?,
    ai_sonuc=?,
    ai_emsal_ilke=?,
    ai_anahtar_kelimeler=?,
    ai_uzman_notu=?,
    ai_analiz_tarihi=?

    WHERE id=?

    """,
    (

    konu,
    soru,
    ozet,
    sonuc,
    emsal,
    kelimeler,
    "AI hukuk analiz kartı oluşturuldu",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    id

    ))



    print("Tamamlandı:",karar_no)



conn.commit()



print()
print("="*70)
print("ANALIZ TAMAMLANDI")
print()
print("İşlenen:")
print(len(kararlar))
print("="*70)



conn.close()