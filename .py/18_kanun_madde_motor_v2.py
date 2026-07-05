import sqlite3
import re


DB="kik.db"


conn=sqlite3.connect(DB)
cursor=conn.cursor()


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - GELİŞMİŞ KANUN MOTORU")
print("="*70)



kararlar=cursor.execute("""
SELECT id,tam_metin
FROM kararlar
""").fetchall()



for k in kararlar:


    karar_id=k[0]
    metin=k[1] or ""

    maddeler=[]



    # 4734 sayılı Kanun'un ... maddeleri

    bulunan=re.findall(
        r"(?:Kanunu|Kanun[u]?)’?n?un?\s+.*?(\d+)[’']?uncu\s+madd",
        metin
    )



    for m in bulunan:

        madde="4734/"+m

        if madde not in maddeler:

            maddeler.append(madde)



    # direkt madde yakalama

    bulunan2=re.findall(
        r"(\d+)[’']?uncu\s+maddesi",
        metin
    )


    for m in bulunan2:

        if int(m) < 100:

            madde="4734/"+m

            if madde not in maddeler:

                maddeler.append(madde)



    sonuc=", ".join(maddeler)



    cursor.execute("""
    UPDATE kararlar
    SET kanun_maddeleri=?
    WHERE id=?
    """,
    (
    sonuc,
    karar_id
    ))



    print(
    karar_id,
    sonuc
    )



conn.commit()



print()
print("="*70)
print(" KANUN VERİLERİ GÜNCELLENDİ")
print("="*70)



conn.close()