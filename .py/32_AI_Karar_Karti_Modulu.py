from flask import Flask, request, render_template_string
import requests


app = Flask(__name__)


API_URL = "http://127.0.0.1:5000/sor"



HTML = """

<!DOCTYPE html>

<html>

<head>

<title>Kamu İhale Karar AI</title>


<style>

body{

font-family:Arial;

background:#f5f5f5;

padding:30px;

}


.container{

max-width:900px;

margin:auto;

background:white;

padding:30px;

border-radius:10px;

}



input{

width:80%;

padding:12px;

font-size:16px;

}


button{

padding:12px 20px;

background:#1d4ed8;

color:white;

border:0;

cursor:pointer;

}



.card{

border:1px solid #ddd;

padding:20px;

margin-top:20px;

border-radius:8px;

background:#fafafa;

}



.baslik{

font-size:20px;

font-weight:bold;

color:#1d4ed8;

}



.etiket{

background:#ddd;

padding:5px;

border-radius:5px;

}



</style>


</head>


<body>


<div class="container">


<h1>
KAMU İHALE KARAR AI
</h1>


<form method="post">


<input 

name="soru"

placeholder="Hukuki sorunuzu yazınız"

value="{{soru}}"

/>


<button>

ARA

</button>


</form>




{% if cevap %}


<h2>

HUKUKİ DEĞERLENDİRME

</h2>


<div class="card">


<p>

{{cevap}}

</p>


</div>





<h2>

DAYANAK KARARLAR

</h2>



{% for k in kararlar %}


<div class="card">


<div class="baslik">

{{k.karar_no}}

</div>


<p>

<b>{{k.baslik}}</b>

</p>


<p>

{{k.ozet}}

</p>



<p>

<strong>Sonuç:</strong>

{{k.sonuc}}

</p>



<span class="etiket">

{{k.kategori}}

</span>



</div>


{% endfor %}





{% endif %}



</div>


</body>


</html>


"""





@app.route("/", methods=["GET","POST"])

def index():


    soru=""

    cevap=""

    kararlar=[]



    if request.method=="POST":


        soru=request.form["soru"]



        r=requests.post(

            API_URL,

            json={

                "soru":soru

            }

        )



        data=r.json()



        sonuclar=data.get("sonuclar",[])



        if sonuclar:


            cevap=(

            "Kamu İhale Kurulu kararları birlikte "
            "değerlendirildiğinde uyuşmazlık; "
            "mevzuata uygunluk, belge yeterliliği "
            "ve teklif açıklamalarının doğruluğu "
            "çerçevesinde incelenmektedir."
            )


            kararlar=sonuclar[:3]



        else:


            cevap="İlgili karar bulunamadı."





    return render_template_string(

        HTML,

        soru=soru,

        cevap=cevap,

        kararlar=kararlar

    )





if __name__=="__main__":


    print("="*70)

    print("KAMU IHALE KARAR AI - KARAR KARTI MODULU")

    print("="*70)



    app.run(

        host="0.0.0.0",

        port=9000,

        debug=True

    )