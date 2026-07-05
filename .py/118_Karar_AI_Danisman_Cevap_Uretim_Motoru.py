# -*- coding: utf-8 -*-

import sqlite3
import re
from difflib import SequenceMatcher
from collections import Counter

DB_PATH = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"
MIN_SKOR = 50
LIMIT = 3


def temizle(metin):
    if metin is None:
        return ""
    metin = str(metin).lower()
    metin = metin.replace("ı", "i").replace("ğ", "g").replace("ü", "u")
    metin = metin.replace("ş", "s").replace("ö", "o").replace("ç", "c")
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
            kurul_degerlendirmesi,
            mevzuat,
            guven
        FROM hukuki_kartlar
        ORDER BY karar_no, iddia_no
    """).fetchall()

    con.close()
    return rows


def konu_zorunlu_eslesme(sorgu, kart):
    sorgu_norm = temizle(sorgu)
    sorgu_kelimeleri = kelimeler(sorgu)

    alan = " ".join([
        temizle(kart["baslik"]),
        temizle(kart["hukuki_soru"]),
        temizle(kart["anahtar_kelime"]),
    ])

    if sorgu_norm in alan:
        return True

    if len(sorgu_kelimeleri) == 1:
        return sorgu_kelimeleri[0] in alan

    eslesen = sum(1 for k in sorgu_kelimeleri if k in alan)
    return eslesen >= max(2, len(sorgu_kelimeleri))


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

    if sorgu_norm == anahtar:
        skor += 120
    if sorgu_norm == baslik:
        skor += 100
    if sorgu_norm in anahtar:
        skor += 90
    if sorgu_norm in baslik:
        skor += 80
    if sorgu_norm in soru:
        skor += 60
    if sorgu_norm in ilke:
        skor += 30

    for k in sorgu_kelimeleri:
        if k in anahtar:
            skor += 15
        if k in baslik:
            skor += 12
        if k in soru:
            skor += 10
        if k in ilke:
            skor += 5
        if k in sonuc:
            skor += 2
        if k in degerlendirme:
            skor += 2

    return skor


def tekrar_filtrele(sonuclar):
    secilen = []

    for skor, kart in sonuclar:
        tekrar = False

        for _, onceki in secilen:
            if benzerlik(kart["baslik"], onceki["baslik"]) >= 0.92:
                tekrar = True
                break
            if benzerlik(kart["emsal_ilke"], onceki["emsal_ilke"]) >= 0.92:
                tekrar = True
                break

        if not tekrar:
            secilen.append((skor, kart))

        if len(secilen) >= LIMIT:
            break

    return secilen


def ara(sorgu):
    kartlar = kartlari_getir()
    sonuclar = []

    for kart in kartlar:
        if not konu_zorunlu_eslesme(sorgu, kart):
            continue

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


def sonuc_dagilimi(sonuclar):
    return Counter(sonuc_tipi_bul(kart["sonuc"]) for _, kart in sonuclar)


def danisman_cevabi_uret(sorgu, sonuclar):
    print("\n" + "=" * 80)
    print("KİK KARAR AI DANIŞMAN CEVABI")
    print("=" * 80)

    print("\nSORU / KONU:")
    print(sorgu)

    if not sonuclar:
        print("\nCEVAP:")
        print("Bu konuya ilişkin yeterli emsal kart bulunamadı.")
        print("\nNOT:")
        print("Bu sonuç, mevcut test veritabanı ile sınırlıdır. Büyük veri aktarımı yapıldıkça cevap kapsamı genişleyecektir.")
        return

    dagilim = sonuc_dagilimi(sonuclar)
    ana_sonuc = dagilim.most_common(1)[0][0]
    en_iyi_skor, en_iyi = sonuclar[0]

    print("\nKISA CEVAP:")
    print(en_iyi["emsal_ilke"])

    print("\nDEĞERLENDİRME:")
    print(
        f"Mevcut veri tabanında bu konuya ilişkin {len(sonuclar)} güçlü emsal kart bulundu. "
        f"En yüksek eşleşme {en_iyi['karar_no']} sayılı kararın {en_iyi['iddia_no']} numaralı iddiasıdır."
    )

    print("\nSONUÇ EĞİLİMİ:")
    for tip, adet in dagilim.most_common():
        print(f"- {tip}: {adet} emsal")

    print("\nEN GÜÇLÜ EMSAL:")
    print(f"Karar No : {en_iyi['karar_no']}")
    print(f"İddia No : {en_iyi['iddia_no']}")
    print(f"Skor     : {en_iyi_skor}")
    print(f"Güven    : {en_iyi['guven'] or 'Belirtilmemiş'}")

    print("\nHukuki Soru:")
    print(en_iyi["hukuki_soru"])

    print("\nKurul Sonucu:")
    print(en_iyi["sonuc"])

    print("\nEmsal İlke:")
    print(en_iyi["emsal_ilke"])

    if en_iyi["mevzuat"]:
        print("\nMevzuat:")
        print(en_iyi["mevzuat"])

    print("\nDİĞER EMSALLER:")
    for i, (skor, kart) in enumerate(sonuclar[1:], start=2):
        print(f"\n[{i}] {kart['karar_no']} / İddia {kart['iddia_no']} / Skor {skor}")
        print(f"Sonuç: {kart['sonuc']}")
        print(f"İlke : {kart['emsal_ilke']}")

    print("\nUYARI:")
    print("Bu cevap otomatik emsal kart analizine dayalıdır; nihai hukuki görüş için karar metni ve ihale dokümanı birlikte incelenmelidir.")


def kalite_ozeti():
    kartlar = kartlari_getir()
    print("\nKART HAVUZU")
    print("-" * 80)
    print(f"Toplam kart: {len(kartlar)}")


def main():
    print("=" * 80)
    print("118 - KİK KARAR AI DANIŞMAN CEVAP ÜRETİM MOTORU")
    print("=" * 80)

    kalite_ozeti()

    while True:
        sorgu = input("\nSoru / Konu (çıkış=q): ").strip()

        if sorgu.lower() in ["q", "quit", "exit", "çıkış"]:
            break

        sonuclar = ara(sorgu)
        danisman_cevabi_uret(sorgu, sonuclar)

    print("\nProgram sonlandırıldı.")


if __name__ == "__main__":
    main()