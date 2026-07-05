# -*- coding: utf-8 -*-

import sqlite3
from collections import Counter

DB_PATH = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"


def normalize(text):
    if text is None:
        return ""
    return str(text).lower().strip()


def skor_hesapla(aranan, kart):

    skor = 0

    baslik = normalize(kart["baslik"])
    soru = normalize(kart["hukuki_soru"])
    ilke = normalize(kart["emsal_ilke"])
    anahtar = normalize(kart["anahtar_kelime"])

    kelimeler = [k for k in normalize(aranan).split() if len(k) > 2]

    for kelime in kelimeler:

        if kelime in baslik:
            skor += 5

        if kelime in soru:
            skor += 4

        if kelime in ilke:
            skor += 3

        if kelime in anahtar:
            skor += 6

    return skor


def kartlari_getir():

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row

    cur = con.cursor()

    rows = cur.execute("""
        SELECT
            karar_no,
            iddia_no,
            baslik,
            hukuki_soru,
            sonuc,
            emsal_ilke,
            anahtar_kelime
        FROM hukuki_kartlar
    """).fetchall()

    con.close()

    return rows


def ara(soru):

    kartlar = kartlari_getir()

    sonuclar = []

    for kart in kartlar:

        skor = skor_hesapla(soru, kart)

        if skor > 0:
            sonuclar.append((skor, kart))

    sonuclar.sort(key=lambda x: x[0], reverse=True)

    return sonuclar[:10]


def yazdir(sonuclar):

    print("\n" + "=" * 80)
    print("EMSAL ARAMA SONUÇLARI")
    print("=" * 80)

    if not sonuclar:
        print("\nSonuç bulunamadı.")
        return

    for sira, (skor, kart) in enumerate(sonuclar, start=1):

        print(f"\n[{sira}] Skor: {skor}")
        print("-" * 80)

        print("Karar No :", kart["karar_no"])
        print("İddia No :", kart["iddia_no"])

        print("\nBaşlık:")
        print(kart["baslik"])

        print("\nHukuki Soru:")
        print(kart["hukuki_soru"])

        print("\nSonuç:")
        print(kart["sonuc"])

        print("\nEmsal İlke:")
        print(kart["emsal_ilke"])

        print("\nAnahtar Kelime:")
        print(kart["anahtar_kelime"])


def istatistik():

    kartlar = kartlari_getir()

    print("\nToplam kart:", len(kartlar))

    kelimeler = []

    for k in kartlar:

        if k["anahtar_kelime"]:

            for x in str(k["anahtar_kelime"]).split(","):
                x = x.strip()

                if x:
                    kelimeler.append(x)

    print("\nEn sık geçen etiketler:\n")

    for etiket, adet in Counter(kelimeler).most_common(20):
        print(f"{adet:>4}  {etiket}")


def main():

    print("=" * 80)
    print("110 - KİK KARAR AI ARAMA VE EMSAL SORGU MOTORU")
    print("=" * 80)

    istatistik()

    while True:

        soru = input("\nSoru / Anahtar Kelime (çıkış=q): ").strip()

        if soru.lower() in ["q", "quit", "exit"]:
            break

        sonuclar = ara(soru)

        yazdir(sonuclar)

    print("\nProgram sonlandırıldı.")


if __name__ == "__main__":
    main()