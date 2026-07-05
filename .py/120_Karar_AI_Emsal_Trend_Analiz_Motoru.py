# -*- coding: utf-8 -*-

import sqlite3
import csv
from pathlib import Path
from datetime import datetime
from collections import Counter

DB_PATH = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
RAPOR_DIR = BASE_DIR / "raporlar"
RAPOR_DIR.mkdir(exist_ok=True)

TARIH = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_RAPOR = RAPOR_DIR / f"120_emsal_trend_analizi_{TARIH}.csv"
TXT_RAPOR = RAPOR_DIR / f"120_emsal_trend_analizi_{TARIH}.txt"


def main():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    print("=" * 80)
    print("120 - KİK KARAR AI EMSAL TREND ANALİZ MOTORU")
    print("=" * 80)

    rows = cur.execute("""
        SELECT
            tarih,
            soru,
            bulunan_emsal_sayisi,
            en_guclu_karar_no,
            en_guclu_iddia_no,
            en_guclu_skor,
            sonuc_tipi,
            cevap_ozeti
        FROM ai_danisman_sorgu_loglari
        ORDER BY id DESC
    """).fetchall()

    toplam = len(rows)

    if toplam == 0:
        print("Henüz danışman sorgu logu yok.")
        return

    soru_sayac = Counter()
    karar_sayac = Counter()
    sonuc_sayac = Counter()
    basarisiz = []

    toplam_emsal = 0
    toplam_skor = 0
    skor_adet = 0

    for r in rows:
        tarih, soru, emsal_sayisi, karar_no, iddia_no, skor, sonuc_tipi, cevap_ozeti = r

        soru_sayac[soru] += 1
        sonuc_sayac[sonuc_tipi] += 1
        toplam_emsal += emsal_sayisi or 0

        if karar_no:
            karar_sayac[karar_no] += 1

        if skor:
            toplam_skor += skor
            skor_adet += 1

        if not emsal_sayisi:
            basarisiz.append((tarih, soru))

    ort_emsal = toplam_emsal / toplam if toplam else 0
    ort_skor = toplam_skor / skor_adet if skor_adet else 0

    print(f"\nToplam sorgu           : {toplam}")
    print(f"Ortalama emsal sayısı  : {ort_emsal:.2f}")
    print(f"Ortalama skor          : {ort_skor:.2f}")
    print(f"Başarısız sorgu        : {len(basarisiz)}")

    print("\nEN ÇOK SORULAN KONULAR")
    print("-" * 80)
    for soru, adet in soru_sayac.most_common(20):
        print(f"{adet:>4}  {soru}")

    print("\nEN ÇOK KULLANILAN EMSAL KARARLAR")
    print("-" * 80)
    for karar, adet in karar_sayac.most_common(20):
        print(f"{adet:>4}  {karar}")

    print("\nSONUÇ TİPİ DAĞILIMI")
    print("-" * 80)
    for tip, adet in sonuc_sayac.most_common():
        print(f"{adet:>4}  {tip}")

    print("\nEMSAL BULUNAMAYAN SORGULAR")
    print("-" * 80)
    for tarih, soru in basarisiz[:20]:
        print(f"{tarih}  |  {soru}")

    with open(CSV_RAPOR, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "tarih",
            "soru",
            "bulunan_emsal_sayisi",
            "en_guclu_karar_no",
            "en_guclu_iddia_no",
            "en_guclu_skor",
            "sonuc_tipi",
            "cevap_ozeti",
        ])
        writer.writerows(rows)

    txt = []
    txt.append("KİK KARAR AI EMSAL TREND ANALİZ RAPORU")
    txt.append(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    txt.append("")
    txt.append(f"Toplam sorgu: {toplam}")
    txt.append(f"Ortalama emsal sayısı: {ort_emsal:.2f}")
    txt.append(f"Ortalama skor: {ort_skor:.2f}")
    txt.append(f"Başarısız sorgu: {len(basarisiz)}")
    txt.append("")
    txt.append("EN ÇOK SORULAN KONULAR")
    for soru, adet in soru_sayac.most_common(20):
        txt.append(f"{adet} - {soru}")
    txt.append("")
    txt.append("EN ÇOK KULLANILAN EMSAL KARARLAR")
    for karar, adet in karar_sayac.most_common(20):
        txt.append(f"{adet} - {karar}")
    txt.append("")
    txt.append("SONUÇ TİPİ DAĞILIMI")
    for tip, adet in sonuc_sayac.most_common():
        txt.append(f"{adet} - {tip}")
    txt.append("")
    txt.append("EMSAL BULUNAMAYAN SORGULAR")
    for tarih, soru in basarisiz[:50]:
        txt.append(f"{tarih} - {soru}")

    with open(TXT_RAPOR, "w", encoding="utf-8") as f:
        f.write("\n".join(txt))

    con.close()

    print("\nRaporlar oluşturuldu:")
    print(CSV_RAPOR)
    print(TXT_RAPOR)


if __name__ == "__main__":
    main()