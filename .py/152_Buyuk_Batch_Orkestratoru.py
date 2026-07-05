# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
BATCH_DIR = os.path.join(BASE_DIR, "batch_planlari")

DEFAULT_SOURCE_DIR = os.path.join(PY_DIR, "pdfler")
BATCH_SIZE = 500
MAX_BATCH = 999999
DB_YAZ = False

MANUAL_KARAR_NO_OVERRIDES = {
    "2008.09.16_16.09.2008.pdf": "2008/ISTISNA-16092008",
    "2022.11.28_KIK-YOK.pdf": "2022/KIK-YOK-1128",
}

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(BATCH_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def normalize_karar_no(text):
    if not text:
        return ""

    text = str(text).upper()

    text = text.replace("0008-", "2008-")
    text = text.replace("200-", "2008-")
    text = text.replace(".1-", ".I-")
    text = text.replace("--", "-")

    patterns = [
        r"(20\d{2})[-_.]?([A-ZÇĞİÖŞÜ]{2,}(?:\.[A-ZÇĞİÖŞÜI]+)?)[-_.]+(\d+)",
        r"(20\d{2})([A-ZÇĞİÖŞÜ]{2,}(?:\.[A-ZÇĞİÖŞÜI]+)?)[-_.]+(\d+)",
        r"(?:^|\\|/)(20\d{2})\.\d{2}\.\d{2}.*?([A-ZÇĞİÖŞÜ]{2,}(?:\.[A-ZÇĞİÖŞÜI]+)?)[-_.]+(\d+)",
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            yil, kod, no = m.group(1), m.group(2), m.group(3)
            kod = kod.replace(".1", ".I")
            return f"{yil}/{kod}-{no}"

    return ""


def resolve_source_dir():
    if len(sys.argv) >= 2:
        source_dir = sys.argv[1].strip('"').strip()
    else:
        source_dir = DEFAULT_SOURCE_DIR

    if not os.path.exists(source_dir):
        raise FileNotFoundError(f"Kaynak klasör bulunamadı: {source_dir}")

    if not os.path.isdir(source_dir):
        raise NotADirectoryError(f"Kaynak yol klasör değil: {source_dir}")

    return source_dir


def scan_files(source_dir):
    files = []
    total_seen = 0

    for root, dirs, filenames in os.walk(source_dir):
        for fn in filenames:
            low = fn.lower()
            if not (low.endswith(".pdf") or low.endswith(".txt")):
                continue

            total_seen += 1
            full = os.path.join(root, fn)

            karar_no = MANUAL_KARAR_NO_OVERRIDES.get(fn, "") or normalize_karar_no(fn)

            if not karar_no:
                karar_no = normalize_karar_no(full)

            try:
                size = os.path.getsize(full)
                modified = datetime.fromtimestamp(os.path.getmtime(full)).strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                size = 0
                modified = ""

            files.append({
                "dosya_yolu": full,
                "dosya_adi": fn,
                "karar_no": karar_no,
                "uzanti": os.path.splitext(fn)[1].lower(),
                "boyut": size,
                "modified": modified,
            })

            if total_seen % 5000 == 0:
                print(f"Taranan dosya: {total_seen}")

    return files


def get_db_processed_decisions():
    processed = set()

    if not os.path.exists(DB_PATH):
        return processed

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    try:
        cur.execute("""
            SELECT DISTINCT karar_no
            FROM hukuki_kartlar
            WHERE karar_no IS NOT NULL
              AND TRIM(karar_no) <> ''
        """)
        for (k,) in cur.fetchall():
            processed.add(str(k).strip().upper())
    except Exception:
        pass

    con.close()
    return processed


def chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    print("=" * 80)
    print("152 - BÜYÜK BATCH ORKESTRATÖRÜ / ÜRETİM SÜRÜMÜ")
    print("=" * 80)

    run_tag = tag()
    source_dir = resolve_source_dir()

    rapor_path = os.path.join(RAPOR_DIR, f"152_buyuk_batch_orkestrator_raporu_{run_tag}.txt")
    master_jsonl = os.path.join(BATCH_DIR, f"152_master_is_plani_{run_tag}.jsonl")
    skipped_jsonl = os.path.join(BATCH_DIR, f"152_dbde_olan_atlanan_{run_tag}.jsonl")
    no_karar_jsonl = os.path.join(BATCH_DIR, f"152_karar_no_bulunamayan_{run_tag}.jsonl")

    print(f"\nKaynak klasör: {source_dir}")
    print("Dosyalar taranıyor...")

    all_files = scan_files(source_dir)
    db_processed = get_db_processed_decisions()

    karar_no_yok = []
    adaylar = []
    dbde_olan = []
    seen_paths = set()
    seen_karar_for_batch = set()
    duplicate_in_source = []

    for item in all_files:
        path_key = item["dosya_yolu"].lower()
        if path_key in seen_paths:
            continue
        seen_paths.add(path_key)

        karar_no = item["karar_no"]

        if not karar_no:
            karar_no_yok.append(item)
            continue

        if karar_no in db_processed:
            dbde_olan.append(item)
            continue

        if karar_no in seen_karar_for_batch:
            duplicate_in_source.append(item)
            continue

        seen_karar_for_batch.add(karar_no)
        adaylar.append(item)

    adaylar.sort(key=lambda x: (x["karar_no"], x["dosya_adi"]))

    batch_files = []
    master_rows = []
    batch_count = 0

    for idx, part in enumerate(chunked(adaylar, BATCH_SIZE), start=1):
        if idx > MAX_BATCH:
            break

        batch_count += 1
        batch_path = os.path.join(BATCH_DIR, f"152_batch_{run_tag}_{idx:04d}.jsonl")
        batch_files.append(batch_path)

        rows = []
        for sira, item in enumerate(part, start=1):
            rows.append({
                "batch_no": idx,
                "batch_sira": sira,
                "karar_no": item["karar_no"],
                "dosya_adi": item["dosya_adi"],
                "dosya_yolu": item["dosya_yolu"],
                "uzanti": item["uzanti"],
                "boyut": item["boyut"],
                "modified": item["modified"],
                "durum": "ISLENECEK",
                "kaynak": "152_BUYUK_BATCH_ORKESTRATORU"
            })

        write_jsonl(batch_path, rows)

        master_rows.append({
            "batch_no": idx,
            "batch_dosyasi": batch_path,
            "kayit_sayisi": len(rows),
            "durum": "HAZIR",
            "kaynak": "152_BUYUK_BATCH_ORKESTRATORU"
        })

    write_jsonl(master_jsonl, master_rows)
    write_jsonl(skipped_jsonl, dbde_olan)
    write_jsonl(no_karar_jsonl, karar_no_yok)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("152 - BÜYÜK BATCH ORKESTRATÖRÜ RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                  : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                     : {DB_PATH}\n")
        f.write(f"Kaynak klasör           : {source_dir}\n")
        f.write(f"Batch klasörü           : {BATCH_DIR}\n")
        f.write(f"Batch size              : {BATCH_SIZE}\n")
        f.write(f"DB yaz                  : {DB_YAZ}\n\n")

        f.write("ÖZET\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam PDF/TXT dosya    : {len(all_files)}\n")
        f.write(f"DB'de olan karar        : {len(dbde_olan)}\n")
        f.write(f"İşlenecek karar/dosya   : {len(adaylar)}\n")
        f.write(f"Kaynak içi mükerrer     : {len(duplicate_in_source)}\n")
        f.write(f"Karar no bulunamayan    : {len(karar_no_yok)}\n")
        f.write(f"Oluşturulan batch       : {batch_count}\n")
        f.write(f"Master plan             : {master_jsonl}\n")
        f.write(f"DB'de olan atlanan      : {skipped_jsonl}\n")
        f.write(f"Karar no bulunamayan    : {no_karar_jsonl}\n\n")

        f.write("BATCH DOSYALARI\n")
        f.write("-" * 80 + "\n")
        for p in batch_files:
            f.write(p + "\n")

        if karar_no_yok:
            f.write("\nKARAR NO BULUNAMAYAN DOSYALAR\n")
            f.write("-" * 80 + "\n")
            for item in karar_no_yok:
                f.write(f"{item['dosya_adi']} | {item['dosya_yolu']}\n")

        if duplicate_in_source:
            f.write("\nKAYNAK İÇİ MÜKERRER İLK 100 DOSYA\n")
            f.write("-" * 80 + "\n")
            for item in duplicate_in_source[:100]:
                f.write(f"{item['karar_no']} | {item['dosya_adi']} | {item['dosya_yolu']}\n")

    print("\nBÜYÜK BATCH PLANI OLUŞTURULDU")
    print("-" * 80)
    print(f"Toplam PDF/TXT dosya  : {len(all_files)}")
    print(f"DB'de olan karar      : {len(dbde_olan)}")
    print(f"İşlenecek karar/dosya : {len(adaylar)}")
    print(f"Kaynak içi mükerrer   : {len(duplicate_in_source)}")
    print(f"Karar no bulunamayan  : {len(karar_no_yok)}")
    print(f"Oluşturulan batch     : {batch_count}")

    print("\nDosyalar:")
    print(master_jsonl)
    print(skipped_jsonl)
    print(no_karar_jsonl)
    print(rapor_path)

    print("\nNOT: DB'ye yazılmadı. Sadece büyük üretim batch planı hazırlandı.")


if __name__ == "__main__":
    main()