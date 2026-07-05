from flask import Flask, request, render_template
import json


app = Flask(__name__)


with open(
    "kararlar.json",
    "r",
    encoding="utf-8"
) as f:

    kararlar=json.load(f)



print("="*70)
print("KAMU IHALE KARAR AI - WEB SISTEMI")
print("="*70)



def ara(soru):

    soru=soru.lower()


    sonuc=[]


    kelimeler=soru.split()


    for karar in kararlar:


        metin=""


        metin+=str(karar.get("soru_basligi",""))
        metin+=str(karar.get("kisa_ozet",""))
        metin+=str(karar.get("anahtar_kelimeler",""))


        metin=metin.lower()


        puan=0


        for kelime in kelimeler:

            if kelime in metin:

                puan+=1



        if puan>0:

            sonuc.append(
                (
                puan,
                karar
                )
            )



    sonuc.sort(
        key=lambda x:x[0],
        reverse=True
    )


    return sonuc[:5]





@app.route("/",methods=["GET","POST"])

def index():


    cevap=[]

    soru=""


    if request.method=="POST":


        soru=request.form["soru"]


        cevap=ara(soru)



    return render_template(
        "index.html",
        cevap=cevap,
        soru=soru
    )





app.run(
host="127.0.0.1",
port=5000,
debug=True
)