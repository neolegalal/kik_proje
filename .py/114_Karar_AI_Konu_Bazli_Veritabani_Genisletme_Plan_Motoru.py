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
CSV_PLAN = RAPOR_DIR / f"114_konu_bazli_genisletme_plani_{TARIH}.csv"
TXT_PLAN = RAPOR_DIR / f"114_konu_bazli_genisletme_plani_{TARIH}.txt"

HEDEF_KONULAR = {
    "iş deneyim belgesi": {
        "varyasyon": ["iş deneyim", "is deneyim", "iş bitirme", "is bitirme", "iş durum", "is durum"],
        "oncelik": 1,
        "hedef_min_kart": 100,
    },
    "benzer iş": {
        "varyasyon": ["benzer iş", "benzer is", "benzer iş grubu", "benzer is grubu"],
        "oncelik": 1,
        "hedef_min_kart": 100,
    },
    "iş ortaklığı": {
        "varyasyon": ["iş ortaklığı", "is ortakligi", "ortak girişim", "ortak girisim", "pilot ortak", "özel ortak", "ozel ortak"],
        "oncelik": 1,
        "hedef_min_kart": 80,
    },
    "yasaklama": {
        "varyasyon": ["yasaklama", "ihalelere katılmaktan yasaklama", "ihalelere katilmaktan yasaklama", "4734 58", "4735 26"],
        "oncelik": 1,
        "hedef_min_kart": 80,
    },
    "yaklaşık maliyet": {
        "varyasyon": ["yaklaşık maliyet", "yaklasik maliyet"],
        "oncelik": 2,
        "hedef_min_kart": 70,
    },
    "sınır değer": {
        "varyasyon": ["sınır değer", "sinir deger"],
        "oncelik": 2,
        "hedef_min_kart": 70,
    },
    "alt yüklenici": {
        "varyasyon": ["alt yüklenici", "alt yuklenici"],
        "oncelik": 2,
        "hedef_min_kart": 50,
    },
    "bilanço": {
        "varyasyon": ["bilanço", "bilanco", "bilanço oranları", "bilanco oranlari"],
        "oncelik": 3,
        "hedef_min_kart": 40,
    },
    "ciro": {
        "varyasyon": ["ciro", "iş hacmi", "is hacmi", "toplam ciro"],
        "oncelik": 3,
        "hedef_min_kart": 40,
    },
    "kesin teminat": {
        "varyasyon": ["kesin teminat"],
        "oncelik": 3,
        "hedef_min_kart": 40,
    },
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


def baglan():
    return sqlite3.connect(DB_PATH)


def kart_sayisi(cur, varyasyonlar):
    sartlar = []
    params = []

    for v in varyasyonlar:
        v = temizle(v)
        like = f"%{v}%"
        sartlar.append("""
            (
                LOWER(IFNULL(baslik,'')) LIKE ?
                OR LOWER(IFNULL(hukuki_soru,'')) LIKE ?
                OR LOWER(IFNULL(sonuc,'')) LIKE ?
                OR LOWER(IFNULL(emsal_ilke,'')) LIKE ?
                OR LOWER(IFNULL(anahtar_kelime,'')) LIKE ?
                OR LOWER(IFNULL(kurul_degerlendirmesi,'')) LIKE ?
            )
        """)
        params.extend([like, like, like, like, like, like])

    sql = f"""
        SELECT COUNT(*), COUNT(DISTINCT karar_no)
        FROM hukuki_kartlar
        WHERE {" OR ".join(sartlar)}
    """

    return cur.execute(sql, params).fetchone()


def karar_adaylari(cur, varyasyonlar, limit=10):
    sartlar = []
    params = []

    for v in varyasyonlar:
        v = temizle(v)
        like = f"%{v}%"
        sartlar.append("""
            (
                LOWER(IFNULL(tam_metin,'')) LIKE ?
                OR LOWER(IFNULL(karar_soru_basligi,'')) LIKE ?
                OR LOWER(IFNULL(karar_ozeti,'')) LIKE ?
                OR LOWER(IFNULL(karar_sonuc_ozeti,'')) LIKE ?
                OR LOWER(IFNULL(anahtar_kelimeler,'')) LIKE ?
                OR LOWER(IFNULL(ilgili_mevzuat,'')) LIKE ?
            )
        """)
        params.extend([like, like, like, like, like, like])

    sql = f"""
        SELECT
            karar_no,
            karar_tarihi,
            ihale_konusu,
            karar_soru_basligi,
            anahtar_kelimeler
        FROM kararlar
        WHERE {" OR ".join(sartlar)}
        ORDER BY karar_tarihi DESC
        LIMIT {limit}
    """

    try:
        return cur.execute(sql, params).fetchall()
    except Exception:
        return []


def plan_uret():
    con = baglan()
    cur = con.cursor()

    satirlar = []
    txt = []

    print("=" * 80)
    print("114 - KİK KARAR AI KONU BAZLI VERİTABANI GENİŞLETME PLAN MOTORU")
    print("=" * 80)

    txt.append("KİK KARAR AI KONU BAZLI VERİTABANI GENİŞLETME PLANI")
    txt.append(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    txt.append("")

    for konu, bilgi in sorted(HEDEF_KONULAR.items(), key=lambda x: x[1]["oncelik"]):
        varyasyonlar = bilgi["varyasyon"]
        oncelik = bilgi["oncelik"]
        hedef = bilgi["hedef_min_kart"]

        mevcut_kart, mevcut_karar = kart_sayisi(cur, varyasyonlar)
        eksik = max(0, hedef - mevcut_kart)

        if mevcut_kart == 0:
            durum = "KRİTİK BOŞLUK"
        elif mevcut_kart < hedef * 0.25:
            durum = "ZAYIF"
        elif mevcut_kart < hedef * 0.75:
            durum = "ORTA"
        else:
            durum = "YETERLİ"

        if oncelik == 1:
            islem = "Öncelikli işlenecek konu. PDF/karar taraması bu başlıktan başlatılmalı."
        elif oncelik == 2:
            islem = "İkinci fazda artırılmalı."
        else:
            islem = "Destekleyici konu olarak planlanmalı."

        adaylar = karar_adaylari(cur, varyasyonlar, limit=5)
        aday_ozet = " | ".join([str(a[0]) for a in adaylar]) if adaylar else "Aday karar bulunamadı"

        print(f"\nKonu        : {konu}")
        print(f"Öncelik     : {oncelik}")
        print(f"Mevcut kart : {mevcut_kart}")
        print(f"Hedef kart  : {hedef}")
        print(f"Eksik kart  : {eksik}")
        print(f"Durum       : {durum}")
        print(f"Adaylar     : {aday_ozet}")

        txt.extend([
            f"Konu: {konu}",
            f"Öncelik: {oncelik}",
            f"Mevcut kart: {mevcut_kart}",
            f"Hedef kart: {hedef}",
            f"Eksik kart: {eksik}",
            f"Durum: {durum}",
            f"Önerilen işlem: {islem}",
            f"Aday kararlar: {aday_ozet}",
            "-" * 80,
        ])

        satirlar.append([
            konu,
            oncelik,
            mevcut_kart,
            mevcut_karar,
            hedef,
            eksik,
            durum,
            islem,
            aday_ozet,
            ", ".join(varyasyonlar),
        ])

    with open(CSV_PLAN, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "konu",
            "oncelik",
            "mevcut_kart",
            "mevcut_karar",
            "hedef_min_kart",
            "eksik_kart",
            "durum",
            "onerilen_islem",
            "aday_kararlar",
            "aranacak_varyasyonlar",
        ])
        writer.writerows(satirlar)

    with open(TXT_PLAN, "w", encoding="utf-8") as f:
        f.write("\n".join(txt))

    con.close()

    print("\n" + "=" * 80)
    print("PLAN RAPORLARI OLUŞTURULDU")
    print("=" * 80)
    print(CSV_PLAN)
    print(TXT_PLAN)


if __name__ == "__main__":
    plan_uret()