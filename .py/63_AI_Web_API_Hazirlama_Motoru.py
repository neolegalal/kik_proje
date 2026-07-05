import sqlite3
from flask import Flask, request, jsonify


DB = "kik.db"

app = Flask(__name__)


print("="*70)
print("KAMU IHALE KARAR AI - WEB API MOTORU")
print("="*70)



def baglan():

    conn = sqlite3.connect(DB)

    conn.row_factory = sqlite3.Row

    return conn



# ------------------------------------------------
# ANA SAYFA
# ------------------------------------------------

@app.route("/")
def ana():

    return jsonify({

        "sistem":
        "Kamu Ihale Karar AI",

        "durum":
        "aktif",

        "versiyon":
        "1.0"

    })



# ------------------------------------------------
# KARARLAR
# ------------------------------------------------

@app.route("/kararlar")
def karar_listesi():

    conn = baglan()

    cursor = conn.cursor()


    cursor.execute("""

    SELECT

    karar_no,
    soru_basligi,
    kisa_ozet,
    kategori

    FROM ai_karar_kartlari

    LIMIT 50

    """)


    sonuc = cursor.fetchall()

    conn.close()



    return jsonify([dict(x) for x in sonuc])




# ------------------------------------------------
# ARAMA
# ------------------------------------------------


@app.route("/arama")
def arama():


    kelime = request.args.get(
        "q",
        ""
    )


    conn = baglan()

    cursor = conn.cursor()



    cursor.execute("""

    SELECT

    karar_no,
    soru_basligi,
    kisa_ozet,
    kategori


    FROM ai_karar_kartlari


    WHERE


    soru_basligi LIKE ?

    OR

    kisa_ozet LIKE ?


    LIMIT 20


    """,

    (

    "%" + kelime + "%",

    "%" + kelime + "%"

    ))



    sonuc = cursor.fetchall()

    conn.close()



    return jsonify([dict(x) for x in sonuc])




# ------------------------------------------------
# SORU SORMA
# ------------------------------------------------


@app.route("/soru", methods=["POST"])

def soru_motoru():


    veri = request.json


    soru = veri.get(
        "soru",
        ""
    )


    conn = baglan()

    cursor = conn.cursor()



    cursor.execute("""

    SELECT


    karar_no,

    soru_basligi,

    kisa_ozet,

    kategori,

    ai_cevap


    FROM ai_karar_kartlari


    WHERE


    ai_soru LIKE ?

    OR

    ai_cevap LIKE ?


    LIMIT 5


    """,

    (

    "%" + soru + "%",

    "%" + soru + "%"

    ))



    sonuc = cursor.fetchall()


    conn.close()



    return jsonify({

        "soru":

        soru,


        "emsal_kararlar":

        [

        dict(x)

        for x in sonuc

        ]

    })




# ------------------------------------------------
# KARAR DETAY
# ------------------------------------------------


@app.route("/karar/<karar_no>")

def karar_detay(karar_no):


    conn = baglan()

    cursor = conn.cursor()



    cursor.execute("""

    SELECT *

    FROM ai_karar_kartlari

    WHERE karar_no=?

    """,

    (karar_no,))



    sonuc = cursor.fetchone()


    conn.close()



    if sonuc:


        return jsonify(dict(sonuc))


    else:


        return jsonify({

            "hata":
            "Karar bulunamadı"

        })




# ------------------------------------------------
# BASLAT
# ------------------------------------------------


if __name__ == "__main__":


    print()

    print("API BASLATILIYOR")

    print()

    print(
    "http://127.0.0.1:5000"
    )


    app.run(

        host="0.0.0.0",

        port=5000

    )