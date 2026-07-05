import sqlite3
from datetime import datetime


from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4


from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont



DB = "kik.db"



# =====================================================
# FONT
# =====================================================

pdfmetrics.registerFont(
    TTFont(
        "DejaVu",
        "DejaVuSans.ttf"
    )
)


pdfmetrics.registerFont(
    TTFont(
        "DejaVu-Bold",
        "DejaVuSans-Bold.ttf"
    )
)



print("="*70)
print("⚖️ KAMU İHALE KARAR AI")
print("KİK KARAR FORMAT ÜRETİM MOTORU v2")
print("="*70)




# =====================================================
# KARAR ARAMA
# =====================================================


def karar_bul(soru):


    con = sqlite3.connect(DB)

    cur = con.cursor()



    cur.execute("""

    SELECT

    karar_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke,
    mevzuat


    FROM hukuki_kartlar


    """)



    veriler = cur.fetchall()


    con.close()



    soru=soru.lower()



    eniyi=None

    skor=0



    for v in veriler:


        metin=" ".join([

            str(v[1]),

            str(v[2]),

            str(v[5])

        ]).lower()



        ortak=set(
            soru.split()
        ).intersection(
            set(metin.split())
        )



        if len(ortak)>skor:


            skor=len(ortak)

            eniyi=v



    return eniyi






# =====================================================
# SAYFA NUMARASI
# =====================================================


def sayfa_no(canvas,doc):


    canvas.saveState()


    canvas.setFont(
        "DejaVu",
        9
    )


    canvas.drawRightString(

        550,

        20,

        f"Sayfa {doc.page}"

    )


    canvas.restoreState()







# =====================================================
# PDF ÜRET
# =====================================================


def pdf_uret(veri,soru):


    tarih=datetime.now().strftime(
        "%d.%m.%Y"
    )



    dosya="KIK_Karar_AI_2026_001.pdf"


    txt="KIK_Karar_AI_2026_001.txt"





    doc=SimpleDocTemplate(

        dosya,

        pagesize=A4,

        leftMargin=65,

        rightMargin=65,

        topMargin=60,

        bottomMargin=60

    )





    styles=getSampleStyleSheet()



    normal=ParagraphStyle(

        "normal",

        parent=styles["Normal"],

        fontName="DejaVu",

        fontSize=11,

        leading=18

    )



    baslik=ParagraphStyle(

        "baslik",

        parent=normal,

        fontName="DejaVu-Bold",

        fontSize=15,

        alignment=1,

        spaceAfter=15

    )



    alt=ParagraphStyle(

        "alt",

        parent=normal,

        fontName="DejaVu-Bold",

        fontSize=12,

        spaceBefore=12

    )





    rapor=f"""


KAMU İHALE HUKUKU
UZMAN DEĞERLENDİRME RAPORU



Rapor No:
AI-2026/001


Rapor Tarihi:
{tarih}





BAŞVURU SAHİBİ:

.....................................





İHALEYİ YAPAN İDARE:

.....................................





BAŞVURUYA KONU İHALE:

.....................................





UYUŞMAZLIK KONUSU:


{soru}






KURUM TARAFINDAN YAPILAN İNCELEME:


Başvuru konusu olay;

ilgili mevzuat hükümleri,
Kamu İhale Kurulu kararları ve
emsal uygulamalar birlikte değerlendirilerek incelenmiştir.






KARAR:



Esas inceleme kapsamında yapılan değerlendirmede;

başvuru sahibinin iddiaları aşağıdaki şekilde incelenmiştir.





İLGİLİ MEVZUAT:



{veri[6]}






KURUL DEĞERLENDİRMESİ:



{veri[3]}






EMSAL KARAR:



Karar No:

{veri[0]}






EMSAL İLKE:



{veri[5]}






UZMAN DEĞERLENDİRMESİ:



Kamu İhale mevzuatı ve Kurul kararları birlikte değerlendirildiğinde;


Uyuşmazlık konusu olayda;


- ihale sürecindeki işlem,

- isteklilerin hukuki durumu,

- teklif değerlendirme süreci,

- mevzuat hükümleri


birlikte değerlendirilmelidir.


Somut olay bakımından yapılan incelemede,
ilgili Kurul yaklaşımı doğrultusunda değerlendirme yapılması gerektiği kanaatine varılmıştır.






SONUÇ VE KANAAT:



{veri[4]}





Açıklanan nedenlerle;

ilgili mevzuat hükümleri ve emsal kararlar çerçevesinde
yukarıdaki değerlendirme sonucuna ulaşılmıştır.






DÜZENLEYEN:



Kamu İhale Hukuku Uzmanı


İnşaat Yüksek Mühendisi


Kamil ÇAKMAK



"""





    story=[]



    for satir in rapor.split("\n"):


        if satir.strip() in [

            "KAMU İHALE HUKUKU",

            "UZMAN DEĞERLENDİRME RAPORU",

            "KARAR:"

        ]:


            stil=baslik


        elif satir.strip().endswith(":"):


            stil=alt


        else:


            stil=normal




        story.append(

            Paragraph(

                satir.replace(
                    "\n",
                    "<br/>"
                ),

                stil

            )

        )


        story.append(
            Spacer(1,8)
        )





    doc.build(

        story,

        onFirstPage=sayfa_no,

        onLaterPages=sayfa_no

    )





    with open(

        txt,

        "w",

        encoding="utf-8"

    ) as f:


        f.write(rapor)



    return dosya,txt







# =====================================================
# ANA PROGRAM
# =====================================================


while True:


    soru=input(

        "\nUyuşmazlık konusu (q çıkış): "

    )



    if soru=="q":

        break




    karar=karar_bul(soru)



    if not karar:


        print("Karar bulunamadı")

        continue




    pdf,txt=pdf_uret(

        karar,

        soru

    )



    print()

    print("="*70)

    print("KİK FORMAT RAPOR OLUŞTURULDU")

    print("="*70)


    print()

    print(pdf)

    print(txt)