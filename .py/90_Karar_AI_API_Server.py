import sqlite3
import re

from flask import Flask, request, jsonify


DB = "kik.db"


app = Flask(__name__)


# --------------------------------------------------
# METİN TEMİZLEME
# --------------------------------------------------

def temizle(metin):

    if not metin:
        return ""

    metin = metin.lower()

    karakter = {
        "ı":"i",
        "ğ":"g",
        "ü":"u",
        "ş":"s",
        "ö":"o",
        "ç":"c"
    }

    for k,v in karakter.items():
        metin = metin.replace(k,v)

    return metin



def kelimeler(metin):

    return set(
        re.findall(
            r"\w+",
            temizle(metin)
        )
    )



# --------------------------------------------------
# PUANLAMA MOTORU
# --------------------------------------------------

def puanla(soru,kart):

    soru_kelime = kelimeler(soru)

    toplam = 0


    alanlar = [

        ("baslik",5),
        ("anahtar_kelime",5),
        ("hukuki_soru",4),
        ("iddia_ozeti",3),
        ("emsal_ilke",2),
        ("mevzuat",2)

    ]


    for alan,puan in alanlar:

        metin = kart[alan]

        ortak = soru_kelime.intersection(
            kelimeler(metin)
        )


        toplam += len(ortak)*puan



    return toplam




# --------------------------------------------------
# KARAR ARAMA
# --------------------------------------------------

def karar_ara(soru):


    conn = sqlite3.connect(DB)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()



    kartlar = cursor.execute(

        """
        SELECT *
        FROM hukuki_kartlar

        """

    ).fetchall()



    sonuc=[]



    for kart in kartlar:


        skor = puanla(
            soru,
            kart
        )


        if skor > 3:

            sonuc.append(

                {
                "skor":skor,
                "kart":kart

                }

            )



    conn.close()



    sonuc.sort(

        key=lambda x:x["skor"],
        reverse=True

    )


    return sonuc[:5]





# --------------------------------------------------
# API ENDPOINT
# --------------------------------------------------

@app.route(
    "/ara",
    methods=["POST"]
)

def ara():



    veri=request.get_json()



    soru=veri.get(
        "soru",
        ""
    )



    if not soru:

        return jsonify(

            {
            "hata":
            "Soru gönderilmedi"
            }

        )



    sonuclar = karar_ara(
        soru
    )



    cevap=[]



    for item in sonuclar:


        kart=item["kart"]



        cevap.append(

            {

            "karar_no":
            kart["karar_no"],


            "konu":
            kart["baslik"],


            "hukuki_soru":
            kart["hukuki_soru"],


            "kurul_degerlendirmesi":
            kart["kurul_degerlendirmesi"],


            "sonuc":
            kart["sonuc"],


            "emsal_ilke":
            kart["emsal_ilke"],


            "guven":
            kart["guven"],


            "skor":
            item["skor"]

            }

        )



    return jsonify(

        {

        "soru":
        soru,


        "sonuclar":
        cevap

        }

    )





# --------------------------------------------------
# ÇALIŞTIR
# --------------------------------------------------

if __name__=="__main__":


    print("="*70)

    print(
    "KAMU IHALE KARAR AI - API SERVER"
    )

    print("="*70)


    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )