import sqlite3
import time


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - 100 BIN ARAMA PERFORMANS TEST MOTORU")
print("="*70)



conn = sqlite3.connect(DB)

cursor = conn.cursor()



# --------------------------------------------------
# TEST KONTROL
# --------------------------------------------------


cursor.execute(
"SELECT COUNT(*) FROM stres_test_kararlar"
)


toplam = cursor.fetchone()[0]


print()
print("Test veri sayısı:")
print(toplam)



if toplam < 100000:

    print()
    print("⚠ Önce 100 bin yükleme testi çalıştırılmalı")

    conn.close()
    exit()




# --------------------------------------------------
# ARAMA TESTLERİ
# --------------------------------------------------


sorular = [

    "Aşırı Düşük Teklifler",

    "İş Deneyim Belgeleri",

    "İhale İptali",

    "Yeterlik Değerlendirme",

    "Sözleşme Süreci"

]




print()

print("="*70)

print("ARAMA TESTLERİ")

print("="*70)



basarili = 0



for soru in sorular:


    print()

    print("-"*60)

    print("Arama:")

    print(soru)



    baslangic = time.time()



    cursor.execute(
    """
    SELECT karar_no,kategori,ozet
    FROM stres_test_kararlar
    WHERE kategori LIKE ?
    LIMIT 10
    """,
    (
        "%" + soru + "%",
    )
    )


    sonuc = cursor.fetchall()



    bitis = time.time()



    sure = round(
        bitis-baslangic,
        5
    )



    print()

    print("Bulunan:")

    print(len(sonuc))



    print("Süre:")

    print(
        sure,
        "sn"
    )



    if sonuc:

        basarili += 1





# --------------------------------------------------
# SONUÇ
# --------------------------------------------------


print()

print("="*70)

print("PERFORMANS SONUCU")

print("="*70)


print()

print("Başarılı arama:")

print(
    basarili,
    "/",
    len(sorular)
)



if basarili == len(sorular):

    print()

    print("✓ 100 BIN KAYIT ARAMA BAŞARILI")


else:

    print()

    print("⚠ Bazı aramalar başarısız")



print("="*70)



conn.close()