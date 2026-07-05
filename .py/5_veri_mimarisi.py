# -*- coding: utf-8 -*-

"""
ADIM 5
KİK Karar Sistemi Veri Mimarisi

Amaç:
- Bir karar içinde birden fazla hukuki mesele saklamak
- Web sitesi araması için hazır yapı oluşturmak
- İstatistik altyapısı kurmak
"""


import sqlite3


DB = "./kik.db"


def main():

    db = sqlite3.connect(DB)

    cursor = db.cursor()


    # 1) Karar içindeki ayrı hukuki konular
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS karar_konulari (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        karar_id INTEGER,

        soru_basligi TEXT,

        karar_ozeti TEXT,

        karar_sonucu TEXT,

        ana_kategori TEXT,

        alt_kategori TEXT,

        anahtar_kelimeler TEXT,


        FOREIGN KEY (karar_id)
        REFERENCES kararlar(id)

    )
    """)



    # 2) İstatistik altyapısı

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS istatistik (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        kategori TEXT,

        alt_kategori TEXT,

        sonuc TEXT,

        adet INTEGER DEFAULT 0

    )
    """)




    # 3) Arama için etiket tablosu

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS arama_etiketleri (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        konu_id INTEGER,

        etiket TEXT,

        FOREIGN KEY(konu_id)
        REFERENCES karar_konulari(id)

    )
    """)



    db.commit()


    print("================================")
    print("VERİ MİMARİSİ OLUŞTURULDU")
    print("================================")


    tablolar = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()


    print("Tablolar:")

    for t in tablolar:
        print("-", t[0])


    db.close()



if __name__ == "__main__":
    main()