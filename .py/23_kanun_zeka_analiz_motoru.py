import sqlite3
from collections import Counter


DB="kik.db"


conn=sqlite3.connect(DB)
c=conn.cursor()


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - KANUN ZEKA ANALİZ MOTORU")
print("="*70)



onemli_maddeler=[
"4734/5",
"4734/10",
"4734/38",
"4734/39",
"4734/40",
"4734/41",
"4734/54",
"4734/55",
"4734/56"
]



for madde in onemli_maddeler:

    print("\n")
    print("-"*50)

    print(madde)


    rows=c.execute("""
    SELECT 
    karar_sonucu
    FROM kararlar
    WHERE kanun_maddeleri LIKE ?
    """,
    ("%"+madde+"%",)).fetchall()



    print(
        "Kullanım:",
        len(rows),
        "karar"
    )



    sonuc=Counter()


    for r in rows:

        sonuc[r[0]]+=1



    print("\nSonuç:")


    for k,v in sonuc.items():

        print(
            "-",
            k,
            ":",
            v
        )



    if len(rows)>0:


        olumlu=0


        for r in rows:


            if (
                "Düzeltici" in r[0]
                or
                "İptal" in r[0]
            ):

                olumlu+=1



        oran=round(
            olumlu/len(rows)*100
        )


        print("\nBaşarı oranı:")

        print(
            "%",
            oran,
            "başvuru lehine sonuç"
        )




print("\n")
print("="*70)
print(" KANUN ZEKA ANALİZ TAMAMLANDI")
print("="*70)


conn.close()