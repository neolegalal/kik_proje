import sqlite3


DB="kik.db"



print("="*70)
print("KAMU IHALE KARAR AI - KARAR GRAFI MOTORU v2")
print("="*70)



ES_ANLAM={

"aynı":"aynı şahıs",
"kişi":"şahıs",
"kişinin":"şahıs",
"şirketle":"şirket aracılığıyla",
"iki şirket":"birden fazla şirket",
"teklif vermesi":"teklif verilmesi",
"vermesi":"verilmesi",
"yasak":"yasak fiil",
"kanun":"mevzuat"

}




def normalize(text):


    text=text.lower()


    for k,v in ES_ANLAM.items():

        text=text.replace(
            k,
            v
        )


    return text




def benzerlik(soru,metin):


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
        (ortak/len(soru))*100,
        2
    )





def kararlar():


    con=sqlite3.connect(DB)

    cur=con.cursor()


    cur.execute("""

    SELECT

    karar_no,
    baslik,
    hukuki_soru,
    emsal_ilke


    FROM hukuki_kartlar

    """)


    data=cur.fetchall()


    con.close()


    return data





def analiz(soru):


    sonuc=[]


    for k in kararlar():


        metin=" ".join([

        str(k[1]),
        str(k[2]),
        str(k[3])

        ])



        skor=benzerlik(
            soru,
            metin
        )


        if skor>20:


            sonuc.append({

            "karar":k[0],

            "konu":k[1],

            "skor":skor

            })



    sonuc.sort(
        key=lambda x:x["skor"],
        reverse=True
    )


    return sonuc





while True:


    soru=input(
    "\nHukuki konu (çıkış:q): "
    )



    if soru=="q":

        break



    print("\n")
    print("="*70)
    print("HUKUKİ KARAR AĞI")
    print("="*70)



    sonuc=analiz(soru)



    for i,k in enumerate(sonuc,1):


        print(f"""

{i}. KARAR

Karar:
{k['karar']}


Bağlantılı Konu:
{k['konu']}


Hukuki Yakınlık:
{k['skor']} %

----------------------------------------

""")
