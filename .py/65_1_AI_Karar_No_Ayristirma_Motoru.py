import sqlite3
import re


DB = "kik.db"


print("=" * 70)
print("KAMU IHALE KARAR AI - KARAR NO AYRISTIRMA MOTORU")
print("=" * 70)


conn = sqlite3.connect(DB)
cursor = conn.cursor()


cursor.execute("""
SELECT id, dosya_adi
FROM kararlar
""")


kayitlar = cursor.fetchall()


guncel = 0
atlanmis = 0



for kayit_id, dosya_adi in kayitlar:

    print()
    print("-" * 60)
    print("Kontrol:")
    print(dosya_adi)


    # Örnek:
    # 2006.02.22_KIK_2007-UY.Z-3245.pdf

    temiz = dosya_adi.upper()


    eslesme = re.search(
        r'(20\d{2})[-_](UY|UH|UM)\.?Z?[-_\.]?(\d+)',
        temiz
    )


    if eslesme:

        yil = eslesme.group(1)
        seri = eslesme.group(2)
        numara = eslesme.group(3)


        karar_no = f"{yil}/{seri}.Z-{numara}"


        cursor.execute("""
        UPDATE kararlar
        SET karar_no=?
        WHERE id=?
        """,
        (
            karar_no,
            kayit_id
        ))


        print("Düzeltildi:")
        print(karar_no)


        guncel += 1


    else:

        print("Karar no ayrıştırılamadı")

        atlanmis += 1



conn.commit()
conn.close()



print()
print("=" * 70)
print("KARAR NO DUZELTME TAMAMLANDI")
print()
print("Güncellenen:")
print(guncel)

print()
print("Atlanan:")
print(atlanmis)

print("=" * 70)