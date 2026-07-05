import os
import sqlite3
import fitz
import re
from datetime import datetime


DB = "kik.db"


PDF_KLASORU = "pdfler"


print("="*70)
print("KAMU IHALE KARAR AI - 100 BIN GERCEK VERI YUKLEME MOTORU")
print("="*70)



conn = sqlite3.connect(DB)

cursor = conn.cursor()



# -------------------------------------------------
# PDF KLASORU
# -------------------------------------------------

if not os.path.exists(PDF_KLASORU):

    os.makedirs(PDF_KLASORU)

    print("pdfler klasoru olusturuldu")




pdfler = [

x for x in os.listdir(PDF_KLASORU)

if x.lower().endswith(".pdf")

]



print()

print("PDF SAYISI:")

print(len(pdfler))




eklenen = 0

atlanan = 0





for pdf in pdfler:


    yol = os.path.join(PDF_KLASORU,pdf)



    print()

    print("-"*60)

    print("Isleniyor:")

    print(pdf)



    # karar no yakala


    bulunan = re.search(

    r'(\d{4})[_-](UY|UH|D|A|UY\.II|UH\.II)[._-]*(\d+)',

    pdf.upper()

    )



    karar_no = None



    if bulunan:


        yil = bulunan.group(1)

        seri = bulunan.group(2)

        no = bulunan.group(3)


        karar_no = yil + "/" + seri + "." + no



    else:


        karar_no = pdf.replace(".pdf","")




    # kontrol


    cursor.execute(

    """

    SELECT id

    FROM kararlar

    WHERE karar_no=?

    """,

    (karar_no,)

    )


    mevcut = cursor.fetchone()



    if mevcut:


        print("Zaten mevcut:")

        print(karar_no)

        atlanan += 1

        continue





    # PDF OKU


    doc = fitz.open(yol)


    metin = ""


    for sayfa in doc:


        metin += sayfa.get_text()




    doc.close()




    # kayıt


    cursor.execute(

    """

    INSERT INTO kararlar

    (

    karar_no,

    tam_metin,

    dosya_adi,

    islenme_tarihi

    )

    VALUES (?,?,?,?)

    """,

    (

    karar_no,

    metin,

    pdf,

    datetime.now().strftime("%Y-%m-%d")

    )

    )





    eklenen += 1



    print("Eklendi:")

    print(karar_no)







conn.commit()

conn.close()




print()

print("="*70)

print("GERCEK VERI YUKLEME TAMAMLANDI")

print()

print("Yeni eklenen:")

print(eklenen)


print()

print("Atlanan:")

print(atlanan)


print("="*70)