# -*- coding: utf-8 -*-
import os
import re
import json
import glob
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

READY_PATTERN = os.path.join(URETIM_OUTPUT_DIR, "159_db_ready_cards_*.jsonl")

DB_YAZ = True
KAYNAK_YONTEM = "PRODUCTION_158"

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def read_jsonl(path):
    rows = []
    errors = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                errors.append({"line_no": line_no, "error": str(e), "raw": line[:500]})
    return rows, errors


def table_columns(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def ensure_columns(cur, columns):
    mevcut = set(table_columns(cur, "hukuki_kartlar"))

    add_map = {
        "aktif": "INTEGER DEFAULT 1",
        "kalite_etiketi": "TEXT",
        "kalite_notu": "TEXT",
        "kaynak_yontem": "TEXT",
        "created_at": "TEXT",
    }

    added = []
    for col, ddl in add_map.items():
        if col not in mevcut:
            cur.execute(f"ALTER TABLE hukuki_kartlar ADD COLUMN {col} {ddl}")
            added.append(col)

    return added


def make_backup(cur, t):
    backup_table = f"hukuki_kartlar_yedek_160_{t}"
    cur.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM hukuki_kartlar")
    return backup_table


def get_existing_karar_set(cur):
    try:
        cur.execute("SELECT DISTINCT karar_no FROM hukuki_kartlar WHERE karar_no IS NOT NULL AND TRIM(karar_no)<>''")
        return {str(r[0]).strip().upper() for r in cur.fetchall()}
    except Exception:
        return set()


def get_next_id(cur, columns):
    if "id" not in columns:
        return None
    try:
        cur.execute("SELECT COALESCE(MAX(id),0) FROM hukuki_kartlar")
        return int(cur.fetchone()[0]) + 1
    except Exception:
        return None


def build_insert_row(card_result, columns, next_id=None):
    card = card_result.get("card", {})
    karar_no = card_result.get("karar_no", "")

    values = {}

    if "id" in columns and next_id is not None:
        values["id"] = next_id

    mapping = {
        "karar_no": karar_no,
        "baslik": card.get("baslik", ""),
        "hukuki_soru": card.get("hukuki_soru", ""),
        "sonuc_tipi": card.get("sonuc_tipi", ""),
        "sonuc": card.get("sonuc", ""),
        "emsal_ilke": card.get("emsal_ilke", ""),
        "anahtar": card.get("anahtar", ""),
        "mevzuat": card.get("mevzuat", ""),
        "guven": card.get("guven", ""),
        "kaynak_yontem": KAYNAK_YONTEM,
        "aktif": 1,
        "kalite_etiketi": "PRODUCTION_READY",
        "kalite_notu": "159 kalite kontrolünden geçti.",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    for col in columns:
        if col in mapping:
            values[col] = mapping[col]

    return values


def insert_row(cur, values):
    cols = list(values.keys())
    placeholders = ",".join(["?"] * len(cols))
    sql = f"INSERT INTO hukuki_kartlar ({','.join(cols)}) VALUES ({placeholders})"
    cur.execute(sql, [values[c] for c in cols])


def main():
    print("=" * 80)
    print("160 - PRODUCTION DB IMPORTER")
    print("=" * 80)

    t = tag()

    ready_path = latest_file(READY_PATTERN)
    if not ready_path:
        raise FileNotFoundError("159 DB ready JSONL bulunamadı.")

    rows, errors = read_jsonl(ready_path)
    if errors:
        raise RuntimeError(f"Ready JSONL içinde JSON hatası var: {len(errors)}")

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"DB bulunamadı: {DB_PATH}")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    added_columns = ensure_columns(cur, [])
    backup_table = make_backup(cur, t)

    columns = table_columns(cur, "hukuki_kartlar")
    existing_karars = get_existing_karar_set(cur)
    next_id = get_next_id(cur, columns)

    inserted = 0
    skipped_duplicate_karar = 0
    skipped_not_ready = 0
    failed = 0
    details = []

    for r in rows:
        try:
            if not r.get("db_ready", False):
                skipped_not_ready += 1
                details.append({"status": "SKIP_NOT_READY", "karar_no": r.get("karar_no")})
                continue

            karar_no = str(r.get("karar_no", "")).strip()
            if not karar_no:
                failed += 1
                details.append({"status": "FAILED", "reason": "KARAR_NO_YOK", "row": r})
                continue

            # Pilot yeni üretimde aynı karar zaten DB'de varsa tekrar yazma.
            if karar_no.upper() in existing_karars:
                skipped_duplicate_karar += 1
                details.append({"status": "SKIP_DBDE_VAR", "karar_no": karar_no, "baslik": r.get("baslik")})
                continue

            values = build_insert_row(r, columns, next_id)

            if DB_YAZ:
                insert_row(cur, values)

            inserted += 1
            details.append({"status": "INSERTED", "karar_no": karar_no, "baslik": r.get("baslik")})

            if next_id is not None:
                next_id += 1

        except Exception as e:
            failed += 1
            details.append({
                "status": "FAILED",
                "karar_no": r.get("karar_no"),
                "baslik": r.get("baslik"),
                "error": str(e),
            })

    if DB_YAZ:
        con.commit()
    con.close()

    rapor_path = os.path.join(RAPOR_DIR, f"160_production_db_importer_raporu_{t}.txt")
    state_path = os.path.join(STATE_DIR, f"160_production_db_importer_state_{t}.json")
    detail_jsonl = os.path.join(URETIM_OUTPUT_DIR, f"160_production_db_importer_detay_{t}.jsonl")

    with open(detail_jsonl, "w", encoding="utf-8") as f:
        for d in details:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    state = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ready_path": ready_path,
        "db_path": DB_PATH,
        "db_yaz": DB_YAZ,
        "kaynak_yontem": KAYNAK_YONTEM,
        "backup_table": backup_table,
        "ready_rows": len(rows),
        "inserted": inserted,
        "skipped_duplicate_karar": skipped_duplicate_karar,
        "skipped_not_ready": skipped_not_ready,
        "failed": failed,
        "added_columns": added_columns,
        "detail_jsonl": detail_jsonl,
        "next_step": "146_Aktif_Kart_Son_Kalite_Raporu.py",
    }

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("160 - PRODUCTION DB IMPORTER RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                  : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                     : {DB_PATH}\n")
        f.write(f"Ready JSONL             : {ready_path}\n")
        f.write(f"DB yaz                  : {DB_YAZ}\n")
        f.write(f"Kaynak yöntem           : {KAYNAK_YONTEM}\n")
        f.write(f"Yedek tablo             : {backup_table}\n\n")

        f.write("ÖZET\n")
        f.write("-" * 80 + "\n")
        f.write(f"Ready kayıt             : {len(rows)}\n")
        f.write(f"DB'ye eklenen           : {inserted}\n")
        f.write(f"DB'de var diye atlanan  : {skipped_duplicate_karar}\n")
        f.write(f"Ready değil atlanan     : {skipped_not_ready}\n")
        f.write(f"Hatalı                  : {failed}\n")
        f.write(f"Eklenen kolonlar        : {', '.join(added_columns) if added_columns else 'YOK'}\n\n")

        f.write("DETAYLAR\n")
        f.write("-" * 80 + "\n")
        for d in details[:200]:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"State JSON              : {state_path}\n")
        f.write(f"Detay JSONL             : {detail_jsonl}\n")
        f.write(f"Rapor                   : {rapor_path}\n")

    print("\nDB IMPORT TAMAMLANDI")
    print("-" * 80)
    print(f"Ready kayıt            : {len(rows)}")
    print(f"DB'ye eklenen          : {inserted}")
    print(f"DB'de var atlanan      : {skipped_duplicate_karar}")
    print(f"Ready değil atlanan    : {skipped_not_ready}")
    print(f"Hatalı                 : {failed}")
    print(f"Yedek tablo            : {backup_table}")

    print("\nDosyalar:")
    print(rapor_path)
    print(state_path)
    print(detail_jsonl)


if __name__ == "__main__":
    main()