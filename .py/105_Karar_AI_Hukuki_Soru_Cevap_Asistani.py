import sqlite3



DB="kik.db"



print("="*70)
print("⚖️ KAMU IHALE KARAR AI - HUKUKİ SORU CEVAP ASISTANI")
print("="*70)




def normalize(text):

    if not text:
        return ""


    text=text.lower()


    esleme={

    "aynı kişinin":"aynı şahıs",
    "kişinin":"şahıs",
    "iki şirket":"birden fazla şirket",
    "şirketle":"şirket aracılığıyla",
    "teklif vermesi":"teklif verilmesi",
    "vermesi":"verilmesi"

    }


    for a,b in esleme.items():

        text=text.replace(a,b)


    return text






def benzerlik(soru,icerik):


    soru=set(
        normalize(soru).split()
    )


    icerik=set(
        normalize(icerik).split()
    )



    ortak=len(
        soru.intersection(icerik)
    )



    if len(soru)==0:

        return 0



    return round(
        (ortak/len(soru))*100,
        2
    )







def karar_bul(soru):


    con=sqlite3.connect(DB)

    cur=con.cursor()



    cur.execute("""

    SELECT

    karar_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke,
    mevzuat,
    guven


    FROM hukuki_kartlar


    """)



    kararlar=cur.fetchall()


    con.close()



    sonuc=[]


    for k in kararlar:



        metin=" ".join([

        str(k[1]),
        str(k[2]),
        str(k[5]),
        str(k[6])

        ])



        skor=benzerlik(
            soru,
            metin
        )



        if skor>25:


            sonuc.append({

            "karar":k[0],
            "konu":k[1],
            "soru":k[2],
            "degerlendirme":k[3],
            "sonuc":k[4],
            "ilke":k[5],
            "mevzuat":k[6],
            "guven":k[7],
            "skor":skor


            })





    sonuc.sort(

    key=lambda x:x["skor"],

    reverse=True

    )


    return sonuc







while True:



    soru=input(

    "\nHukuki soru (çıkış:q): "

    )



    if soru=="q":

        break




    cevap=karar_bul(soru)



    print("\n")
    print("="*70)
    print("⚖️ HUKUKİ DEĞERLENDİRME")
    print("="*70)



    print("\nSORU:")
    print(soru)




    if not cevap:


        print("\nEmsal karar bulunamadı.")

        continue





    en=cevap[0]



    print("\n")
    print("İLGİLİ MEVZUAT")
    print("-"*70)


    if en["mevzuat"]:

        print(en["mevzuat"])

    else:

        print("4734 sayılı Kamu İhale Kanunu")





    print("\n")
    print("EMSAL KİK KARARI")
    print("-"*70)



    print("""

Karar No:
{}

Hukuki Konu:
{}

Hukuki Sorun:
{}

KİK Yaklaşımı:
{}

Sonuç:
{}

Emsal İlke:
{}

Güven:
{}

Benzerlik:
{} %

""".format(

en["karar"],
en["konu"],
en["soru"],
en["degerlendirme"],
en["sonuc"],
en["ilke"],
en["guven"],
en["skor"]

))





    print("="*70)
    print("UZMAN HUKUKİ SONUÇ")
    print("="*70)



    print("""

Kamu İhale Kurulu kararları ve ilgili mevzuat
birlikte değerlendirildiğinde;

Somut olay bakımından;

- isteklilerin teklif verme davranışı,
- taraflar arasındaki hukuki ilişki,
- yasak fiil ve davranış hükümleri,
- Kurul'un önceki uygulamaları

birlikte incelenmelidir.


Bu değerlendirme emsal karar destekli
yapay zeka hukuki analizidir.

""")


