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

font-family: Arial;
margin:40px;
background:#f5f5f5;

}


.container{

background:white;
padding:30px;
border-radius:10px;
max-width:900px;
margin:auto;

}


textarea{

width:100%;
height:100px;
font-size:16px;

}


button{

padding:12px 30px;
font-size:16px;
cursor:pointer;

}


.karar{

border:1px solid #ddd;
padding:15px;
margin-top:15px;
border-radius:8px;

}



</style>


</head>



<body>


<div class="container">


<h1>
KAMU İHALE KARAR AI
</h1>



<form method="post">


<textarea name="soru"
placeholder="Hukuki sorunuzu yazınız...">{{soru}}</textarea>


<br><br>


<button>

ARA

</button>


</form>





{% if cevap %}



<h2>

HUKUKİ DEĞERLENDİRME

</h2>



<p>

{{cevap}}

</p>




<h2>

DAYANAK KARARLAR

</h2>



{% for k in kararlar %}


<div class="karar">


<b>
{{k.karar_no}}
</b>


<br>


{{k.baslik}}


<br><br>


{{k.sonuc}}


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



        kararlar=data.get(

            "sonuclar",

            []

        )





        if kararlar:



            cevap="""

Kamu İhale Kurulu kararları birlikte değerlendirildiğinde;

uyuşmazlıkların teklif açıklamalarının mevzuata uygunluğu,
sunulan belgelerin yeterliliği ve maliyet unsurlarının
açıklanabilirliği yönlerinden incelendiği görülmektedir.

Benzer olaylarda açıklamaların yeterli belge ile
desteklenmemesi veya mevzuata uygun olmaması halinde
teklifin değerlendirme dışı bırakılması sonucu
ortaya çıkabilmektedir.

"""



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

    print("KAMU IHALE KARAR AI WEB ARAYUZ")

    print("="*70)



    app.run(

        host="0.0.0.0",

        port=8000,

        debug=True

    )