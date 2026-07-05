import sqlite3
from flask import Flask, request, jsonify, render_template_string


DB = "kik.db"


app = Flask(__name__)





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


    return {

        "kanun":
        "Belirlenemedi",

        "madde":
        "",

        "konu":
        ""

    }







def karar_ara(soru):


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



    sonuc=[]



    kelimeler=set(
        soru.lower().split()
    )



    for k in kararlar:


        skor=0


        metin=" ".join([

            str(k[1]),
            str(k[2]),
            str(k[3]),
            str(k[5])

        ]).lower()



        for kelime in kelimeler:


            if len(kelime)>2 and kelime in metin:

                skor+=1




        if (
            "iki şirket" in soru.lower()
            or
            "iki sirket" in soru.lower()
        ):


            if "birden fazla teklif" in metin:

                skor+=5




        if skor>0:


            sonuc.append({

                "karar_no":k[0],

                "konu":k[1],

                "hukuki_soru":k[2],

                "kurul_degerlendirmesi":k[3],

                "sonuc":k[4],

                "emsal_ilke":k[5],

                "skor":skor

            })




    sonuc.sort(

        key=lambda x:x["skor"],

        reverse=True

    )



    return sonuc[:5]








def guven(skor):


    if skor>=7:

        return "Çok yüksek"

    elif skor>=4:

        return "Yüksek"

    else:

        return "Orta"








@app.route("/ara", methods=["POST"])
def ara():


    data=request.json


    soru=data.get(
        "soru",
        ""
    )



    kararlar=karar_ara(soru)



    for k in kararlar:


        k["guven"]=guven(
            k["skor"]
        )



    return jsonify({

        "soru":soru,

        "mevzuat":
        mevzuat_getir(soru),

        "sonuclar":
        kararlar

    })









HTML="""

<!DOCTYPE html>

<html>

<head>

<title>
Kamu İhale Karar AI
</title>


<style>

body{

font-family:Arial;

margin:40px;

background:#f5f5f5;

}


.kutu{

background:white;

padding:25px;

border-radius:10px;

}


button{

padding:10px;

}


textarea{

width:80%;

height:80px;

}

</style>


</head>


<body>


<div class="kutu">


<h1>
⚖️ Kamu İhale Karar AI
</h1>


<form method="post" action="/webara">


<textarea name="soru"
placeholder="Hukuki sorunuzu yazınız..."></textarea>


<br><br>


<button>
Ara
</button>


</form>



{% if sonuc %}


<hr>


<h2>
Hukuki Değerlendirme
</h2>


{% for k in sonuc %}


<h3>
{{k.konu}}
</h3>


<b>
Karar:
</b>

{{k.karar_no}}

<br><br>


<b>
Hukuki Soru:
</b>

{{k.hukuki_soru}}


<br><br>


<b>
Kurul Değerlendirmesi:
</b>

{{k.kurul_degerlendirmesi}}


<br><br>


<b>
Sonuç:
</b>

{{k.sonuc}}


<br><br>


<b>
Emsal İlke:
</b>

{{k.emsal_ilke}}


<br><br>


<b>
Güven:
</b>

{{k.guven}}


<hr>


{% endfor %}


{% endif %}



</div>


</body>


</html>

"""







@app.route("/")
def index():

    return render_template_string(
        HTML,
        sonuc=None
    )








@app.route("/webara", methods=["POST"])
def webara():


    soru=request.form["soru"]


    sonuc=karar_ara(
        soru
    )



    for k in sonuc:


        k["guven"]=guven(
            k["skor"]
        )



    return render_template_string(

        HTML,

        sonuc=sonuc

    )







if __name__=="__main__":


    print("="*70)

    print(
    "KAMU IHALE KARAR AI - WEB API MOTORU"
    )

    print("="*70)


    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )