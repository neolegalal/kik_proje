# -*- coding: utf-8 -*-

import sqlite3
import re
import csv
from pathlib import Path
from datetime import datetime

DB_PATH = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"
BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
RAPOR_DIR = BASE_DIR / "raporlar"
RAPOR_DIR.mkdir(exist_ok=True)

TARIH = datetime.now().strftime("%Y%m%d_%H%M%S")
CSV_RAPOR = RAPOR_DIR / f"113_konu_bosluk_analizi_{TARIH}.csv"


KRITIK_KONULAR = {
    "aşırı düşük teklif": ["aşırı düşük", "asiri dusuk"],
    "geçici teminat": ["geçici teminat", "gecici teminat"],
    "kesin teminat": ["kesin teminat"],
    "yeterlik kriteri": ["yeterlik", "yeterlilik"],
    "iş deneyim belgesi": ["iş deneyim", "is deneyim"],
    "benzer iş": ["benzer iş", "benzer is"],
    "iş ortaklığı": ["iş ortaklığı", "is ortakligi", "ortak girişim", "ortak girisim"],
    "birden fazla teklif verme": ["birden fazla teklif", "17/d"],
    "teknik şartname": ["teknik şartname", "teknik sartname"],
    "idari şartname": ["idari şartname", "idari sartname"],
    "ihale dokümanı": ["ihale dokümanı", "ihale dokumani"],
    "başvuru süresi": ["başvuru süresi", "basvuru suresi", "süre"],
    "şikayet başvurusu": ["şikayet", "sikayet"],
    "itirazen şikayet": ["itirazen şikayet", "itirazen sikayet"],
    "yasaklama": ["yasaklama", "ihalelere katılmaktan yasaklama"],
    "fiyat dışı unsur": ["fiyat dışı", "fiyat disi"],
    "yaklaşık maliyet": ["yaklaşık maliyet", "yaklasik maliyet"],
    "ekonomik açıdan en avantajlı teklif": ["ekonomik açıdan", "ekonomik acıdan", "avantajlı teklif"],
    "alt yüklenici": ["alt yüklenici", "alt yuklenici"],
    "sınır değer": ["sınır değer", "sinir deger"],
    "bilanço": ["bilanço", "bilanco"],
    "ciro": ["ciro"],
    "personel çalıştırılması": ["personel çalıştırılması", "personel calistirilmasi"],
    "araç makine ekipman": ["araç", "arac", "makine", "ekipman"],
}


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
    """).fetchall()

    con.close()
    return rows


def kart_metni(kart):
    return temizle(" ".join([
        str(kart["baslik"] or ""),
        str(kart["hukuki_soru"] or ""),
        str(kart["sonuc"] or ""),
        str(kart["emsal_ilke"] or ""),
        str(kart["anahtar_kelime"] or ""),
        str(kart["kurul_degerlendirmesi"] or ""),
    ]))


def analiz_yap():
    kartlar = kartlari_getir()
    sonuc_satirlari = []

    print("=" * 80)
    print("113 - KİK KARAR AI KONU BOŞLUK ANALİZ MOTORU")
    print("=" * 80)
    print(f"Toplam hukuki kart: {len(kartlar)}")

    print("\nKONU DAĞILIMI")
    print("-" * 80)

    for konu, varyasyonlar in KRITIK_KONULAR.items():
        adet = 0
        kararlar = set()

        varyasyonlar_norm = [temizle(v) for v in varyasyonlar]

        for kart in kartlar:
            metin = kart_metni(kart)

            if any(v in metin for v in varyasyonlar_norm):
                adet += 1
                kararlar.add(kart["karar_no"])

        durum = "VAR" if adet > 0 else "YOK"

        if adet >= 20:
            seviye = "GÜÇLÜ"
        elif adet >= 5:
            seviye = "ORTA"
        elif adet >= 1:
            seviye = "ZAYIF"
        else:
            seviye = "BOŞLUK"

        print(f"{konu:<40} {adet:>4} kart | {len(kararlar):>4} karar | {seviye}")

        sonuc_satirlari.append([
            konu,
            adet,
            len(kararlar),
            durum,
            seviye,
            ", ".join(varyasyonlar),
        ])

    with open(CSV_RAPOR, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "konu",
            "kart_sayisi",
            "karar_sayisi",
            "durum",
            "seviye",
            "aranan_varyasyonlar",
        ])
        writer.writerows(sonuc_satirlari)

    print("\nRapor oluşturuldu:")
    print(CSV_RAPOR)


if __name__ == "__main__":
    analiz_yap()