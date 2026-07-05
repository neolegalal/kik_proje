from flask import Flask, request, jsonify
import sqlite3


app = Flask(__name__)


DB = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"





def karar_ara(soru):


    conn = sqlite3.connect(DB)

    c = conn.cursor()



    soru_lower = soru.lower()



    kelimeler = [

        x.lower()

        for x in soru.replace("?", " ").replace(",", " ").split()

    ]





    rows = c.execute("""
    
    SELECT

    k.karar_no,
    kk.soru_basligi,
    kk.karar_ozeti,
    kk.karar_sonucu,
    kk.ana_kategori,
    kk.anahtar_kelimeler


    FROM karar_konulari kk


    JOIN kararlar k

    ON kk.karar_id = k.id


    """).fetchall()





    sonuc=[]





    for r in rows:



        kategori = str(r[4] or "").lower()



        metin = " ".join([

            str(r[1] or ""),
            str(r[2] or ""),
            str(r[3] or ""),
            str(r[4] or ""),
            str(r[5] or "")

        ]).lower()





        puan = 0





        # AŞIRI DÜŞÜK ÖZEL FİLTRE

        if "aşırı düşük" in soru_lower:



            if "a08" not in kategori:


                continue




        for kelime in kelimeler:



            if len(kelime) > 3 and kelime in metin:


                puan += 1






        if "aşırı düşük" in soru_lower:



            if "a08" in kategori:


                puan += 10






        if puan > 0:



            sonuc.append({

                "puan": puan,

                "karar_no": r[0],

                "baslik": r[1],

                "kategori": r[4],

                "ozet": r[2],

                "sonuc": r[3]

            })





    conn.close()




    sonuc.sort(

        key=lambda x:x["puan"],

        reverse=True

    )



    return sonuc[:5]







@app.route("/", methods=["GET"])

def ana():

    return jsonify({

        "sistem":
        "Kamu Ihale Karar AI API",

        "durum":
        "aktif"

    })









@app.route("/sor", methods=["POST"])

def sor():



    data = request.get_json()



    soru = data.get("soru","")




    if not soru:


        return jsonify({

            "hata":
            "Soru girilmedi"

        })





    kararlar = karar_ara(soru)





    return jsonify({

        "soru": soru,

        "karar_sayisi":

        len(kararlar),


        "sonuclar":

        kararlar

    })









if __name__ == "__main__":


    print("="*70)

    print("KAMU IHALE KARAR SISTEMI - AI API MOTORU")

    print("="*70)



    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )