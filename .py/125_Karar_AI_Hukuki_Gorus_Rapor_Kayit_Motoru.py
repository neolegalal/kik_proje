# -*- coding: utf-8 -*-

import sqlite3
import re
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher
from collections import Counter

DB_PATH = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
RAPOR_DIR = BASE_DIR / "raporlar"
RAPOR_DIR.mkdir(exist_ok=True)

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


def dosya_adi_temizle(metin):
    metin = temizle(metin)
    metin = re.sub(r"[^a-zA-Z0-9]+", "_", metin)
    return metin.strip("_")[:80] or "hukuki_gorus"


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


def rapor_uret(sorgu):
    konular = konulari_ayir(sorgu)
    konu_sonuclari = {}
    genel_dagilim = Counter()
    satirlar = []

    satirlar.append("=" * 80)
    satirlar.append("KİK KARAR AI ÇOKLU KONU HUKUKİ GÖRÜŞ RAPORU")
    satirlar.append("=" * 80)
    satirlar.append(f"Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    satirlar.append("")

    satirlar.append("1. SORU")
    satirlar.append("-" * 80)
    satirlar.append(sorgu)
    satirlar.append("")

    satirlar.append("2. AYRIŞTIRILAN KONULAR")
    satirlar.append("-" * 80)
    for konu in konular:
        satirlar.append(f"- {konu}")
    satirlar.append("")

    satirlar.append("3. EMSAL KARARLAR")
    satirlar.append("-" * 80)

    for konu in konular:
        sonuclar = konu_ara(konu)
        konu_sonuclari[konu] = sonuclar

        satirlar.append("")
        satirlar.append(f"KONU: {konu}")
        satirlar.append("-" * 80)

        if not sonuclar:
            satirlar.append("Bu konu için emsal bulunamadı.")
            continue

        for i, (skor, kart) in enumerate(sonuclar, start=1):
            tip = sonuc_tipi_bul(kart["sonuc"])
            genel_dagilim[tip] += 1

            satirlar.append(f"{i}) Karar No: {kart['karar_no']} | İddia No: {kart['iddia_no']} | Skor: {skor}")
            satirlar.append(f"   Sonuç Tipi: {tip}")
            satirlar.append(f"   Hukuki Soru: {kart['hukuki_soru']}")
            satirlar.append(f"   Sonuç: {kart['sonuc']}")
            satirlar.append(f"   İlke: {kart['emsal_ilke']}")
            satirlar.append("")

    satirlar.append("")
    satirlar.append("4. ORTAK HUKUKİ DEĞERLENDİRME")
    satirlar.append("-" * 80)
    satirlar.append(ortak_degerlendirme_uret(konular, konu_sonuclari))
    satirlar.append("")

    satirlar.append("5. SONUÇ EĞİLİMİ")
    satirlar.append("-" * 80)
    if not genel_dagilim:
        satirlar.append("Sonuç eğilimi üretilemedi.")
    else:
        for tip, adet in genel_dagilim.most_common():
            satirlar.append(f"- {tip}: {adet} emsal")
    satirlar.append("")

    satirlar.append("6. NİHAİ ÖN GÖRÜŞ")
    satirlar.append("-" * 80)
    satirlar.append(nihai_gorus_uret(genel_dagilim))
    satirlar.append("")

    satirlar.append("7. UYARI")
    satirlar.append("-" * 80)
    satirlar.append(
        "Bu metin otomatik çoklu konu emsal analizine dayalı ön hukuki görüş taslağıdır. "
        "Nihai değerlendirme için karar tam metinleri, ihale dokümanı, başvuru dilekçesi "
        "ve ilgili mevzuat birlikte incelenmelidir."
    )

    return "\n".join(satirlar)


def rapor_kaydet(sorgu, rapor):
    tarih = datetime.now().strftime("%Y%m%d_%H%M%S")
    ad = dosya_adi_temizle(sorgu)
    dosya = RAPOR_DIR / f"125_hukuki_gorus_{ad}_{tarih}.txt"

    with open(dosya, "w", encoding="utf-8") as f:
        f.write(rapor)

    return dosya


def main():
    print("=" * 80)
    print("125 - KİK KARAR AI HUKUKİ GÖRÜŞ RAPOR KAYIT MOTORU")
    print("=" * 80)

    while True:
        sorgu = input("\nÇoklu konu / hukuki soru (çıkış=q): ").strip()

        if sorgu.lower() in ["q", "quit", "exit", "çıkış"]:
            break

        rapor = rapor_uret(sorgu)
        dosya = rapor_kaydet(sorgu, rapor)

        print("\n" + rapor)
        print("\nRAPOR KAYDEDİLDİ:")
        print(dosya)

    print("\nProgram sonlandırıldı.")


if __name__ == "__main__":
    main()