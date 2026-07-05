import sqlite3


DB = "kik.db"



def temizle(metin):

    if not metin:
        return ""

    return metin



def mevzuat_getir(soru):


    soru = soru.lower()


    sonuc = []


    if (
        "iki şirket" in soru
        or "iki sirket" in soru
        or "aynı kişinin" in soru
        or "ayni kisinin" in soru
        or "birden fazla teklif" in soru
    ):


        sonuc.append({

            "kanun":
            "4734 sayılı Kamu İhale Kanunu",

            "madde":
            "17/d maddesi",

            "konu":
            "Yasak fiil ve davranışlar - Birden fazla teklif verme yasağı"

        })


    return sonuc





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



    bulunan=[]



    for k in kararlar:


        metin = (

            str(k[1])
            +
            str(k[2])
            +
            str(k[3])
            +
            str(k[5])

        ).lower()



        skor=0



        for kelime in soru.lower().split():

            if len(kelime)>2 and kelime in metin:

                skor +=1



        if skor>=3:


            bulunan.append({

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



    bulunan.sort(

        key=lambda x:x["skor"],

        reverse=True

    )


    return bulunan[:1]







def guven(skor):


    if skor>=6:

        return "Çok yüksek"


    elif skor>=4:

        return "Yüksek"


    else:

        return "Orta"







def rapor_uret(soru):


    print("\n")

    print("="*70)

    print("⚖️ KAMU İHALE KARAR AI - HUKUKİ DEĞERLENDİRME")

    print("="*70)



    print("\nSORU:")

    print(soru)



    print("\n")

    print("İLGİLİ MEVZUAT")

    print("-"*70)



    mevzuatlar = mevzuat_getir(soru)



    for m in mevzuatlar:


        print("\nKanun:")

        print(m["kanun"])



        print("\nMadde:")

        print(m["madde"])



        print("\nHukuki Konu:")

        print(m["konu"])




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


        print("\nUygun emsal karar bulunamadı.")






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