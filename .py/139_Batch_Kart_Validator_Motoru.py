# -*- coding: utf-8 -*-
"""
139 - BATCH KART VALIDATOR MOTORU

Amaç:
- BATCH_136E kartlarını DB'den okur.
- Sonuç Tipi / Sonuç metni çelişkilerini yakalar.
- Aynı karar içindeki mükerrer kartları işaretler.
- Emsal ilke kalitesini kontrol eder.
- Güven seviyesini öneri olarak revize eder.
- DB'ye yazmaz. Sadece rapor üretir.
"""

import os
import re
import csv
import json
import sqlite3
import difflib
from datetime import datetime
from collections import defaultdict

# =============================================================================
# AYARLAR
# =============================================================================

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

DB_PATHS = [
    os.path.join(PY_DIR, "kik.db"),
    r"C:\Users\MSI\Desktop\kik_proje.py\kik.db",
]

KAYNAK_YONTEM = "BATCH_136E"

DUPLICATE_THRESHOLD = 0.78

SONUC_TIPI_LISTESI = [
    "KABUL",
    "RET",
    "DÜZELTİCİ İŞLEM",
    "İPTAL",
    "KARAR VERİLMESİNE YER OLMADIĞI",
    "BELİRSİZ",
]

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def find_db_path():
    for path in DB_PATHS:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("kik.db bulunamadı. DB_PATHS ayarını kontrol et.")


def norm(text):
    if text is None:
        return ""
    text = str(text).lower()
    text = text.replace("ı", "i").replace("İ", "i")
    text = text.replace("ğ", "g").replace("ü", "u").replace("ş", "s")
    text = text.replace("ö", "o").replace("ç", "c")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def get_table_columns(cur, table):
    rows = cur.execute(f"PRAGMA table_info({table})").fetchall()
    return [r[1] for r in rows]


def pick_col(columns, candidates):
    for c in candidates:
        if c in columns:
            return c
    return None


def safe(row, col):
    return row.get(col, "") if col else ""


def similarity(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def detect_sonuc_celiskisi(sonuc_tipi, sonuc):
    st = norm(sonuc_tipi)
    s = norm(sonuc)

    kabul_phrases = [
        "yerindedir",
        "yerinde oldugu",
        "hakli bulunmustur",
        "uygun olmadigi",
        "mevzuata aykiridir",
        "mevzuata uyarlik bulunmadigi",
        "duzeltici islem",
        "iptaline",
        "iptal edilmesine",
        "yeniden yapilmasi",
        "yeterli gorulmesi",
    ]

    ret_phrases = [
        "yerinde degildir",
        "yerinde gorulmemistir",
        "reddedilmistir",
        "reddine",
        "sure yonunden redd",
        "gorev yonunden redd",
        "itiraz niteligi",
        "uygun bulunmustur",
        "mevzuata uygundur",
        "hukuka uygundur",
    ]

    has_kabul = any(p in s for p in kabul_phrases)
    has_ret = any(p in s for p in ret_phrases)

    if st == "ret" and has_kabul and not has_ret:
        return True, "RET yazıyor ancak sonuç metni kabul/yerindelik/düzeltici işlem yönünde."
    if st == "kabul" and has_ret:
        return True, "KABUL yazıyor ancak sonuç metni ret/yerinde değil yönünde."
    if st == "duzeltici islem" and has_ret and not has_kabul:
        return True, "DÜZELTİCİ İŞLEM yazıyor ancak sonuç metni ret yönünde."
    if st == "iptal" and "iptal" not in s:
        return True, "İPTAL yazıyor ancak sonuç metninde açık iptal ifadesi yok."

    return False, ""


def önerilen_sonuc_tipi(sonuc_tipi, sonuc):
    s = norm(sonuc)

    if "iptaline" in s or "iptal edilmesine" in s or "ihalenin iptali" in s:
        return "İPTAL"

    if "duzeltici islem" in s or "yeniden gerceklestirilmesi" in s or "yeniden yapilmasi" in s:
        return "DÜZELTİCİ İŞLEM"

    if (
        "yerindedir" in s
        or "hakli bulunmustur" in s
        or "mevzuata aykiridir" in s
        or "mevzuata uyarlik bulunmadigi" in s
        or "yeterli gorulmesi" in s
    ):
        return "KABUL"

    if (
        "yerinde degildir" in s
        or "yerinde gorulmemistir" in s
        or "reddedilmistir" in s
        or "reddine" in s
        or "sure yonunden redd" in s
        or "gorev yonunden redd" in s
    ):
        return "RET"

    return sonuc_tipi or "BELİRSİZ"


def detect_emsal_sorunu(emsal, sonuc, soru):
    e = norm(emsal)
    s = norm(sonuc)
    q = norm(soru)

    sorunlar = []

    if not e or len(e) < 40:
        sorunlar.append("Emsal ilke çok kısa veya boş.")

    if e and s and similarity(e, s) >= 0.82:
        sorunlar.append("Emsal ilke sonuç cümlesini fazla tekrar ediyor.")

    if e and q and similarity(e, q) >= 0.82:
        sorunlar.append("Emsal ilke hukuki soruyu fazla tekrar ediyor.")

    weak_words = ["yerindedir", "yerinde degildir", "reddedilmistir", "kabul edilmistir"]
    if any(w in e for w in weak_words):
        sorunlar.append("Emsal ilke normatif ilke yerine karar sonucu gibi yazılmış.")

    return sorunlar


def guven_onerisi(guven, risk_count, duplicate_flag, celiski_flag):
    g = norm(guven)

    if celiski_flag:
        return "Düşük"
    if duplicate_flag or risk_count >= 2:
        return "Orta"
    if risk_count == 1:
        return "Orta" if "yuksek" in g else guven
    return guven or "Orta"


def row_to_text(row, cols):
    parts = []
    for c in cols:
        parts.append(str(row.get(c, "")))
    return " ".join(parts)


# =============================================================================
# ANA
# =============================================================================

def main():
    os.makedirs(RAPOR_DIR, exist_ok=True)

    db_path = find_db_path()
    now = datetime.now().strftime("%Y%m%d_%H%M%S")

    txt_path = os.path.join(RAPOR_DIR, f"139_batch_kart_validator_raporu_{now}.txt")
    csv_path = os.path.join(RAPOR_DIR, f"139_batch_kart_validator_ozet_{now}.csv")
    jsonl_path = os.path.join(RAPOR_DIR, f"139_batch_kart_validator_riskli_kartlar_{now}.jsonl")

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    columns = get_table_columns(cur, "hukuki_kartlar")

    col_id = pick_col(columns, ["id", "kart_id"])
    col_karar_no = pick_col(columns, ["karar_no", "kararNo", "karar"])
    col_baslik = pick_col(columns, ["baslik", "başlık"])
    col_soru = pick_col(columns, ["hukuki_soru", "soru"])
    col_sonuc_tipi = pick_col(columns, ["sonuc_tipi", "sonuç_tipi"])
    col_sonuc = pick_col(columns, ["sonuc", "sonuç"])
    col_emsal = pick_col(columns, ["emsal_ilke", "ilke"])
    col_guven = pick_col(columns, ["guven", "güven"])
    col_kaynak = pick_col(columns, ["kaynak_yontem", "kaynak"])

    required = {
        "karar_no": col_karar_no,
        "baslik": col_baslik,
        "hukuki_soru": col_soru,
        "sonuc_tipi": col_sonuc_tipi,
        "sonuc": col_sonuc,
        "emsal_ilke": col_emsal,
        "guven": col_guven,
        "kaynak_yontem": col_kaynak,
    }

    missing = [k for k, v in required.items() if not v]
    if missing:
        raise RuntimeError(f"Eksik kolonlar: {missing}\nMevcut kolonlar: {columns}")

    rows = cur.execute(
        f"""
        SELECT *
        FROM hukuki_kartlar
        WHERE {col_kaynak} = ?
        ORDER BY {col_karar_no}, {col_id if col_id else col_karar_no}
        """,
        (KAYNAK_YONTEM,)
    ).fetchall()

    cards = [dict(r) for r in rows]

    by_karar = defaultdict(list)
    for r in cards:
        by_karar[safe(r, col_karar_no)].append(r)

    riskli_kartlar = []
    csv_rows = []

    report_lines = []
    report_lines.append("139 - BATCH KART VALIDATOR MOTORU")
    report_lines.append("=" * 100)
    report_lines.append(f"Tarih        : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    report_lines.append(f"DB           : {db_path}")
    report_lines.append(f"Kaynak       : {KAYNAK_YONTEM}")
    report_lines.append(f"Karar sayısı : {len(by_karar)}")
    report_lines.append(f"Kart sayısı  : {len(cards)}")
    report_lines.append("")

    total_celiski = 0
    total_duplicate = 0
    total_emsal = 0
    total_guven_revize = 0
    total_riskli = 0

    for karar_no, karar_cards in by_karar.items():
        duplicate_pairs = set()

        for i in range(len(karar_cards)):
            for j in range(i + 1, len(karar_cards)):
                a = karar_cards[i]
                b = karar_cards[j]

                text_a = " ".join([
                    safe(a, col_baslik),
                    safe(a, col_soru),
                    safe(a, col_emsal),
                ])
                text_b = " ".join([
                    safe(b, col_baslik),
                    safe(b, col_soru),
                    safe(b, col_emsal),
                ])

                sim = similarity(text_a, text_b)
                if sim >= DUPLICATE_THRESHOLD:
                    ida = safe(a, col_id) or f"{karar_no}_{i+1}"
                    idb = safe(b, col_id) or f"{karar_no}_{j+1}"
                    duplicate_pairs.add((ida, idb, sim))

        karar_risk_count = 0
        karar_lines = []

        for idx, r in enumerate(karar_cards, start=1):
            kart_id = safe(r, col_id) or idx
            baslik = safe(r, col_baslik)
            soru = safe(r, col_soru)
            sonuc_tipi = safe(r, col_sonuc_tipi)
            sonuc = safe(r, col_sonuc)
            emsal = safe(r, col_emsal)
            guven = safe(r, col_guven)

            celiski, celiski_notu = detect_sonuc_celiskisi(sonuc_tipi, sonuc)
            emsal_sorunlari = detect_emsal_sorunu(emsal, sonuc, soru)

            duplicate_flag = False
            duplicate_notu = ""
            for ida, idb, sim in duplicate_pairs:
                if str(kart_id) in [str(ida), str(idb)]:
                    duplicate_flag = True
                    duplicate_notu += f"Muhtemel mükerrer: {ida} - {idb} | Benzerlik: {sim:.2f}; "

            riskler = []
            if celiski:
                riskler.append(celiski_notu)
                total_celiski += 1

            if duplicate_flag:
                riskler.append(duplicate_notu.strip())
                total_duplicate += 1

            if emsal_sorunlari:
                riskler.extend(emsal_sorunlari)
                total_emsal += 1

            guven_yeni = guven_onerisi(
                guven=guven,
                risk_count=len(riskler),
                duplicate_flag=duplicate_flag,
                celiski_flag=celiski,
            )

            if norm(guven_yeni) != norm(guven):
                total_guven_revize += 1

            sonuc_tipi_oneri = önerilen_sonuc_tipi(sonuc_tipi, sonuc)

            risk_durumu = "RİSKLİ" if riskler else "TEMİZ"
            if riskler:
                karar_risk_count += 1
                total_riskli += 1

                risk_record = {
                    "karar_no": karar_no,
                    "kart_id": kart_id,
                    "baslik": baslik,
                    "mevcut_sonuc_tipi": sonuc_tipi,
                    "onerilen_sonuc_tipi": sonuc_tipi_oneri,
                    "mevcut_guven": guven,
                    "onerilen_guven": guven_yeni,
                    "riskler": riskler,
                    "sonuc": sonuc,
                    "emsal_ilke": emsal,
                }
                riskli_kartlar.append(risk_record)

            csv_rows.append({
                "karar_no": karar_no,
                "kart_id": kart_id,
                "risk_durumu": risk_durumu,
                "mevcut_sonuc_tipi": sonuc_tipi,
                "onerilen_sonuc_tipi": sonuc_tipi_oneri,
                "mevcut_guven": guven,
                "onerilen_guven": guven_yeni,
                "risk_sayisi": len(riskler),
                "riskler": " | ".join(riskler),
                "baslik": baslik,
            })

            if riskler:
                karar_lines.append(f"[KART {idx}] ID: {kart_id}")
                karar_lines.append(f"Başlık              : {baslik}")
                karar_lines.append(f"Sonuç Tipi          : {sonuc_tipi}")
                karar_lines.append(f"Önerilen Sonuç Tipi : {sonuc_tipi_oneri}")
                karar_lines.append(f"Güven               : {guven}")
                karar_lines.append(f"Önerilen Güven      : {guven_yeni}")
                karar_lines.append("Riskler:")
                for rr in riskler:
                    karar_lines.append(f" - {rr}")
                karar_lines.append("")

        if karar_lines:
            report_lines.append("=" * 100)
            report_lines.append(f"KARAR NO: {karar_no} | Kart: {len(karar_cards)} | Riskli Kart: {karar_risk_count}")
            report_lines.append("-" * 100)
            report_lines.extend(karar_lines)

    report_lines.insert(8, f"Riskli kart  : {total_riskli}")
    report_lines.insert(9, f"Çelişki      : {total_celiski}")
    report_lines.insert(10, f"Mükerrer     : {total_duplicate}")
    report_lines.insert(11, f"Emsal sorun  : {total_emsal}")
    report_lines.insert(12, f"Güven revize : {total_guven_revize}")
    report_lines.insert(13, "")

    if total_riskli == 0:
        report_lines.append("Riskli kart bulunmadı.")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        fieldnames = [
            "karar_no",
            "kart_id",
            "risk_durumu",
            "mevcut_sonuc_tipi",
            "onerilen_sonuc_tipi",
            "mevcut_guven",
            "onerilen_guven",
            "risk_sayisi",
            "riskler",
            "baslik",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_rows)

    with open(jsonl_path, "w", encoding="utf-8") as f:
        for rec in riskli_kartlar:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    con.close()

    print("=" * 80)
    print("139 - BATCH KART VALIDATOR MOTORU")
    print("=" * 80)
    print()
    print("VALIDATOR RAPORU OLUŞTURULDU")
    print("-" * 80)
    print(f"Karar sayısı : {len(by_karar)}")
    print(f"Kart sayısı  : {len(cards)}")
    print(f"Riskli kart  : {total_riskli}")
    print(f"Çelişki      : {total_celiski}")
    print(f"Mükerrer     : {total_duplicate}")
    print(f"Emsal sorun  : {total_emsal}")
    print(f"Güven revize : {total_guven_revize}")
    print()
    print("Dosyalar:")
    print(txt_path)
    print(csv_path)
    print(jsonl_path)
    print()
    print("NOT: DB'ye yazılmadı. Sadece rapor üretildi.")


if __name__ == "__main__":
    main()