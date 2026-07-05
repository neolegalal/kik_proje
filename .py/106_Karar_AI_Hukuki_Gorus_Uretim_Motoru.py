import sqlite3



DB="kik.db"



print("="*70)
print("⚖️ KAMU IHALE KARAR AI - HUKUKİ GÖRÜŞ ÜRETİM MOTORU")
print("="*70)





def normalize(text):

    if not text:
        return ""


    text=text.lower()


    degisim={

    "aynı kişinin":"aynı şahıs",
    "iki şirket":"birden fazla şirket",
    "şirketle":"şirket aracılığıyla",
    "teklif vermesi":"teklif verilmesi"

    }


    for a,b in degisim.items():

        text=text.replace(a,b)


    return text






def skor_hesapla(soru,metin):


    soru=set(
        normalize(soru).split()
    )


    metin=set(
        normalize(metin).split()
    )



    ortak=len(
        soru.intersection(metin)
    )



    if len(soru)==0:

        return 0



    return round(
        ortak/len(soru)*100,
        2
    )






def emsal_getir(soru):


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



    rows=cur.fetchall()


    con.close()



    liste=[]



    for r in rows:


        metin=" ".join([

        str(r[1]),
        str(r[2]),
        str(r[5]),
        str(r[6])

        ])



        skor=skor_hesapla(
            soru,
            metin
        )



        if skor>=30:


            liste.append({

            "karar":r[0],
            "konu":r[1],
            "soru":r[2],
            "yaklasim":r[3],
            "sonuc":r[4],
            "ilke":r[5],
            "mevzuat":r[6],
            "guven":r[7],
            "skor":skor

            })




    liste.sort(

    key=lambda x:x["skor"],

    reverse=True

    )


    return liste






while True:


    soru=input(
    "\nHukuki soru (çıkış:q): "
    )


    if soru=="q":

        break




    kararlar=emsal_getir(soru)



    print("\n")
    print("="*70)
    print("⚖️ HUKUKİ UZMAN GÖRÜŞÜ")
    print("="*70)



    print("\nSORU:")

    print(soru)




    if not kararlar:


        print("\nEmsal karar bulunamadı.")

        continue





    k=kararlar[0]




    print("\nEMSAL KARAR")

    print("-"*70)


    print("""

Karar No:
{}

Hukuki Konu:
{}

Kurul Yaklaşımı:
{}

Sonuç:
{}

Emsal İlke:
{}

Mevzuat:
{}

Güven:
{}

""".format(

k["karar"],
k["konu"],
k["yaklasim"],
k["sonuc"],
k["ilke"],
k["mevzuat"] if k["mevzuat"] else "4734 sayılı Kamu İhale Kanunu",
k["guven"]

))





    print("="*70)
    print("UZMAN DEĞERLENDİRME")
    print("="*70)




    print("""


Kamu İhale Kurulu kararları ve ilgili mevzuat
birlikte değerlendirildiğinde;


Somut olay bakımından öncelikle;

- isteklilerin hukuki ilişkisi,
- tekliflerin hangi kişiler tarafından verildiği,
- şirketler arasındaki bağlantı,
- yasak fiil ve davranış hükümleri


birlikte incelenmelidir.



Emsal Kurul uygulamasında;

aynı hukuki kişi veya bağlantılı kişiler üzerinden
birden fazla teklif verilmesi,
ihale rekabeti ve teklif güvenilirliği bakımından
değerlendirilmektedir.



SONUÇ:

Somut olayın özellikleri emsal karar ile
uyumlu ise, tekliflerin birden fazla teklif verme yasağı
kapsamında değerlendirilmesi mümkündür.



Bu çıktı;

Kamu İhale Kurulu kararları,
mevzuat bağlantıları ve emsal ilkeler
esas alınarak oluşturulan
yapay zeka destekli hukuki değerlendirmedir.



""")


