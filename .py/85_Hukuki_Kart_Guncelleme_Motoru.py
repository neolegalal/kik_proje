# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime


DB = "kik.db"


def tablo_kontrol(cursor):

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hukuki_kartlar (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        karar_no TEXT,

        iddia_no INTEGER,

        baslik TEXT,

        hukuki_soru TEXT,

        iddia_ozeti TEXT,

        kurul_degerlendirmesi TEXT,

        sonuc TEXT,

        emsal_ilke TEXT,

        mevzuat TEXT,

        anahtar_kelime TEXT,

        guven TEXT,

        olusturma_tarihi TEXT

    )
    """)


def temizle(cursor):

    cursor.execute("""
    DELETE FROM hukuki_kartlar
    """)

    print("Eski kartlar temizlendi")


def kart_uret(cursor):


    veriler = cursor.execute("""

        SELECT

        karar_no,
        iddia_no,
        konu,
        uzman_soru,
        iddia_ozeti,
        kurul_degerlendirmesi,
        sonuc,
        emsal_ilke,
        mevzuat,
        anahtar_kelime,
        guven

        FROM karar_iddialari

        WHERE kurul_degerlendirmesi IS NOT NULL
        AND kurul_degerlendirmesi != ''

        ORDER BY karar_no, iddia_no


    """).fetchall()



    sayac = 0


    for v in veriler:


        karar_no = v[0]

        iddia_no = v[1]

        konu = v[2]

        soru = v[3]

        iddia_ozeti = v[4] or ""

        kurul = v[5] or ""

        sonuc = v[6] or ""

        emsal = v[7] or ""

        mevzuat = v[8] or ""

        anahtar = v[9] or konu

        guven = v[10] or "orta"



        cursor.execute("""

        INSERT INTO hukuki_kartlar

        (

        karar_no,

        iddia_no,

        baslik,

        hukuki_soru,

        iddia_ozeti,

        kurul_degerlendirmesi,

        sonuc,

        emsal_ilke,

        mevzuat,

        anahtar_kelime,

        guven,

        olusturma_tarihi

        )

        VALUES

        (?,?,?,?,?,?,?,?,?,?,?,?)

        """,

        (

        karar_no,

        iddia_no,

        konu,

        soru,

        iddia_ozeti,

        kurul,

        sonuc,

        emsal,

        mevzuat,

        anahtar,

        guven,

        datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ))


        sayac += 1


    print("Üretilen kart:", sayac)




def main():


    print("="*70)

    print("KAMU IHALE KARAR AI - HUKUKI KART GUNCELLEME MOTORU")

    print("="*70)



    conn = sqlite3.connect(DB)

    c = conn.cursor()



    tablo_kontrol(c)


    print("Kart tablosu hazır")


    temizle(c)


    kart_uret(c)



    conn.commit()

    conn.close()



    print()

    print("="*70)

    print("HUKUKI KART GUNCELLEME TAMAMLANDI")

    print("="*70)




if __name__ == "__main__":

    main()