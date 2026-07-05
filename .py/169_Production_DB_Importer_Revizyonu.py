# -*- coding: utf-8 -*-
"""
169 - PRODUCTION DB IMPORTER REVIZYONU

Amaç:
- 168 / 168 v2 production output JSONL dosyasını okur.
- 171 v2 kalite kontrolünden geçmiş üretim çıktısını SQLite DB'ye aktarır.
- hukuki_kartlar tablosuna yeni alanları yazar:
    konu_ozeti
    sonuc_ozeti
    anahtar
- Gerekli kolonlar yoksa güvenli şekilde ekler.
- Import öncesi yedek tablo oluşturur.
- Duplicate kartları tekrar yazmaz.

Kullanım:
  python ".py\\169_Production_DB_Importer_Revizyonu.py"

Belirli output dosyası ile:
  python ".py\\169_Production_DB_Importer_Revizyonu.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\uretim_output\\168_production_output_YYYYMMDD_HHMMSS.jsonl"

Not:
- Bu dosya OpenAI API çağrısı yapmaz.
- DB'ye yazar.
"""

import os
import re
import sys
import glob
import json
import sqlite3
import traceback
from datetime import datetime

# =============================================================================
# AYARLAR
# =============================================================================

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATHS = [
    os.path.join(PY_DIR, "kik.db"),
    os.path.join(BASE_DIR, "kik.db"),
]
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

OUTPUT_PATTERN = os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl")
TABLE_NAME = "hukuki_kartlar"

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

# =============================================================================
# YARDIMCI FONKSIYONLAR
# =============================================================================

def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def find_db_path():
    for p in DB_PATHS:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("kik.db bulunamadı. Beklenen: " + " | ".join(DB_PATHS))


def get_input_path():
    if len(sys.argv) >= 2:
        p = sys.argv[1].strip().strip('"')
        if not os.path.exists(p):
            raise FileNotFoundError(f"Verilen output JSONL bulunamadı: {p}")
        return p

    p = latest_file(OUTPUT_PATTERN)
    if not p:
        raise FileNotFoundError("168 production output JSONL bulunamadı.")
    return p


def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                obj["_line_no"] = line_no
                rows.append(obj)
            except Exception as e:
                rows.append({
                    "_json_error": str(e),
                    "_line_no": line_no,
                    "_raw": line[:500],
                })
    return rows


def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def table_exists(cur, table):
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
    return cur.fetchone() is not None


def get_columns(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def add_column_if_missing(cur, table, column, coltype="TEXT"):
    cols = get_columns(cur, table)
    if column not in cols:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
        return True
    return False


def safe_text(v):
    if v is None:
        return ""
    if isinstance(v, (list, dict)):
        return json.dumps(v, ensure_ascii=False)
    return str(v).strip()


def normalize_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        out = []
        for x in v:
            s = str(x).strip()
            if s and s not in out:
                out.append(s)
        return out
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return []
        # JSON liste string geldiyse çöz.
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return normalize_list(parsed)
        except Exception:
            pass
        # Virgül / noktalı virgül ile ayrılmış metinleri listeye çevir.
        parts = re.split(r"[,;\n]+", s)
        return normalize_list(parts)
    return [str(v).strip()] if str(v).strip() else []


def list_to_db(v):
    return json.dumps(normalize_list(v), ensure_ascii=False)


def normalize_guven(v):
    s = str(v or "").strip()
    if not s:
        return "Orta"
    # Sayısal geldiyse metne çevir.
    try:
        n = float(s)
        if n >= 85:
            return "Yüksek"
        if n >= 65:
            return "Orta"
        return "Düşük"
    except Exception:
        pass
    low = s.lower()
    if "yük" in low or "yuk" in low or low == "high":
        return "Yüksek"
    if "düş" in low or "dus" in low or low == "low":
        return "Düşük"
    return "Orta"


def normalize_sonuc_tipi(v):
    s = str(v or "").strip()
    if not s:
        return "DİĞER"
    up = s.upper()
    up = up.replace("DUZELTICI", "DÜZELTİCİ")
    up = up.replace("ISLEM", "İŞLEM")
    up = up.replace("DIGER", "DİĞER")
    up = up.replace("RET", "RET")
    allowed = {
        "KABUL",
        "RET",
        "DÜZELTİCİ İŞLEM",
        "İPTAL",
        "KARAR VERİLMESİNE YER OLMADIĞI",
        "DİĞER",
    }
    if up in allowed:
        return up
    if "DÜZELT" in up:
        return "DÜZELTİCİ İŞLEM"
    if "İPTAL" in up or "IPTAL" in up:
        return "İPTAL"
    if "KABUL" in up:
        return "KABUL"
    if "RET" in up or "RED" in up:
        return "RET"
    if "YER OLMADI" in up:
        return "KARAR VERİLMESİNE YER OLMADIĞI"
    return "DİĞER"


def card_signature(karar_no, card):
    # Duplicate kontrolü: karar_no + baslik + hukuki_soru + emsal_ilke
    parts = [
        karar_no,
        safe_text(card.get("baslik")),
        safe_text(card.get("hukuki_soru")),
        safe_text(card.get("emsal_ilke")),
    ]
    raw = "||".join(parts).lower()
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def fetch_existing_signatures(cur, table):
    cols = get_columns(cur, table)
    needed = ["karar_no", "baslik", "hukuki_soru", "emsal_ilke"]
    if not all(c in cols for c in needed):
        return set()
    cur.execute(f"SELECT karar_no, baslik, hukuki_soru, emsal_ilke FROM {table}")
    sigs = set()
    for karar_no, baslik, hukuki_soru, emsal_ilke in cur.fetchall():
        fake = {"baslik": baslik, "hukuki_soru": hukuki_soru, "emsal_ilke": emsal_ilke}
        sigs.add(card_signature(str(karar_no or ""), fake))
    return sigs


def build_insert_row(cols, row_obj, card, kalite_etiketi="168_V2_READY"):
    karar_no = safe_text(row_obj.get("karar_no") or row_obj.get("orijinal_karar_no"))
    sonuc_ozeti = safe_text(card.get("sonuc_ozeti"))
    sonuc = safe_text(card.get("sonuc")) or sonuc_ozeti

    values = {
        "karar_no": karar_no,
        "baslik": safe_text(card.get("baslik")),
        "hukuki_soru": safe_text(card.get("hukuki_soru")),
        "konu_ozeti": safe_text(card.get("konu_ozeti")),
        "sonuc_ozeti": sonuc_ozeti,
        "sonuc": sonuc,
        "sonuc_tipi": normalize_sonuc_tipi(card.get("sonuc_tipi")),
        "emsal_ilke": safe_text(card.get("emsal_ilke")),
        "mevzuat": list_to_db(card.get("mevzuat")),
        "anahtar": list_to_db(card.get("anahtar")),
        "guven": normalize_guven(card.get("guven")),
        "dosya_adi": safe_text(row_obj.get("dosya_adi")),
        "dosya_yolu": safe_text(row_obj.get("dosya_yolu")),
        "kaynak_yontem": "168_v2_production_format_revision",
        "kalite_etiketi": kalite_etiketi,
        "aktif": 1,
        "created_at": now(),
        "updated_at": now(),
        "run_id": safe_text(row_obj.get("run_id")),
        "source": safe_text(row_obj.get("source")),
    }

    insert_cols = []
    insert_vals = []
    for c in cols:
        if c.lower() == "id":
            continue
        if c in values:
            insert_cols.append(c)
            insert_vals.append(values[c])
    return insert_cols, insert_vals


def ensure_schema(cur, table):
    added = []
    required = {
        "konu_ozeti": "TEXT",
        "sonuc_ozeti": "TEXT",
        "anahtar": "TEXT",
        "kaynak_yontem": "TEXT",
        "kalite_etiketi": "TEXT",
        "aktif": "INTEGER DEFAULT 1",
        "created_at": "TEXT",
        "updated_at": "TEXT",
        "run_id": "TEXT",
        "source": "TEXT",
        "dosya_adi": "TEXT",
        "dosya_yolu": "TEXT",
    }
    for col, typ in required.items():
        if add_column_if_missing(cur, table, col, typ):
            added.append(col)
    return added


def make_backup(cur, table, run_tag):
    backup_table = f"{table}_yedek_169_{run_tag}"
    cur.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM {table}")
    return backup_table

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 80)
    print("169 - PRODUCTION DB IMPORTER REVIZYONU")
    print("=" * 80)

    run_tag = tag()
    input_path = get_input_path()
    db_path = find_db_path()

    log_path = os.path.join(LOG_DIR, f"169_db_importer_detay_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"169_db_importer_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"169_production_db_importer_revizyonu_raporu_{run_tag}.txt")

    rows = read_jsonl(input_path)
    json_errors = [r for r in rows if "_json_error" in r]
    good_rows = [r for r in rows if "_json_error" not in r and r.get("status") == "OK"]

    print(f"\nInput JSONL : {input_path}")
    print(f"DB          : {db_path}")
    print("-" * 80)

    inserted = 0
    skipped_duplicate = 0
    skipped_empty = 0
    error_count = 0
    total_cards = 0
    backup_table = None
    added_columns = []

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        if not table_exists(cur, TABLE_NAME):
            raise RuntimeError(f"{TABLE_NAME} tablosu bulunamadı.")

        backup_table = make_backup(cur, TABLE_NAME, run_tag)
        added_columns = ensure_schema(cur, TABLE_NAME)
        conn.commit()

        cols = get_columns(cur, TABLE_NAME)
        existing_sigs = fetch_existing_signatures(cur, TABLE_NAME)

        for row in good_rows:
            karar_no = safe_text(row.get("karar_no") or row.get("orijinal_karar_no"))
            kartlar = row.get("kartlar", [])
            if not isinstance(kartlar, list):
                kartlar = []

            for i, card in enumerate(kartlar, start=1):
                total_cards += 1
                try:
                    if not isinstance(card, dict):
                        skipped_empty += 1
                        continue

                    # Temel zorunlu alanlar boşsa DB'ye alma.
                    required_text = [
                        safe_text(card.get("baslik")),
                        safe_text(card.get("hukuki_soru")),
                        safe_text(card.get("konu_ozeti")),
                        safe_text(card.get("sonuc_ozeti")),
                        safe_text(card.get("emsal_ilke")),
                    ]
                    if any(not x for x in required_text):
                        skipped_empty += 1
                        append_jsonl(log_path, {
                            "time": now(),
                            "status": "SKIP_EMPTY_REQUIRED",
                            "karar_no": karar_no,
                            "card_index": i,
                            "card": card,
                        })
                        continue

                    sig = card_signature(karar_no, card)
                    if sig in existing_sigs:
                        skipped_duplicate += 1
                        append_jsonl(log_path, {
                            "time": now(),
                            "status": "SKIP_DUPLICATE",
                            "karar_no": karar_no,
                            "card_index": i,
                            "baslik": safe_text(card.get("baslik")),
                        })
                        continue

                    insert_cols, insert_vals = build_insert_row(cols, row, card)
                    placeholders = ",".join(["?"] * len(insert_cols))
                    sql = f"INSERT INTO {TABLE_NAME} ({','.join(insert_cols)}) VALUES ({placeholders})"
                    cur.execute(sql, insert_vals)
                    inserted += 1
                    existing_sigs.add(sig)

                    append_jsonl(log_path, {
                        "time": now(),
                        "status": "INSERTED",
                        "karar_no": karar_no,
                        "card_index": i,
                        "baslik": safe_text(card.get("baslik")),
                    })

                except Exception as e:
                    error_count += 1
                    append_jsonl(log_path, {
                        "time": now(),
                        "status": "ERROR",
                        "karar_no": karar_no,
                        "card_index": i,
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    })

        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    ready_for_next = inserted > 0 and error_count == 0

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_path": input_path,
        "db_path": db_path,
        "table": TABLE_NAME,
        "backup_table": backup_table,
        "added_columns": added_columns,
        "jsonl_rows": len(rows),
        "json_errors": len(json_errors),
        "ok_rows": len(good_rows),
        "total_cards": total_cards,
        "inserted": inserted,
        "skipped_duplicate": skipped_duplicate,
        "skipped_empty": skipped_empty,
        "error_count": error_count,
        "ready_for_next_step": ready_for_next,
        "next_step": "170_Export_Motoru_Revizyonu.py",
        "log_path": log_path,
        "rapor_path": rapor_path,
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("169 - PRODUCTION DB IMPORTER REVIZYONU RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                 : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input JSONL            : {input_path}\n")
        f.write(f"DB                     : {db_path}\n")
        f.write(f"Tablo                  : {TABLE_NAME}\n")
        f.write(f"Yedek tablo            : {backup_table}\n")
        f.write(f"Eklenen kolonlar       : {', '.join(added_columns) if added_columns else 'Yok'}\n\n")

        f.write("OZET\n")
        f.write("-" * 80 + "\n")
        f.write(f"JSONL satır            : {len(rows)}\n")
        f.write(f"JSON hata              : {len(json_errors)}\n")
        f.write(f"OK satır               : {len(good_rows)}\n")
        f.write(f"Toplam kart            : {total_cards}\n")
        f.write(f"DB'ye eklenen kart     : {inserted}\n")
        f.write(f"Duplicate atlanan      : {skipped_duplicate}\n")
        f.write(f"Eksik alan atlanan     : {skipped_empty}\n")
        f.write(f"Hata                   : {error_count}\n")
        f.write(f"170'e geçilebilir mi   : {'EVET' if ready_for_next else 'HAYIR'}\n\n")

        f.write("DOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Detay log              : {log_path}\n")
        f.write(f"State JSON             : {state_path}\n")
        f.write(f"Rapor                  : {rapor_path}\n")

    print("\n169 DB IMPORTER TAMAMLANDI")
    print("-" * 80)
    print(f"JSONL satır            : {len(rows)}")
    print(f"OK satır               : {len(good_rows)}")
    print(f"Toplam kart            : {total_cards}")
    print(f"DB'ye eklenen kart     : {inserted}")
    print(f"Duplicate atlanan      : {skipped_duplicate}")
    print(f"Eksik alan atlanan     : {skipped_empty}")
    print(f"Hata                   : {error_count}")
    print(f"Yedek tablo            : {backup_table}")
    print(f"Eklenen kolonlar       : {', '.join(added_columns) if added_columns else 'Yok'}")
    print(f"170'e geçilebilir mi   : {'EVET' if ready_for_next else 'HAYIR'}")

    print("\nDosyalar:")
    print(log_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
