import sqlite3
import re


DB="kik.db"


conn=sqlite3.connect(DB)
cursor=conn.cursor()


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - KANUN MOTORU V3")
print("="*70)



kararlar=cursor.execute("""
SELECT id,tam_metin
FROM kararlar
""").fetchall()



for karar in kararlar:


    karar_id=karar[0]
    metin=karar[1] or ""


    maddeler=[]



    # 5'inci, 39'uncu, 56'ncı vb.

    bulunan=re.findall(

        r"(\d+)\s*['’]?(inci|ıncı|nci|uncu|üncü)\s+madd",

        metin,
        flags=re.IGNORECASE

    )


    for madde,ek in bulunan:


        sayi=int(madde)


        if sayi < 100:


            veri="4734/"+str(sayi)


            if veri not in maddeler:

                maddeler.append(veri)




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
print(" V3 TAMAMLANDI")
print("="*70)



conn.close()