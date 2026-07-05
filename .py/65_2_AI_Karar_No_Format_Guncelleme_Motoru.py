import sqlite3
import re


DB="kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - YENI FORMAT KARAR NO MOTORU")
print("="*70)


conn=sqlite3.connect(DB)
cursor=conn.cursor()



cursor.execute("""
SELECT id,dosya_adi
FROM kararlar
WHERE karar_no IS NULL
OR karar_no=''
""")


kayitlar=cursor.fetchall()



guncel=0



for id,dosya in kayitlar:


    print()
    print("-"*60)
    print(dosya)



    temiz=dosya.upper()



    # yeni format
    # 2026.06.04_KIK_2026-UY.II-1482.pdf


    m=re.search(
        r'(20\d{2})[-](UY\.II|UY\.I|UH\.II|UH\.I|UM\.II|UM\.I)[-](\d+)',
        temiz
    )



    if m:


        yil=m.group(1)
        seri=m.group(2)
        no=m.group(3)



        karar_no=f"{yil}/{seri}-{no}"



        cursor.execute("""
        UPDATE kararlar
        SET karar_no=?
        WHERE id=?
        """,
        (
            karar_no,
            id
        ))


        print("Düzeltildi:")
        print(karar_no)


        guncel+=1



conn.commit()
conn.close()



print()
print("="*70)
print("YENI FORMAT TAMAMLANDI")
print()
print("Güncellenen:")
print(guncel)
print("="*70)