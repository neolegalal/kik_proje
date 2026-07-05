# -*- coding: utf-8 -*-

import sqlite3
import re
from collections import Counter, defaultdict
from difflib import SequenceMatcher

DB_PATH = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"


def temizle(metin):
    if metin is None:
        return ""
    metin = str(metin).lower()
    metin = re.sub(r"\s+", " ", metin)
    return metin.strip()


def kelimeler(metin):
    metin = temizle(metin)
    return [k for k in re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]+", metin) if len(k) > 2]


def benzerlik(a, b):
    return SequenceMatcher(None, temizle(a), temizle(b)).ratio()


def sonuc_tipi_bul(sonuc):
    s = temizle(sonuc)

    if "iptal" in s:
        return "İPTAL"
    if "kabul" in s or "yerinde bulunmuş" in s:
        return "KABUL"
    if "ret" in s or "reddedil" in s or "yerinde bulunmamış" in s:
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
    sorgu_kelimeleri = kelimeler(sorgu)

    baslik = temizle(kart["baslik"])
    soru = temizle(kart["hukuki_soru"])
    sonuc = temizle(kart["sonuc"])
    ilke = temizle(kart["emsal_ilke"])
    anahtar = temizle(kart["anahtar_kelime"])
    degerlendirme = temizle(kart["kurul_degerlendirmesi"])

    for k in sorgu_kelimeleri:
        if k in anahtar:
            skor += 8
        if k in baslik:
            skor += 6
        if k in soru:
            skor += 5
        if k in ilke:
            skor += 4
        if k in sonuc:
            skor += 2
        if k in degerlendirme:
            skor += 2

    if temizle(sorgu) in baslik:
        skor += 15
    if temizle(sorgu) in anahtar:
        skor += 20

    return skor


def kalite_analizi(kartlar):
    baslik_sayac = Counter()
    ilke_sayac = Counter()
    sonuc_sayac = Counter()

    for k in kartlar:
        baslik_sayac[temizle(k["baslik"])] += 1
        ilke_sayac[temizle(k["emsal_ilke"])] += 1
        sonuc_sayac[temizle(k["sonuc"])] += 1

    ayni_baslik = sum(1 for _, adet in baslik_sayac.items() if adet > 1)
    ayni_ilke = sum(1 for _, adet in ilke_sayac.items() if adet > 1)
    ayni_sonuc = sum(1 for _, adet in sonuc_sayac.items() if adet > 1)

    print("\n" + "=" * 80)
    print("KART KALİTE / TEKRAR ANALİZİ")
    print("=" * 80)

    print(f"Toplam kart              : {len(kartlar)}")
    print(f"Benzersiz başlık         : {len(baslik_sayac)}")
    print(f"Benzersiz emsal ilke     : {len(ilke_sayac)}")
    print(f"Benzersiz sonuç          : {len(sonuc_sayac)}")
    print(f"Tekrar eden başlık grubu : {ayni_baslik}")
    print(f"Tekrar eden ilke grubu   : {ayni_ilke}")
    print(f"Tekrar eden sonuç grubu  : {ayni_sonuc}")

    print("\nEn çok tekrar eden başlıklar:")
    for baslik, adet in baslik_sayac.most_common(10):
        if adet > 1 and baslik:
            print(f"{adet:>4}  {baslik[:120]}")

    print("\nSonuç tipi dağılımı:")
    dagilim = Counter(sonuc_tipi_bul(k["sonuc"]) for k in kartlar)
    for tip, adet in dagilim.most_common():
        print(f"{adet:>4}  {tip}")


def tekrar_filtrele(sonuclar, limit=5):
    secilen = []

    for skor, kart in sonuclar:
        cok_benzer = False

        for _, onceki in secilen:
            b1 = benzerlik(kart["baslik"], onceki["baslik"])
            b2 = benzerlik(kart["emsal_ilke"], onceki["emsal_ilke"])

            if b1 >= 0.88 or b2 >= 0.88:
                cok_benzer = True
                break

        if not cok_benzer:
            secilen.append((skor, kart))

        if len(secilen) >= limit:
            break

    return secilen


def ara(sorgu, limit=5):
    kartlar = kartlari_getir()
    sonuclar = []

    for kart in kartlar:
        skor = skor_hesapla(sorgu, kart)
        if skor > 0:
            sonuclar.append((skor, kart))

    sonuclar.sort(
        key=lambda x: (
            x[0],
            len(str(x[1]["emsal_ilke"] or "")),
            len(str(x[1]["kurul_degerlendirmesi"] or "")),
        ),
        reverse=True,
    )

    return tekrar_filtrele(sonuclar, limit=limit)


def yazdir(sonuclar):
    print("\n" + "=" * 80)
    print("TEKRARSIZ EN İYİ EMSAL SONUÇLARI")
    print("=" * 80)

    if not sonuclar:
        print("Sonuç bulunamadı.")
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
    print("111 - KİK KARAR AI KART KALİTE ANALİZ VE ARAMA MOTORU")
    print("=" * 80)

    kartlar = kartlari_getir()
    kalite_analizi(kartlar)

    while True:
        sorgu = input("\nSoru / Anahtar Kelime (çıkış=q): ").strip()

        if sorgu.lower() in ["q", "quit", "exit", "çıkış"]:
            break

        sonuclar = ara(sorgu, limit=5)
        yazdir(sonuclar)

    print("\nProgram sonlandırıldı.")


if __name__ == "__main__":
    main()