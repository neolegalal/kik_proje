import sqlite3
import re


DB="kik.db"


conn=sqlite3.connect(DB)
cursor=conn.cursor()


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - KANUN MOTORU V4")
print("="*70)



kararlar=cursor.execute("""
SELECT id,tam_metin
FROM kararlar
""").fetchall()



for karar in kararlar:


    karar_id=karar[0]
    metin=karar[1] or ""


    maddeler=[]


    # sadece Kanun atıflarını yakala

    pattern=r"""

    (?:

    4734\s*sayılı\s*Kamu\s*İhale\s*Kanunu

    |

    Kanun

    )

    .*?

    (\d+)

    \s*['’]?

    (?:inci|ıncı|nci|uncu|üncü)

    \s*madd

    """


    bulunan=re.findall(
        pattern,
        metin,
        flags=re.IGNORECASE | re.VERBOSE
    )



    for m in bulunan:


        madde=int(m)


        # genel filtre

        if madde in [
            1,2,3,4,5,6,7,8,9,
            10,11,12,13,14,15,
            16,17,18,19,20,
            21,22,23,24,25,
            26,27,28,29,30,
            31,32,33,34,35,
            36,37,38,39,40,
            41,42,43,44,45,
            46,47,48,49,
            50,51,52,53,54,
            55,56,57,58,59,
            60,61,62,63,64,65
        ]:


            veri="4734/"+str(madde)


            if veri not in maddeler:

                maddeler.append(veri)



    cursor.execute("""

    UPDATE kararlar

    SET kanun_maddeleri=?

    WHERE id=?

    """,
    (
    ", ".join(maddeler),
    karar_id
    ))



    print(
        karar_id,
        ", ".join(maddeler)
    )



conn.commit()


print()
print("="*70)
print(" V4 TAMAMLANDI")
print("="*70)


conn.close()