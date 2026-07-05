import os
import sqlite3
import re
from datetime import datetime
import fitz   # PyMuPDF


DB = "kik.db"
PDF_KLASORU = "pdfs"


print("="*70)
print("KAMU IHALE KARAR AI - KIK KARAR IMPORT MOTORU")
print("="*70)


conn = sqlite3.connect(DB)
cursor = conn.cursor()


# hata log tablosu
cursor.execute("""
CREATE TABLE IF NOT EXISTS import_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dosya TEXT,
    hata TEXT,
    tarih TEXT
)
""")


def karar_no_bul(text):

    sonuc = re.search(
        r'20\d{2}/[A-ZÇĞİÖŞÜ]+\.[A-ZÇĞİÖŞÜ]+-\d+',
        text
    )

    if sonuc:
        return sonuc.group(0)

    return None



def pdf_oku(path):

    metin = ""

    doc = fitz.open(path)

    for sayfa in doc:
        metin += sayfa.get_text()

    return metin



def zaten_var_mi(karar_no):

    cursor.execute(
        """
        SELECT id 
        FROM kararlar
        WHERE karar_no=?
        """,
        (karar_no,)
    )

    return cursor.fetchone()



def kaydet(
    karar_no,
    dosya,
    metin
):

    cursor.execute("""
    INSERT INTO kararlar
    (
    dosya_adi,
    karar_no,
    tam_metin,
    islenme_tarihi
    )

    VALUES
    (?,?,?,?)

    """,
    (
    dosya,
    karar_no,
    metin,
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))




yeni = 0
hata = 0



for dosya in os.listdir(PDF_KLASORU):

    if not dosya.lower().endswith(".pdf"):
        continue


    print("\n----------------------------------")
    print("Kontrol:", dosya)


    try:


        yol = os.path.join(
            PDF_KLASORU,
            dosya
        )


        metin = pdf_oku(yol)


        karar_no = karar_no_bul(metin)



        if not karar_no:

            print("Karar no bulunamadı")

            continue



        if zaten_var_mi(karar_no):

            print(
                "Zaten mevcut:",
                karar_no
            )

            continue



        kaydet(
            karar_no,
            dosya,
            metin
        )


        conn.commit()


        yeni += 1


        print(
            "✓ Eklendi:",
            karar_no
        )



    except Exception as e:


        hata += 1


        cursor.execute("""
        INSERT INTO import_log
        (dosya,hata,tarih)

        VALUES (?,?,?)

        """,
        (
        dosya,
        str(e),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))


        conn.commit()


        print(
            "HATA:",
            e
        )



print("\n")
print("="*70)
print("IMPORT TAMAMLANDI")
print("Yeni eklenen karar:", yeni)
print("Hatalı:", hata)
print("="*70)



conn.close()