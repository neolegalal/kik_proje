from flask import Flask, request, render_template_string
import requests


app = Flask(__name__)



HTML = """

<!DOCTYPE html>

<html>

<head>

<meta charset="utf-8">

<title>
Kamu İhale Karar AI
</title>


<style>


body{

font-family: Arial, sans-serif;

background:#f4f6f8;

padding:40px;

}


.container{

max-width:900px;

margin:auto;

background:white;

padding:30px;

border-radius:12px;

box-shadow:0 0 15px #ccc;

}



h1{

text-align:center;

color:#1d3557;

}



input{

width:80%;

padding:15px;

font-size:16px;

}



button{

padding:15px 25px;

background:#1d3557;

color:white;

border:none;

cursor:pointer;

}



.card{

margin-top:25px;

padding:20px;

border-left:6px solid #1d3557;

background:#fafafa;

}



.baslik{

font-size:22px;

font-weight:bold;

color:#1d3557;

}



etiket{

font-weight:bold;

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

required>


<button>

Ara

</button>


</form>





{% if sonuc %}


{% for kart in sonuc %}



<div class="card">


<div class="baslik">

{{kart.konu}}

</div>



<p>

<b>Karar:</b>

{{kart.karar_no}}

</p>



<p>

<b>Hukuki Soru:</b>

{{kart.hukuki_soru}}

</p>




<p>

<b>Kurul Değerlendirmesi:</b>

<br>

{{kart.kurul_degerlendirmesi}}

</p>



<p>

<b>Sonuç:</b>

<br>

{{kart.sonuc}}

</p>



<p>

<b>Emsal İlke:</b>

<br>

{{kart.emsal_ilke}}

</p>



<p>

<b>Güven:</b>

{{kart.guven}}

</p>



</div>



{% endfor %}



{% endif %}




</div>


</body>


</html>


"""





@app.route("/",methods=["GET","POST"])

def index():


    sonuc=[]


    if request.method=="POST":


        soru=request.form["soru"]



        try:


            cevap=requests.post(

                "http://127.0.0.1:5000/ara",

                json={

                    "soru":soru

                }

            ).json()



            sonuc=cevap.get(

                "sonuclar",

                []

            )



        except Exception as e:


            sonuc=[

                {

                "konu":"Hata",

                "kurul_degerlendirmesi":
                str(e),

                "karar_no":"",
                "hukuki_soru":"",
                "sonuc":"",
                "emsal_ilke":"",
                "guven":""

                }

            ]





    return render_template_string(

        HTML,

        sonuc=sonuc

    )






if __name__=="__main__":


    print("="*70)

    print(
    "KAMU IHALE KARAR AI - WEB ARAYUZ"
    )

    print("="*70)



    app.run(

        host="0.0.0.0",

        port=8000,

        debug=True

    )