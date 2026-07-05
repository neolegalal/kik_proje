# -*- coding: utf-8 -*-
"""
112_Karar_AI_Arama_Motoru_v3_Esik_Filtreli.py

Amaç:
- Hukuki kartlar içinde daha temiz emsal arama yapar.
- Düşük skorlu/alakasız sonuçları filtreler.
- Tekrarlı sonuçları azaltır.
- En iyi ve en alakalı emsalleri gösterir.
"""

import sqlite3
import re
from difflib import SequenceMatcher
from collections import Counter

DB_PATH = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"

MIN_SKOR = 50
LIMIT = 5


def temizle(metin):
    if metin is None:
        return ""
    metin = str(metin).lower()
    metin = metin.replace("ı", "i")
    metin = metin.replace("ğ", "g")
    metin = metin.replace("ü", "u")
    metin = metin.replace("ş", "s")
    metin = metin.replace("ö", "o")
    metin = metin.replace("ç", "c")
    metin = re.sub(r"\s+", " ", metin)
    return metin.strip()


def kelimeler(metin):
    return [k for k in re.findall(r"[a-zA-Z0-9]+", temizle(metin)) if len(k) > 2]


def benzerlik(a, b):
    return SequenceMatcher(None, temizle(a), temizle(b)).ratio()


def sonuc_tipi_bul(sonuc):
    s = temizle(sonuc)

    if "iptal" in s:
        return "İPTAL"
    if "kabul" in s or "yerinde bulunmus" in s:
        return "KABUL"
    if "ret" in s or "reddedil" in s or "yerinde bulunmamis" in s:
        return "RET"

    return "BELİRSİZ"


def kartlari_getir():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    rows = cur.execute("""
        SELECT
            id,
            karar_no,
            iddia_no,
            baslik,
            hukuki_soru,
            sonuc,
            emsal_ilke,
            anahtar_kelime,
            kurul_degerlendirmesi
        FROM hukuki_kartlar
        ORDER BY karar_no, iddia_no
    """).fetchall()

    con.close()
    return rows


def skor_hesapla(sorgu, kart):
    skor = 0

    sorgu_norm = temizle(sorgu)
    sorgu_kelimeleri = kelimeler(sorgu)

    baslik = temizle(kart["baslik"])
    soru = temizle(kart["hukuki_soru"])
    sonuc = temizle(kart["sonuc"])
    ilke = temizle(kart["emsal_ilke"])
    anahtar = temizle(kart["anahtar_kelime"])
    degerlendirme = temizle(kart["kurul_degerlendirmesi"])

    if sorgu_norm and sorgu_norm == anahtar:
        skor += 100

    if sorgu_norm and sorgu_norm == baslik:
        skor += 90

    if sorgu_norm and sorgu_norm in anahtar:
        skor += 70

    if sorgu_norm and sorgu_norm in baslik:
        skor += 60

    if sorgu_norm and sorgu_norm in soru:
        skor += 45

    if sorgu_norm and sorgu_norm in ilke:
        skor += 35

    for k in sorgu_kelimeleri:
        if k in anahtar:
            skor += 12
        if k in baslik:
            skor += 10
        if k in soru:
            skor += 8
        if k in ilke:
            skor += 5
        if k in sonuc:
            skor += 3
        if k in degerlendirme:
            skor += 2

    return skor


def tekrar_filtrele(sonuclar, limit=LIMIT):
    secilen = []

    for skor, kart in sonuclar:
        tekrar = False

        for _, onceki in secilen:
            if benzerlik(kart["baslik"], onceki["baslik"]) >= 0.90:
                tekrar = True
                break

            if benzerlik(kart["emsal_ilke"], onceki["emsal_ilke"]) >= 0.90:
                tekrar = True
                break

        if not tekrar:
            secilen.append((skor, kart))

        if len(secilen) >= limit:
            break

    return secilen


def ara(sorgu):
    kartlar = kartlari_getir()
    sonuclar = []

    for kart in kartlar:
        skor = skor_hesapla(sorgu, kart)

        if skor >= MIN_SKOR:
            sonuclar.append((skor, kart))

    sonuclar.sort(
        key=lambda x: (
            x[0],
            len(str(x[1]["emsal_ilke"] or "")),
            len(str(x[1]["kurul_degerlendirmesi"] or "")),
        ),
        reverse=True,
    )

    return tekrar_filtrele(sonuclar)


def kalite_ozeti():
    kartlar = kartlari_getir()

    basliklar = Counter(temizle(k["baslik"]) for k in kartlar)
    ilkeler = Counter(temizle(k["emsal_ilke"]) for k in kartlar)
    sonuc_tipleri = Counter(sonuc_tipi_bul(k["sonuc"]) for k in kartlar)

    print("\nKART HAVUZU")
    print("-" * 80)
    print(f"Toplam kart          : {len(kartlar)}")
    print(f"Benzersiz başlık     : {len(basliklar)}")
    print(f"Benzersiz emsal ilke : {len(ilkeler)}")

    print("\nSonuç tipi dağılımı:")
    for tip, adet in sonuc_tipleri.most_common():
        print(f"{adet:>4}  {tip}")


def yazdir(sonuclar):
    print("\n" + "=" * 80)
    print("EŞİK FİLTRELİ EMSAL SONUÇLARI")
    print("=" * 80)

    if not sonuclar:
        print("Sonuç bulunamadı veya skor eşiğinin altında kaldı.")
        return

    for i, (skor, kart) in enumerate(sonuclar, start=1):
        print(f"\n[{i}] Skor: {skor} | Sonuç Tipi: {sonuc_tipi_bul(kart['sonuc'])}")
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


def main():
    print("=" * 80)
    print("112 - KİK KARAR AI ARAMA MOTORU V3 / EŞİK FİLTRELİ")
    print("=" * 80)

    kalite_ozeti()

    while True:
        sorgu = input("\nSoru / Anahtar Kelime (çıkış=q): ").strip()

        if sorgu.lower() in ["q", "quit", "exit", "çıkış"]:
            break

        sonuclar = ara(sorgu)
        yazdir(sonuclar)

    print("\nProgram sonlandırıldı.")


if __name__ == "__main__":
    main()