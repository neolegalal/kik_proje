import sqlite3
import time
import random
from datetime import datetime


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - 100 BIN YUKLEME STRES TEST MOTORU")
print("="*70)



conn = sqlite3.connect(DB)

cursor = conn.cursor()



# -------------------------------------------------
# TEST TABLOSU
# -------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS stres_test_kararlar(

id INTEGER PRIMARY KEY AUTOINCREMENT,

karar_no TEXT,

kategori TEXT,

ozet TEXT,

tarih TEXT

)
""")


conn.commit()



# -------------------------------------------------
# MEVCUT KONTROL
# -------------------------------------------------

cursor.execute(
"SELECT COUNT(*) FROM stres_test_kararlar"
)


mevcut = cursor.fetchone()[0]


print()
print("Mevcut test kayıt:")
print(mevcut)



hedef = 100000


eklenecek = hedef - mevcut



if eklenecek <= 0:

    print()
    print("✓ 100 BIN TEST KAYDI ZATEN VAR")

else:


    print()
    print("Yeni eklenecek:")
    print(eklenecek)


    baslangic = time.time()


    veri = []


    kategoriler = [

        "Aşırı Düşük Teklifler",
        "İş Deneyim Belgeleri",
        "Yeterlik Değerlendirme",
        "İhale İptali",
        "Sözleşme Süreci"

    ]



    for i in range(eklenecek):


        karar_no = f"TEST/AI/{i+1}"


        veri.append((

            karar_no,

            random.choice(kategoriler),

            "Kamu ihale kararı örnek analiz metni",

            datetime.now().strftime("%Y-%m-%d")

        ))



        if len(veri) == 5000:


            cursor.executemany(
            """
            INSERT INTO stres_test_kararlar
            (
            karar_no,
            kategori,
            ozet,
            tarih
            )
            VALUES (?,?,?,?)
            """,
            veri
            )


            conn.commit()

            veri=[]



    if veri:

        cursor.executemany(
        """
        INSERT INTO stres_test_kararlar
        (
        karar_no,
        kategori,
        ozet,
        tarih
        )
        VALUES (?,?,?,?)
        """,
        veri
        )


        conn.commit()



    bitis=time.time()



    print()
    print("Yükleme tamamlandı")

    print()

    print("Süre:")

    print(
        round(bitis-baslangic,2),
        "saniye"
    )





# -------------------------------------------------
# TEST SONUÇ
# -------------------------------------------------


cursor.execute(
"SELECT COUNT(*) FROM stres_test_kararlar"
)


toplam = cursor.fetchone()[0]



print()

print("="*70)

print("STRES TEST SONUCU")

print()

print("Toplam kayıt:")

print(toplam)


print()


if toplam >= 100000:

    print("✓ 100 BIN KAYIT BAŞARILI")


else:

    print("⚠ EKSİK KAYIT")



print("="*70)



conn.close()