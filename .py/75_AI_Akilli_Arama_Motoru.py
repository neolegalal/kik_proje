import sqlite3
import json
import re


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - AKILLI ARAMA MOTORU V2")
print("="*70)



def kelime_temizle(metin):

    if not metin:
        return []

    metin = metin.lower()

    metin = re.sub(
        r"[^a-zçğıöşü0-9 ]",
        " ",
        metin
    )

    kelimeler = metin.split()

    filtre = [
        "ve",
        "veya",
        "ile",
        "bir",
        "mi",
        "mı",
        "mu",
        "mü",
        "hangi",
        "nasıl"
    ]

    return [
        x for x in kelimeler
        if x not in filtre
    ]



def skor_hesapla(soru, karar):


    aranan = kelime_temizle(soru)


    alanlar = ""


    alanlar += str(
        karar["ai_soru_basligi"]
    )

    alanlar += " "

    alanlar += str(
        karar["ai_hukuki_konu_danisman"]
    )

    alanlar += " "

    alanlar += str(
        karar["ai_arama_kelime_danisman"]
    )

    alanlar += " "

    alanlar += str(
        karar["ai_anahtar_kelimeler"]
    )

    alanlar += " "

    alanlar += str(
        karar["ai_emsal_ilke"]
    )


    alanlar = alanlar.lower()


    skor = 0


    for kelime in aranan:


        if kelime in alanlar:

            skor += 10



        # soru başlığında geçerse daha değerli

        if kelime in str(
            karar["ai_soru_basligi"]
        ).lower():

            skor += 20



    return skor





def ara(soru, limit=5):


    conn = sqlite3.connect(DB)

    conn.row_factory = sqlite3.Row


    cursor = conn.cursor()



    cursor.execute("""

    SELECT *

    FROM kararlar

    """)


    kararlar = cursor.fetchall()


    sonuc = []



    for k in kararlar:


        veri = dict(k)


        skor = skor_hesapla(
            soru,
            veri
        )


        if skor > 0:


            veri["skor"] = skor


            sonuc.append(veri)



    conn.close()



    sonuc.sort(

        key=lambda x:x["skor"],

        reverse=True

    )


    return sonuc[:limit]






while True:


    print()

    soru = input(
        "Uzman sorusu: "
    )


    if soru=="çıkış":

        break



    bulunan = ara(
        soru
    )



    print()

    print(
        "Bulunan karar:"
    )


    print("-"*60)



    for s in bulunan:


        print(
            s["karar_no"]
        )


        print(
            "Soru:",
            s["ai_soru_basligi"]
        )


        print(
            "Skor:",
            s["skor"]
        )


        print("-"*60)



print("Bitti")