import sqlite3
import os
import re
from datetime import datetime
import fitz   # pymupdf



DB = "kik.db"

PDF_KLASOR = "pdfs"



print("="*70)
print("KAMU IHALE KARAR AI - TOPLU PDF ISLEME MOTORU")
print("="*70)





conn = sqlite3.connect(DB)

cursor = conn.cursor()





# =====================================================
# PDF METIN OKUMA
# =====================================================


def pdf_oku(dosya):


    metin = ""


    doc = fitz.open(dosya)


    for sayfa in doc:

        metin += sayfa.get_text()



    return metin







# =====================================================
# KARAR NO BUL
# =====================================================



def karar_no_bul(text, dosya):


    sonuc = re.search(

        r'20\d{2}/[A-ZÇĞİÖŞÜ\.]+[0-9\-]+',

        text

    )


    if sonuc:

        return sonuc.group()



    isim = os.path.basename(dosya)



    sonuc = re.search(

        r'20\d{2}-[A-Z\.]+-[0-9]+',

        isim

    )



    if sonuc:

        return sonuc.group()



    return None







# =====================================================
# PDFLER
# =====================================================



dosyalar = os.listdir(PDF_KLASOR)



pdfler = [

x for x in dosyalar

if x.lower().endswith(".pdf")

]





print()

print("PDF SAYISI:")

print(len(pdfler))





yeni = 0





for pdf in pdfler:



    yol = os.path.join(

        PDF_KLASOR,

        pdf

    )



    print()

    print("-"*60)

    print("Kontrol:")

    print(pdf)




    try:


        metin = pdf_oku(yol)



        karar_no = karar_no_bul(

            metin,

            pdf

        )



        if not karar_no:



            print("Karar no bulunamadı")

            continue





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

            continue





        cursor.execute(

        """

        INSERT INTO kararlar

        (

        dosya_adi,

        karar_no,

        tam_metin,

        islenme_tarihi

        )

        VALUES (?,?,?,?)

        """,

        (

        pdf,

        karar_no,

        metin,

        datetime.now().isoformat()

        )

        )



        conn.commit()



        yeni += 1



        print("✓ EKLENDİ:")

        print(karar_no)





    except Exception as e:


        print("HATA:")

        print(e)







print()

print("="*70)

print("PDF ISLEME TAMAMLANDI")

print()

print("Yeni eklenen karar:")

print(yeni)

print("="*70)



conn.close()