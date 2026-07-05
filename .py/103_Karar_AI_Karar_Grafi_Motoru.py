import sqlite3


DB = "kik.db"



print("="*70)
print("KAMU IHALE KARAR AI - KARAR GRAFI MOTORU")
print("="*70)



def temizle(metin):

    if not metin:
        return ""

    return metin.lower()



def benzerlik(a,b):

    a=set(temizle(a).split())
    b=set(temizle(b).split())


    if not a or not b:
        return 0


    ortak=len(a.intersection(b))


    toplam=len(a.union(b))


    return round(
        (ortak/toplam)*100,
        2
    )



def karar_getir():

    con=sqlite3.connect(DB)

    cur=con.cursor()


    cur.execute("""
    SELECT

    id,
    karar_no,
    baslik,
    hukuki_soru,
    emsal_ilke,
    mevzuat

    FROM hukuki_kartlar

    """)


    veriler=cur.fetchall()


    con.close()


    return veriler




def grafik_olustur(soru):


    kararlar=karar_getir()


    sonuc=[]


    for k in kararlar:


        metin=" ".join([

        str(k[2]),
        str(k[3]),
        str(k[4]),
        str(k[5])

        ])


        skor=benzerlik(
            soru,
            metin
        )


        if skor>5:


            sonuc.append({

            "karar_no":k[1],

            "konu":k[2],

            "skor":skor

            })



    sonuc.sort(
        key=lambda x:x["skor"],
        reverse=True
    )


    return sonuc[:10]





while True:


    soru=input(
    "\nHukuki konu (çıkış:q): "
    )


    if soru=="q":

        break



    print("\n")
    print("="*70)
    print("KARAR GRAFI ANALİZİ")
    print("="*70)



    sonuc=grafik_olustur(
        soru
    )



    if not sonuc:

        print(
        "Bağlantılı karar bulunamadı."
        )

        continue



    print("\nAna konu:")
    print(soru)



    print("\nBENZER KARAR AĞI")
    print("-"*70)



    for i,k in enumerate(sonuc,1):


        print(
        f"""
{i}. Karar

Karar No:
{k['karar_no']}

Bağlantılı Konu:
{k['konu']}

Benzerlik:
{k['skor']} %

----------------------------------------
"""
        )



    print("="*70)