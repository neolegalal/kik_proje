import sqlite3



DB="kik.db"



print("="*70)
print("KAMU IHALE KARAR AI - EMSAL ONCELIKLENDIRME MOTORU")
print("="*70)




def temiz(text):

    if not text:
        return ""

    return text.lower()




def kavram_normalize(text):


    text=temiz(text)


    donusum={

    "aynı kişinin":"aynı şahıs",
    "kişinin":"şahıs",
    "iki şirket":"birden fazla şirket",
    "şirketle":"şirket aracılığıyla",
    "teklif vermesi":"teklif verilmesi",
    "vermesi":"verilmesi"

    }


    for a,b in donusum.items():

        text=text.replace(a,b)


    return text





def oran(soru,metin):


    soru=set(
        kavram_normalize(soru).split()
    )


    metin=set(
        kavram_normalize(metin).split()
    )


    if not soru:

        return 0



    ortak=len(
        soru.intersection(metin)
    )


    return round(
        (ortak/len(soru))*100,
        2
    )





def karar_getir():



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


    data=cur.fetchall()


    con.close()


    return data






def emsal_hesapla(soru,k):


    karar_no,konu,hsoru,kurul,sonuc,ilke,mevzuat,guven=k



    hukuki_yakinlik=oran(

        soru,

        " ".join([
        konu,
        hsoru,
        ilke
        ])

    )



    mevzuat_puan=0


    if mevzuat and "4734" in mevzuat:

        mevzuat_puan=25



    ilke_puan=0


    if ilke:

        ilke_puan=25



    guven_puan=0


    if guven:


        if "yüksek" in guven.lower():

            guven_puan=10

        else:

            guven_puan=5




    toplam=(

    hukuki_yakinlik*0.40

    +

    mevzuat_puan

    +

    ilke_puan

    +

    guven_puan

    )



    return round(toplam,2)







while True:


    soru=input(

    "\nHukuki konu (çıkış:q): "

    )



    if soru=="q":

        break



    print("\n")
    print("="*70)
    print("EMSAL KARAR ONCELIK ANALIZI")
    print("="*70)



    sonuc=[]


    for k in karar_getir():


        puan=emsal_hesapla(
            soru,
            k
        )


        if puan>20:


            sonuc.append({

            "karar":k[0],
            "konu":k[1],
            "puan":puan,
            "ilke":k[5],
            "sonuc":k[4]


            })





    sonuc.sort(

    key=lambda x:x["puan"],

    reverse=True

    )



    if not sonuc:


        print(
        "Uygun emsal bulunamadı."
        )

        continue





    print("\nEN GÜÇLÜ EMSAL KARARLAR")
    print("-"*70)




    for i,s in enumerate(sonuc[:5],1):


        print(f"""

{i}. EMSAL KARAR


Karar:
{s['karar']}


Hukuki Konu:
{s['konu']}


EMSAL GÜCÜ:
{s['puan']}


Emsal İlke:
{s['ilke']}


Sonuç:
{s['sonuc']}


----------------------------------------

""")



    print("="*70)