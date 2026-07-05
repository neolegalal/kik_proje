import sqlite3
from collections import Counter


DB="kik.db"

conn=sqlite3.connect(DB)
cur=conn.cursor()


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - KANUN KONUSAL ANALİZ MOTORU")
print("="*70)


rows=cur.execute("""
SELECT 
kararlar.kanun_maddeleri,
karar_konulari.alt_kategori,
kararlar.karar_sonucu

FROM kararlar

JOIN karar_konulari
ON kararlar.id = karar_konulari.karar_id

WHERE kararlar.kanun_maddeleri IS NOT NULL

""").fetchall()



kanunlar={}



for madde, konu, sonuc in rows:

    if not madde:
        continue


    maddeler=[
        x.strip()
        for x in madde.split(",")
    ]


    for m in maddeler:

        if m not in kanunlar:
            kanunlar[m]={
                "konu":Counter(),
                "sonuc":Counter(),
                "adet":0
            }


        kanunlar[m]["adet"]+=1


        if konu:
            kanunlar[m]["konu"][konu]+=1


        if sonuc:
            kanunlar[m]["sonuc"][sonuc]+=1




for m,data in sorted(
    kanunlar.items(),
    key=lambda x:x[1]["adet"],
    reverse=True
):


    print("\n")
    print("-"*40)

    print(m)

    print(
        "Kullanım:",
        data["adet"],
        "karar"
    )


    print("\nKonular:")

    if data["konu"]:

        for k,v in data["konu"].most_common():

            print(
                "-",
                k,
                ":",
                v
            )

    else:

        print("Yok")



    print("\nSonuçlar:")

    for s,v in data["sonuc"].most_common():

        print(
            "-",
            s,
            ":",
            v
        )



conn.close()


print("\n")
print("="*70)
print(" KANUN KONU ANALİZ TAMAMLANDI")
print("="*70)