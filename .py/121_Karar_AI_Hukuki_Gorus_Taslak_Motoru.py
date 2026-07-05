# -*- coding: utf-8 -*-

import sqlite3
import re
from difflib import SequenceMatcher
from collections import Counter
from datetime import datetime

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

    ret_kaliplari = [
        "kabul edilmemistir",
        "kabul edilmemis",
        "uygun bulunmamistir",
        "yerinde bulunmamistir",
        "yerinde gorulmemistir",
        "reddedilmistir",
        "reddedilmis",
        "ret edilmistir",
        "ret edilmis",
        "reddine",
    ]

    kabul_kaliplari = [
        "kabul edilmistir",
        "kabul edilmis",
        "uygun bulunmustur",
        "yerinde bulunmustur",
        "yerinde gorulmustur",
        "duzeltici islem",
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


def log_tablosu_olustur():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_hukuki_gorus_loglari (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT,
            soru TEXT,
            emsal_sayisi INTEGER,
            en_guclu_karar_no TEXT,
            en_guclu_iddia_no INTEGER,
            en_guclu_skor INTEGER,
            sonuc_tipi TEXT
        )
    """)

    con.commit()
    con.close()


def log_yaz(soru, sonuclar):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    if sonuclar:
        skor, kart = sonuclar[0]
        karar_no = kart["karar_no"]
        iddia_no = kart["iddia_no"]
        sonuc_tipi = sonuc_tipi_bul(kart["sonuc"])
    else:
        skor = 0
        karar_no = ""
        iddia_no = None
        sonuc_tipi = "SONUÇ YOK"

    cur.execute("""
        INSERT INTO ai_hukuki_gorus_loglari (
            tarih,
            soru,
            emsal_sayisi,
            en_guclu_karar_no,
            en_guclu_iddia_no,
            en_guclu_skor,
            sonuc_tipi
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        soru,
        len(sonuclar),
        karar_no,
        iddia_no,
        skor,
        sonuc_tipi,
    ))

    con.commit()
    con.close()


def hukuki_gorus_yaz(soru, sonuclar):
    print("\n" + "=" * 80)
    print("KİK KARAR AI HUKUKİ GÖRÜŞ TASLAĞI")
    print("=" * 80)

    print("\n1. SORU")
    print("-" * 80)
    print(soru)

    if not sonuclar:
        print("\n2. KISA CEVAP")
        print("-" * 80)
        print("Mevcut test veritabanında bu konuya ilişkin yeterli emsal karar kartı bulunamamıştır.")

        print("\n3. SONUÇ")
        print("-" * 80)
        print("Bu konuda sağlıklı bir hukuki görüş taslağı üretilebilmesi için ilgili karar havuzunun genişletilmesi gerekir.")
        return

    dagilim = Counter(sonuc_tipi_bul(kart["sonuc"]) for _, kart in sonuclar)
    en_iyi_skor, en_iyi = sonuclar[0]

    print("\n2. KISA CEVAP")
    print("-" * 80)
    print(en_iyi["emsal_ilke"])

    print("\n3. EMSAL KARARLAR")
    print("-" * 80)

    for i, (skor, kart) in enumerate(sonuclar, start=1):
        print(f"{i}) Karar No: {kart['karar_no']} | İddia No: {kart['iddia_no']} | Skor: {skor}")
        print(f"   Sonuç Tipi: {sonuc_tipi_bul(kart['sonuc'])}")
        print(f"   Sonuç: {kart['sonuc']}")
        print(f"   İlke: {kart['emsal_ilke']}")
        print("")

    print("\n4. HUKUKİ DEĞERLENDİRME")
    print("-" * 80)
    print(
        f"Mevcut karar kartları içinde en güçlü emsal, {en_iyi['karar_no']} sayılı kararın "
        f"{en_iyi['iddia_no']} numaralı iddiasıdır. Bu emsal karta göre; "
        f"{en_iyi['emsal_ilke']}"
    )

    if len(sonuclar) > 1:
        print(
            "\nDiğer emsal kartlar da birlikte değerlendirildiğinde, konu bakımından Kurul yaklaşımının "
            "somut olayın özellikleri, ihale dokümanı düzenlemeleri ve başvuru iddiasının niteliği "
            "çerçevesinde şekillendiği görülmektedir."
        )

    print("\n5. SONUÇ EĞİLİMİ")
    print("-" * 80)
    for tip, adet in dagilim.most_common():
        print(f"- {tip}: {adet} emsal")

    print("\n6. SONUÇ")
    print("-" * 80)

    ana_tip = dagilim.most_common(1)[0][0]

    if ana_tip == "RET":
        print("Mevcut emsal kartlara göre başvurunun reddedilmesi yönünde bir eğilim bulunmaktadır.")
    elif ana_tip == "KABUL":
        print("Mevcut emsal kartlara göre başvuru iddiasının kabulü yönünde bir eğilim bulunmaktadır.")
    elif ana_tip == "İPTAL":
        print("Mevcut emsal kartlarda ihale sürecini etkileyen ve iptal sonucu doğurabilecek değerlendirmeler bulunmaktadır.")
    else:
        print("Mevcut emsal kartlarda sonuç eğilimi net değildir; somut olayın ayrıca incelenmesi gerekir.")

    print("\n7. UYARI")
    print("-" * 80)
    print(
        "Bu metin otomatik emsal kart analizine dayalı ön hukuki görüş taslağıdır. "
        "Nihai değerlendirme için kararın tam metni, ihale dokümanı, başvuru dilekçesi "
        "ve ilgili mevzuat birlikte incelenmelidir."
    )


def main():
    log_tablosu_olustur()

    print("=" * 80)
    print("121 - KİK KARAR AI HUKUKİ GÖRÜŞ TASLAK MOTORU")
    print("=" * 80)

    while True:
        soru = input("\nHukuki soru / konu (çıkış=q): ").strip()

        if soru.lower() in ["q", "quit", "exit", "çıkış"]:
            break

        sonuclar = ara(soru)
        log_yaz(soru, sonuclar)
        hukuki_gorus_yaz(soru, sonuclar)

    print("\nProgram sonlandırıldı.")


if __name__ == "__main__":
    main()