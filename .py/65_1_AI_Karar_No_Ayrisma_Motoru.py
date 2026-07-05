import sqlite3
import re


DB="kik.db"


conn=sqlite3.connect(DB)

c=conn.cursor()



c.execute("""

SELECT id,dosya_adi

FROM kararlar

""")


kayitlar=c.fetchall()


guncel=0



for id,dosya in kayitlar:


    m=re.search(
    r'(20\d{2})[-_](UY|UH|UM)\.?Z?[-.]?(\d+)',
    dosya.upper()
    )


    if m:


        yil=m.group(1)

        seri=m.group(2)

        no=m.group(3)


        karar_no=f"{yil}/{seri}.Z-{no}"



        c.execute("""

        UPDATE kararlar

        SET karar_no=?

        WHERE id=?

        """,

        (karar_no,id)

        )


        print(
        "Düzeltildi:",
        karar_no
        )


        guncel+=1




conn.commit()

conn.close()



print()

print("="*60)

print("KARAR NO DUZELTME TAMAMLANDI")

print()

print("Güncellenen:")

print(guncel)

print("="*60)