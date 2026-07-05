import sqlite3


DB = "kik.db"



def mevzuat_getir(soru):

    soru = soru.lower()


    if (
        "iki şirket" in soru
        or "iki sirket" in soru
        or "aynı kişinin" in soru
        or "ayni kisinin" in soru
        or "birden fazla teklif" in soru
    ):

        return {

            "kanun":
            "4734 sayılı Kamu İhale Kanunu",

            "madde":
            "17/d maddesi",

            "konu":
            "Yasak fiil ve davranışlar - Birden fazla teklif verme yasağı"

        }


    return None





def karar_bul(soru):


    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    kararlar = cursor.execute("""

    SELECT

    karar_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke


    FROM hukuki_kartlar


    """).fetchall()


    conn.close()



    liste=[]



    soru_kelime = set(
        soru.lower().split()
    )



    for k in kararlar:


        skor=0



        alanlar=[

            k[1],
            k[2],
            k[3],
            k[5]

        ]



        metin=" ".join(
            alanlar
        ).lower()



        # kelime eşleşmesi

        for kelime in soru_kelime:


            if len(kelime)>2 and kelime in metin:

                skor += 1



        # güçlü konu eşleşmesi

        if "birden fazla teklif" in metin:

            if (
                "iki şirket" in soru.lower()
                or
                "iki sirket" in soru.lower()
                or
                "aynı kişinin" in soru.lower()
                or
                "ayni kisinin" in soru.lower()
            ):

                skor += 5




        if skor>0:


            liste.append({

                "karar":
                k[0],

                "konu":
                k[1],

                "soru":
                k[2],

                "yaklasim":
                k[3],

                "sonuc":
                k[4],

                "ilke":
                k[5],

                "skor":
                skor

            })




    liste.sort(

        key=lambda x:x["skor"],

        reverse=True

    )



    return liste[:1]







def guven(skor):


    if skor >= 7:

        return "Çok yüksek"


    elif skor >=4:

        return "Yüksek"


    else:

        return "Orta"







def rapor_uret(soru):


    print("\n")

    print("="*70)

    print("⚖️ KAMU İHALE KARAR AI - HUKUKİ DEĞERLENDİRME v2")

    print("="*70)



    print("\nSORU:")

    print(soru)



    print("\n")

    print("İLGİLİ MEVZUAT")

    print("-"*70)



    mevzuat = mevzuat_getir(soru)



    if mevzuat:


        print("\nKanun:")

        print(mevzuat["kanun"])



        print("\nMadde:")

        print(mevzuat["madde"])



        print("\nHukuki Konu:")

        print(mevzuat["konu"])




    print("\n")

    print("="*70)

    print("EMSAL KİK KARARI")

    print("="*70)



    kararlar = karar_bul(soru)



    if kararlar:


        k=kararlar[0]



        print("\nKarar No:")

        print(k["karar"])



        print("\nHukuki Sorun:")

        print(k["soru"])



        print("\nKİK Yaklaşımı:")

        print(k["yaklasim"])



        print("\nSonuç:")

        print(k["sonuc"])



        print("\nEmsal İlke:")

        print(k["ilke"])



        print("\nBenzerlik Güveni:")

        print(
            guven(k["skor"])
        )




    else:


        print("\nEmsal karar bulunamadı.")





    print("\n")

    print("="*70)

    print("UZMAN HUKUKİ SONUÇ")

    print("="*70)



    print("""
Kamu İhale Kurulu kararları ve ilgili mevzuat birlikte
değerlendirildiğinde;

Somut olay bakımından;

- isteklilerin teklif verme davranışı,
- taraflar arasındaki hukuki ilişki,
- yasak fiil ve davranış hükümleri,
- emsal Kurul uygulamaları

birlikte incelenmelidir.


Bu çıktı emsal karar destekli
yapay zeka hukuki değerlendirmesidir.

""")







def main():


    while True:


        soru=input(
            "\nHukuki soru (çıkış:q): "
        )


        if soru.lower()=="q":

            break



        rapor_uret(soru)





if __name__=="__main__":

    main()