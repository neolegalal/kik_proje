import requests


API_URL = "http://127.0.0.1:5000/ara"



def guven_hesapla(skor):

    if skor >= 20:
        return "Çok yüksek"

    elif skor >= 12:
        return "Yüksek"

    elif skor >= 6:
        return "Orta"

    else:
        return "Düşük"





def rapor_uret(soru):


    cevap = requests.post(

        API_URL,

        json={

            "soru": soru

        }

    ).json()



    sonuclar = cevap.get(

        "sonuclar",

        []

    )



    if not sonuclar:


        print("\nEmsal karar bulunamadı.")

        return





    print("\n")

    print("="*70)

    print("HUKUKİ UZMAN RAPORU")

    print("="*70)



    print("\nSORULAN KONU:")

    print(soru)





    print("\n")

    print("EMSAL KARAR ANALİZİ")

    print("-"*70)



    for i,kart in enumerate(sonuclar,1):



        guven = guven_hesapla(

            kart.get(

                "skor",

                0

            )

        )



        print("\n")

        print(f"{i}. EMSAL KARAR")

        print("-"*40)



        print(

        "Karar No:",

        kart["karar_no"]

        )



        print(

        "\nHukuki Konu:"

        )

        print(

        kart["konu"]

        )



        print(

        "\nSorun:"

        )

        print(

        kart["hukuki_soru"]

        )



        print(

        "\nKİK Yaklaşımı:"

        )

        print(

        kart["kurul_degerlendirmesi"]

        )



        print(

        "\nSonuç:"

        )

        print(

        kart["sonuc"]

        )



        print(

        "\nEmsal İlke:"

        )

        print(

        kart["emsal_ilke"]

        )



        print(

        "\nBenzerlik Güveni:"

        )

        print(

        guven

        )



        print("-"*70)







    print("\n")

    print("GENEL HUKUKİ DEĞERLENDİRME")

    print("-"*70)



    en_iyi = sonuclar[0]



    print(

    f"""

Kamu İhale Kurulu kararları birlikte değerlendirildiğinde;

"{soru}"

konusundaki uygulamada,

{en_iyi["emsal_ilke"]}

Bu nedenle benzer uyuşmazlıklarda öncelikle teklif verme
davranışı, istekliler arasındaki ilişki ve ihale mevzuatındaki
yasak fiil ve davranış hükümleri birlikte incelenmelidir.

"""

    )



    print("="*70)







if __name__ == "__main__":



    print("="*70)

    print(

    "KAMU IHALE KARAR AI - UZMAN RAPOR MOTORU"

    )

    print("="*70)



    while True:


        soru=input(

        "\nHukuki soru (çıkış:q): "

        )



        if soru.lower()=="q":

            break



        rapor_uret(soru)