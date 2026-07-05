import sqlite3
import difflib


DB="kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - UZMAN CEVAP MOTORU")
print("="*70)



def benzerlik(a,b):

    return difflib.SequenceMatcher(
        None,
        a.lower(),
        b.lower()
    ).ratio()



def cevap_uret(soru):


    con=sqlite3.connect(DB)

    c=con.cursor()


    kartlar=c.execute("""
    SELECT
    karar_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke

    FROM hukuki_kartlar

    """).fetchall()



    sonuc=[]


    for k in kartlar:


        puan=0


        puan+=benzerlik(
            soru,
            k[1]
        )


        puan+=benzerlik(
            soru,
            k[2]
        )


        if soru.lower() in k[2].lower():

            puan+=1



        sonuc.append(
            (
            puan,
            k
            )
        )



    sonuc.sort(
        reverse=True,
        key=lambda x:x[0]
    )



    secilen=[]


    for x in sonuc:

        if x[0] >0.25:

            secilen.append(x[1])


        if len(secilen)==3:

            break




    if not secilen:

        print("\nEmsal karar bulunamadı.")

        return




    print("\n")
    print("="*70)

    print("HUKUKİ DEĞERLENDİRME")
    print()


    print(
    "Sorulan konu: ",
    soru
    )



    print("\n")


    print("EMSAL KARAR ANALİZİ")



    for k in secilen:


        print("-"*70)


        print(
        "Karar:",
        k[0]
        )


        print(
        "Konu:",
        k[1]
        )



        print(
        "\nKurul yaklaşımı:"
        )


        print(
        k[3]
        )



        print(
        "\nSonuç:"
        )


        print(
        k[4]
        )



    print("-"*70)


    print("\nGENEL HUKUKİ SONUÇ")


    print(

    "Kamu İhale Kurulu uygulamasında, "

    "aynı hukuki niteliğe sahip işlemler değerlendirilirken "

    "isteklilerin teklif verme davranışları ve "

    "ihale mevzuatındaki yasak fiil ve davranış hükümleri "

    "birlikte dikkate alınmaktadır."

    )



    print("\nEMSAL İLKE")


    print(
    secilen[0][5]
    )


    print("\nKaynak kararlar:")


    for k in secilen:

        print(
        "-",
        k[0]
        )


    print("="*70)




while True:


    soru=input(
    "\nHukuki soru (çıkış:q): "
    )


    if soru=="q":

        break


    cevap_uret(soru)