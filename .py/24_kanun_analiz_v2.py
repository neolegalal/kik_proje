import sqlite3
from collections import Counter,defaultdict


DB="kik.db"


conn=sqlite3.connect(DB)
c=conn.cursor()


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - KANUN ANALİZ MOTORU V2")
print("="*70)



# Süreç maddeleri
destek_maddeler=[
"4734/53",
"4734/54",
"4734/65"
]


# Ana analiz maddeleri
ana_maddeler=[
"4734/5",
"4734/10",
"4734/38",
"4734/39",
"4734/40",
"4734/41",
"4734/55",
"4734/56"
]



istatistik={}



for madde in ana_maddeler:


    istatistik[madde]={
        "adet":0,
        "konular":Counter(),
        "sonuclar":Counter()
    }



rows=c.execute("""
SELECT
kararlar.kanun_maddeleri,
kararlar.karar_sonucu,
karar_konulari.alt_kategori

FROM kararlar

LEFT JOIN karar_konulari

ON kararlar.id = karar_konulari.karar_id

""").fetchall()



for kanun,sonuc,konu in rows:


    if not kanun:
        continue


    maddeler=[
        x.strip()
        for x in kanun.split(",")
    ]


    for madde in maddeler:


        if madde in ana_maddeler:


            istatistik[madde]["adet"]+=1


            if sonuc:
                istatistik[madde]["sonuclar"][sonuc]+=1


            if konu:
                istatistik[madde]["konular"][konu]+=1





sirali=[]



for madde,data in istatistik.items():


    print("\n")
    print("-"*60)

    print(madde)


    print(
        "Gerçek kullanım:",
        data["adet"],
        "karar"
    )


    if data["konular"]:


        print("\nKonular:")


        for k,v in data["konular"].most_common():

            print(
                "-",
                k,
                ":",
                v
            )



    print("\nSonuç:")


    for s,v in data["sonuclar"].most_common():

        print(
            "-",
            s,
            ":",
            v
        )



    if data["adet"]:


        lehine=0


        for s,v in data["sonuclar"].items():

            if (
                "Düzeltici" in s
                or
                "İptal" in s
            ):

                lehine+=v



        oran=round(
            lehine/data["adet"]*100
        )


        print(
            "\nBaşvuru lehine oran:",
            "%",
            oran
        )


        sirali.append(
            (
                madde,
                oran,
                data["adet"]
            )
        )




print("\n")
print("="*70)

print(" EN ETKİLİ KANUN MADDELERİ")

print("="*70)



for m,o,a in sorted(
    sirali,
    key=lambda x:x[1],
    reverse=True
):


    print(
        m,
        "->",
        "%",
        o,
        "başvuru lehine",
        "(",
        a,
        "karar )"
    )




print("\n")
print("="*70)

print(" DESTEK MADDELERİ")

print("="*70)



for m in destek_maddeler:


    count=c.execute("""
    SELECT COUNT(*)
    FROM kararlar

    WHERE kanun_maddeleri LIKE ?
    """,
    ("%"+m+"%",)).fetchone()[0]


    print(
        m,
        ":",
        count,
        "karar"
    )



conn.close()


print("\n")
print("="*70)
print(" KANUN ANALİZ V2 TAMAMLANDI")
print("="*70)