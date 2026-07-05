import sqlite3
from collections import Counter
import os


# ==============================
# VERİTABANI YOLU
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "kik.db")


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - İSTATİSTİK MOTORU V2")
print("="*70)


# ==============================
# BAĞLANTI
# ==============================

conn = sqlite3.connect(DB)
cursor = conn.cursor()



# ==============================
# GENEL İSTATİSTİK
# ==============================

print("\nGENEL İSTATİSTİK")
print("-"*40)


cursor.execute("""
SELECT COUNT(DISTINCT karar_no)
FROM kararlar
""")


karar = cursor.fetchone()[0]


cursor.execute("""
SELECT COUNT(*)
FROM karar_konulari
""")


konu = cursor.fetchone()[0]


print("Toplam Karar:", karar)
print("Toplam İncelenen Konu:", konu)




# ==============================
# ANA KATEGORİ
# ==============================

print("\nANA KATEGORİ DAĞILIMI")
print("-"*40)


cursor.execute("""
SELECT 
ana_kategori,
COUNT(*)
FROM karar_konulari
GROUP BY ana_kategori
ORDER BY COUNT(*) DESC
""")


for row in cursor.fetchall():

    print(row[0],":",row[1])




# ==============================
# ALT KATEGORİ
# ==============================

print("\nALT KONU DAĞILIMI")
print("-"*40)


cursor.execute("""
SELECT 
alt_kategori,
COUNT(*)
FROM karar_konulari
GROUP BY alt_kategori
ORDER BY COUNT(*) DESC
""")


for row in cursor.fetchall():

    print(row[0],":",row[1])




# ==============================
# ETİKET ANALİZİ
# ==============================

print("\nGERÇEK ETİKET ANALİZİ")
print("-"*40)



cursor.execute("""
SELECT etiketler
FROM karar_konulari
WHERE etiketler IS NOT NULL
""")


etiket_listesi=[]



for row in cursor.fetchall():

    veri=row[0]


    if veri:

        parcalar=veri.split(",")


        for etiket in parcalar:

            etiket=etiket.strip()


            if len(etiket)>2:

                etiket_listesi.append(etiket)




sayac = Counter(etiket_listesi)



for etiket, adet in sayac.most_common(20):

    print(etiket,":",adet)




# ==============================
# KAPANIŞ
# ==============================


print("\n"+"="*70)
print(" İSTATİSTİK OLUŞTURMA TAMAMLANDI")
print("="*70)



conn.close()