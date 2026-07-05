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


def konulari_ayir(sorgu):
    parcalar = re.split(r"\+|,| ve | ile | / ", sorgu)
    return [p.strip() for p in parcalar if p.strip()]


def benzerlik(a, b):
    return SequenceMatcher(None, temizle(a), temizle(b)).ratio()


def sonuc_tipi_bul(sonuc):
    s = temizle(sonuc)

    ret_kaliplari = [
        "kabul edilmemistir", "kabul edilmemis",
        "uygun bulunmamistir", "yerinde bulunmamistir",
        "yerinde gorulmemistir", "reddedilmistir",
        "reddedilmis", "ret edilmistir", "ret edilmis", "reddine"
    ]

    kabul_kaliplari = [
        "kabul edilmistir", "kabul edilmis",
        "uygun bulunmustur", "yerinde bulunmustur",
        "yerinde gorulmustur", "duzeltici islem"
    ]

    if "iptal" in s:
        return "İPTAL"
    if any(k in s for k in ret_kaliplari):
        return "RET"
    if any(k in s for k in kabul_kaliplari):
        return "KABUL"
    if "ret" in s or "redd" in s:
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


def konu_eslesir(konu, kart):
    konu_norm = temizle(konu)
    konu_kelimeleri = kelimeler(konu)

    alan = " ".join([
        temizle(kart["baslik"]),
        temizle(kart["hukuki_soru"]),
        temizle(kart["anahtar_kelime"]),
    ])

    if konu_norm in alan:
        return True

    if len(konu_kelimeleri) == 1:
        return konu_kelimeleri[0] in alan

    eslesen = sum(1 for k in konu_kelimeleri if k in alan)
    return eslesen >= max(2, len(konu_kelimeleri))


def skor_hesapla(konu, kart):
    skor = 0

    konu_norm = temizle(konu)
    konu_kelimeleri = kelimeler(konu)

    baslik = temizle(kart["baslik"])
    soru = temizle(kart["hukuki_soru"])
    sonuc = temizle(kart["sonuc"])
    ilke = temizle(kart["emsal_ilke"])
    anahtar = temizle(kart["anahtar_kelime"])
    degerlendirme = temizle(kart["kurul_degerlendirmesi"])

    if konu_norm == anahtar:
        skor += 120
    if konu_norm in anahtar:
        skor += 90
    if konu_norm in baslik:
        skor += 80
    if konu_norm in soru:
        skor += 60
    if konu_norm in ilke:
        skor += 30

    for k in konu_kelimeleri:
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


def konu_ara(konu):
    kartlar = kartlari_getir()
    sonuclar = []

    for kart in kartlar:
        if not konu_eslesir(konu, kart):
            continue

        skor = skor_hesapla(konu, kart)

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


def ortak_degerlendirme_uret(konular, konu_sonuclari):
    metinler = []

    metinler.append(
        "Mevcut emsal kartlar birlikte değerlendirildiğinde uyuşmazlığın tek bir başlık altında değil, "
        "birden fazla hukuki unsurun birlikte ele alınmasını gerektirdiği görülmektedir."
    )

    for konu in konular:
        sonuclar = konu_sonuclari.get(konu, [])

        if not sonuclar:
            metinler.append(f"{konu} bakımından mevcut test veritabanında yeterli emsal bulunamamıştır.")
            continue

        skor, kart = sonuclar[0]
        metinler.append(
            f"{konu} bakımından en güçlü emsal {kart['karar_no']} sayılı kararın "
            f"{kart['iddia_no']} numaralı iddiasıdır. Bu emsale göre; {kart['emsal_ilke']}"
        )

    if len(konular) >= 2:
        metinler.append(
            "Bu konular birlikte değerlendirildiğinde, Kurul yaklaşımının genellikle ihale dokümanı, "
            "isteklinin sunduğu belgeler, teklif ilişkileri ve somut olayın özellikleri çerçevesinde "
            "oluştuğu anlaşılmaktadır."
        )

    return "\n\n".join(metinler)


def nihai_gorus_uret(dagilim):
    if not dagilim:
        return "Mevcut veri tabanında yeterli emsal bulunmadığından nihai ön görüş üretilememiştir."

    ana_tip = dagilim.most_common(1)[0][0]

    if ana_tip == "RET":
        return "Mevcut emsal kartlara göre başvurunun reddedilmesi yönünde ağırlıklı bir eğilim bulunmaktadır."
    if ana_tip == "KABUL":
        return "Mevcut emsal kartlara göre başvuru iddiasının kabulü yönünde ağırlıklı bir eğilim bulunmaktadır."
    if ana_tip == "İPTAL":
        return "Mevcut emsal kartlarda ihale sürecini etkileyen ve iptal sonucu doğurabilecek değerlendirmeler ağırlıktadır."

    return "Mevcut emsal kartlarda sonuç eğilimi net değildir; somut olayın ayrıca incelenmesi gerekir."


def yazdir(sorgu):
    konular = konulari_ayir(sorgu)
    konu_sonuclari = {}
    genel_dagilim = Counter()

    print("\n" + "=" * 80)
    print("124 - KİK KARAR AI ÇOKLU KONU HUKUKİ GÖRÜŞ TASLAĞI")
    print("=" * 80)

    print("\n1. SORU")
    print("-" * 80)
    print(sorgu)

    print("\n2. AYRIŞTIRILAN KONULAR")
    print("-" * 80)
    for konu in konular:
        print(f"- {konu}")

    print("\n3. EMSAL KARARLAR")
    print("-" * 80)

    for konu in konular:
        sonuclar = konu_ara(konu)
        konu_sonuclari[konu] = sonuclar

        print(f"\nKONU: {konu}")
        print("-" * 80)

        if not sonuclar:
            print("Bu konu için emsal bulunamadı.")
            continue

        for i, (skor, kart) in enumerate(sonuclar, start=1):
            tip = sonuc_tipi_bul(kart["sonuc"])
            genel_dagilim[tip] += 1

            print(f"{i}) Karar No: {kart['karar_no']} | İddia No: {kart['iddia_no']} | Skor: {skor}")
            print(f"   Sonuç Tipi: {tip}")
            print(f"   Hukuki Soru: {kart['hukuki_soru']}")
            print(f"   Sonuç: {kart['sonuc']}")
            print(f"   İlke: {kart['emsal_ilke']}")
            print("")

    print("\n4. ORTAK HUKUKİ DEĞERLENDİRME")
    print("-" * 80)
    print(ortak_degerlendirme_uret(konular, konu_sonuclari))

    print("\n5. SONUÇ EĞİLİMİ")
    print("-" * 80)
    if not genel_dagilim:
        print("Sonuç eğilimi üretilemedi.")
    else:
        for tip, adet in genel_dagilim.most_common():
            print(f"- {tip}: {adet} emsal")

    print("\n6. NİHAİ ÖN GÖRÜŞ")
    print("-" * 80)
    print(nihai_gorus_uret(genel_dagilim))

    print("\n7. UYARI")
    print("-" * 80)
    print(
        "Bu metin otomatik çoklu konu emsal analizine dayalı ön hukuki görüş taslağıdır. "
        "Nihai değerlendirme için karar tam metinleri, ihale dokümanı, başvuru dilekçesi "
        "ve ilgili mevzuat birlikte incelenmelidir."
    )


def main():
    print("=" * 80)
    print("124 - KİK KARAR AI ÇOKLU KONU HUKUKİ GÖRÜŞ MOTORU")
    print("=" * 80)

    while True:
        sorgu = input("\nÇoklu konu / hukuki soru (çıkış=q): ").strip()

        if sorgu.lower() in ["q", "quit", "exit", "çıkış"]:
            break

        yazdir(sorgu)

    print("\nProgram sonlandırıldı.")


if __name__ == "__main__":
    main()