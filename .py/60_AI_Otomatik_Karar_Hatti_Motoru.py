import subprocess
import sqlite3
from datetime import datetime


DB = "kik.db"



print("="*70)
print("KAMU IHALE KARAR AI - OTOMATIK KARAR HATTI")
print("="*70)



def calistir(dosya):

    print()
    print("-"*70)
    print("ÇALIŞIYOR:")
    print(dosya)
    print("-"*70)

    sonuc = subprocess.run(
        [
            "python",
            dosya
        ],
        capture_output=True,
        text=True
    )


    print(sonuc.stdout)


    if sonuc.stderr:

        print("HATA:")
        print(sonuc.stderr)





# =====================================================
# 1 PDF IMPORT
# =====================================================


calistir(
"59_AI_Toplu_PDF_Isleme_Motoru.py"
)





# =====================================================
# 2 AI KART ÜRETİM
# =====================================================


calistir(
"47_AI_100Bin_Uretim_Yonetim_Motoru.py"
)





# =====================================================
# 3 KALİTE KONTROL
# =====================================================


calistir(
"48_AI_Karar_Kalite_Kontrol_Motoru.py"
)





# =====================================================
# 4 GELİŞMİŞ ETİKET
# =====================================================


calistir(
"52_AI_Karar_Karti_Gelistirme_Motoru.py"
)





# =====================================================
# 5 EMBEDDING
# =====================================================


calistir(
"55_AI_Embedding_Vektor_Arama_Motoru.py"
)





# =====================================================
# SON DURUM
# =====================================================



conn = sqlite3.connect(DB)

cursor = conn.cursor()



cursor.execute(
"SELECT COUNT(*) FROM kararlar"
)

karar = cursor.fetchone()[0]



cursor.execute(
"SELECT COUNT(*) FROM ai_karar_kartlari"
)

ai = cursor.fetchone()[0]



print("="*70)

print("OTOMATIK HAT SONUCU")

print()

print("Toplam karar:")

print(karar)


print()

print("AI kart:")

print(ai)



print()

print("Durum:")



if karar == ai:

    print("✓ TÜM KARARLAR AI HAZIR")


else:

    print("⚠ EKSİK KARAR VAR")



print("="*70)



conn.close()