import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - KARAR KALITE KONTROL MOTORU")
print("="*70)



conn = sqlite3.connect(DB)

cursor = conn.cursor()



# =====================================================
# TOPLAM KART
# =====================================================


cursor.execute("""
SELECT COUNT(*)
FROM ai_karar_kartlari
""")


toplam = cursor.fetchone()[0]



print()

print("Toplam AI karar kartı:", toplam)



# =====================================================
# KONTROL EDİLECEK ALANLAR
# =====================================================


alanlar = {

"soru_basligi":"Soru Başlığı",

"kisa_ozet":"Kısa Özet",

"hukuki_sorun":"Hukuki Sorun",

"gerekce":"Gerekçe",

"sonuc":"Sonuç",

"emsal_ilke":"Emsal İlke",

"mevzuat":"Mevzuat",

"anahtar_kelimeler":"Anahtar Kelimeler",

"kategori":"Kategori"

}




sorunlu = []



# =====================================================
# KONTROL
# =====================================================


cursor.execute("""
SELECT *
FROM ai_karar_kartlari
""")


kartlar = cursor.fetchall()



sutunlar = [

" id",

"karar_id",

"karar_no",

"soru_basligi",

"kisa_ozet",

"hukuki_sorun",

"gerekce",

"sonuc",

"emsal_ilke",

"mevzuat",

"anahtar_kelimeler",

"kategori",

"alt_kategori",

"arama_etiketleri",

"emsal_degeri",

"ai_soru",

"ai_cevap",

"olusturma_tarihi"

]



basarili = 0



for kart in kartlar:


    eksikler = []


    veri = dict(zip(sutunlar,kart))



    for alan,ad in alanlar.items():


        if not veri.get(alan):

            eksikler.append(ad)



    if eksikler:


        sorunlu.append({

        "karar_no":veri["karar_no"],

        "eksikler":eksikler

        })


    else:

        basarili += 1





# =====================================================
# RAPOR
# =====================================================


print()

print("="*70)

print("KALİTE RAPORU")

print("="*70)


print()

print("Başarılı kayıt:", basarili)

print("Sorunlu kayıt:", len(sorunlu))



print()



if sorunlu:


    print("SORUNLU KARARLAR")

    print("-"*70)


    for s in sorunlu:


        print()

        print(
        s["karar_no"]
        )


        print(
        "Eksikler:",
        ", ".join(s["eksikler"])
        )


else:


    print()

    print("✓ TÜM AI KARAR KARTLARI KALİTELİ")




print()

print("="*70)

print("KALİTE KONTROL TAMAMLANDI")

print("="*70)



conn.close()