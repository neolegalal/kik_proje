import sqlite3
from flask import Flask, request, render_template_string


DB = "kik.db"


app = Flask(__name__)





def baglan():

    return sqlite3.connect(DB)







def arama_yap(soru, kategori=""):


    conn = baglan()

    cursor = conn.cursor()



    query = """

    SELECT

    id,
    karar_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke,
    mevzuat,
    guven


    FROM hukuki_kartlar

    """



    veriler = cursor.execute(query).fetchall()


    conn.close()



    sonuc=[]



    kelimeler = soru.lower().split()



    for k in veriler:


        skor=0


        metin=" ".join(

        [

        str(k[2]),
        str(k[3]),
        str(k[4]),
        str(k[6]),
        str(k[7])

        ]

        ).lower()



        for kelime in kelimeler:


            if len(kelime)>2 and kelime in metin:

                skor += 1




        # kritik hukuki eşleşmeler


        if (
            ("iki şirket" in soru.lower()
            or
            "iki sirket" in soru.lower()
            or
            "aynı kişinin" in soru.lower()
            or
            "ayni kisinin" in soru.lower())

            and

            "birden fazla teklif" in metin
        ):


            skor += 10




        if skor>0:


            sonuc.append({

                "id":k[0],

                "karar_no":k[1],

                "konu":k[2],

                "soru":k[3],

                "degerlendirme":k[4],

                "sonuc":k[5],

                "emsal":k[6],

                "mevzuat":k[7],

                "guven":k[8],

                "skor":skor

            })



    sonuc.sort(

        key=lambda x:x["skor"],

        reverse=True

    )


    return sonuc











def detay_getir(id):


    conn=baglan()

    c=conn.cursor()


    veri=c.execute("""

    SELECT

    karar_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke,
    mevzuat


    FROM hukuki_kartlar

    WHERE id=?


    """,(id,)).fetchone()



    conn.close()


    return veri










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

background:#eef1f5;

margin:40px;

}


.container{

background:white;

padding:30px;

border-radius:15px;

}


input,select{

padding:12px;

width:70%;

}


button{

padding:12px 25px;

background:#222;

color:white;

border:0;

}



.kart{

margin-top:25px;

padding:20px;

border-radius:12px;

background:#fafafa;

border:1px solid #ddd;

}



.baslik{

font-size:22px;

font-weight:bold;

}


.guven{

color:green;

font-weight:bold;

}



a{

text-decoration:none;

}


</style>


</head>


<body>



<div class="container">


<h1>
⚖️ Kamu İhale Karar AI
</h1>


<form method="post">


<input

name="soru"

placeholder="Hukuki sorunuzu yazınız..."

>


<select name="kategori">


<option>
Tümü
</option>


<option>
Yasak fiiller
</option>


<option>
Teminat
</option>


<option>
Yeterlik
</option>


<option>
İş deneyimi
</option>


</select>



<button>
Ara
</button>


</form>




{% for k in sonuc %}


<div class="kart">


<div class="baslik">

{{k.konu}}

</div>


<br>


<b>
Karar:
</b>

{{k.karar_no}}


<br><br>


<b>
Hukuki soru:
</b>

<br>

{{k.soru}}


<br><br>



<b>
Kurul değerlendirmesi:
</b>

<br>

{{k.degerlendirme}}


<br><br>


<b>
Sonuç:
</b>

<br>

{{k.sonuc}}


<br><br>


<b>
Emsal ilke:
</b>

<br>

{{k.emsal}}


<br><br>



<b>
Mevzuat:
</b>

{{k.mevzuat}}


<br><br>


<span class="guven">

Güven:

{{k.guven}}

</span>


<br><br>


<a href="/karar/{{k.id}}">
Detay Gör →
</a>



</div>



{% endfor %}




</div>


</body>

</html>

"""









DETAY="""

<h1>
⚖️ Karar Detayı
</h1>


<h2>
{{veri[1]}}
</h2>


<b>
Karar:
</b>

{{veri[0]}}


<hr>


<b>
Hukuki Soru
</b>

<p>

{{veri[2]}}

</p>



<b>
Kurul Değerlendirmesi
</b>


<p>

{{veri[3]}}

</p>



<b>
Sonuç
</b>


<p>

{{veri[4]}}

</p>



<b>
Emsal İlke
</b>


<p>

{{veri[5]}}

</p>



<b>
Mevzuat
</b>


<p>

{{veri[6]}}

</p>

"""









@app.route("/",methods=["GET","POST"])

def index():


    sonuc=[]


    if request.method=="POST":


        soru=request.form["soru"]


        sonuc=arama_yap(soru)



    return render_template_string(

        HTML,

        sonuc=sonuc

    )









@app.route("/karar/<int:id>")

def karar(id):


    veri=detay_getir(id)



    return render_template_string(

        DETAY,

        veri=veri

    )








if __name__=="__main__":


    print("="*70)

    print(
    "KAMU IHALE KARAR AI - PROFESYONEL WEB ARAYUZ"
    )

    print("="*70)



    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )