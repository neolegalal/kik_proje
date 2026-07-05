import sqlite3
from flask import Flask, request, render_template_string


DB="kik.db"


app=Flask(__name__)





KONU_AGACI={


"yasak_fiiller":[

"aynı kişinin iki şirket",
"iki şirket",
"birden fazla teklif",
"birden fazla teklif verme",
"aynı şahıs",
"17/d",
"yasak fiil"

],



"asiri_dusuk":[

"aşırı düşük",
"aciklama",
"maliyet",
"teklif açıklaması"

],



"teminat":[

"geçici teminat",
"kesin teminat",
"teminat mektubu"

],



"is_deneyimi":[

"iş deneyim",
"belge",
"benzer iş"

],



"teknik_sartname":[

"teknik şartname",
"marka",
"model",
"özellik"

]


}






MEVZUAT={


"yasak_fiiller":{

"kanun":
"4734 sayılı Kamu İhale Kanunu",

"madde":
"17/d",

"konu":
"Birden fazla teklif verme yasağı"

},


"teminat":{

"kanun":
"4734 sayılı Kamu İhale Kanunu",

"madde":
"35-43",

"konu":
"Teminat hükümleri"

}



}










def konu_bul(soru):


    soru=soru.lower()


    for konu,kelimeler in KONU_AGACI.items():


        for kelime in kelimeler:


            if kelime in soru:

                return konu



    return None










def karar_getir(soru):


    konu=konu_bul(soru)


    conn=sqlite3.connect(DB)

    c=conn.cursor()



    kararlar=c.execute("""

    SELECT

    karar_no,

    baslik,

    hukuki_soru,

    kurul_degerlendirmesi,

    sonuc,

    emsal_ilke,

    mevzuat


    FROM hukuki_kartlar


    """).fetchall()



    conn.close()



    sonuc=[]



    for k in kararlar:



        skor=0



        metin=" ".join(

        [

        str(k[1]),

        str(k[2]),

        str(k[5])

        ]

        ).lower()



        if konu=="yasak_fiiller":


            if "birden fazla teklif" in metin:

                skor+=20



        elif konu=="teknik_sartname":


            if "teknik şartname" in metin:

                skor+=20



        elif konu=="teminat":


            if "teminat" in metin:

                skor+=20




        else:



            for kelime in soru.lower().split():


                if kelime in metin:

                    skor+=1




        if skor>0:



            sonuc.append({

            "karar_no":k[0],

            "konu":k[1],

            "soru":k[2],

            "degerlendirme":k[3],

            "sonuc":k[4],

            "emsal":k[5],

            "mevzuat":k[6],

            "skor":skor


            })




    sonuc.sort(

    key=lambda x:x["skor"],

    reverse=True

    )



    return sonuc[:3],konu











HTML="""

<!DOCTYPE html>

<html>

<head>

<title>Kamu İhale Karar AI</title>


<style>


body{

font-family:Arial;

background:#f1f3f6;

margin:40px;

}



.kutu{

background:white;

padding:30px;

border-radius:15px;

}



.kart{

padding:20px;

margin-top:20px;

background:#fafafa;

border:1px solid #ddd;

border-radius:10px;

}



button{

padding:12px;

background:#111;

color:white;

}



input{

width:70%;

padding:12px;

}


</style>


</head>


<body>


<div class="kutu">


<h1>
⚖️ Kamu İhale Karar AI
</h1>


<form method="post">


<input name="soru"

placeholder="Hukuki sorunuzu yazınız">


<button>
Ara
</button>


</form>




{% if konu %}


<h3>
Tespit Edilen Hukuki Alan:
{{konu}}

</h3>


{% endif %}




{% for k in sonuc %}


<div class="kart">


<h2>

{{k.konu}}

</h2>


<b>
Karar:
</b>

{{k.karar_no}}


<br><br>


<b>
Hukuki Soru:
</b>

<br>

{{k.soru}}


<br><br>


<b>
Kurul Yaklaşımı:
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
Emsal İlke:
</b>

<br>

{{k.emsal}}


<br><br>


<b>
Skor:
</b>

{{k.skor}}



</div>


{% endfor %}



</div>


</body>


</html>

"""









@app.route("/",methods=["GET","POST"])

def index():


    sonuc=[]

    konu=None



    if request.method=="POST":


        soru=request.form["soru"]


        sonuc,konu=karar_getir(soru)



    return render_template_string(

    HTML,

    sonuc=sonuc,

    konu=konu

    )










if __name__=="__main__":


    print("="*70)

    print(
    "KAMU IHALE KARAR AI - KONU AGACI MOTORU"
    )

    print("="*70)


    app.run(

    host="127.0.0.1",

    port=5000,

    debug=True

    )