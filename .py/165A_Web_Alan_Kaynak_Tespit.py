# -*- coding: utf-8 -*-
import os
import json
import glob
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")

EXPORT_DIR = os.path.join(BASE_DIR, "export")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

WEB_PATTERN = os.path.join(EXPORT_DIR, "151_web_aktif_kartlar_*.jsonl")

FIELD_ALIASES = {
    "konu_ozeti": [
        "konu_ozeti", "konu_özeti", "karar_ozeti", "karar_özeti",
        "ozet", "özet", "konu", "karar_konu_ozeti"
    ],
    "sonuc_ozeti": [
        "sonuc_ozeti", "sonuç_özeti", "sonuc", "sonuç",
        "karar_sonucu", "sonuc_metni"
    ],
    "anahtar": [
        "anahtar", "anahtar_kelimeler", "etiketler", "keywords", "tags"
    ],
    "baslik": [
        "baslik", "başlık", "hukuki_baslik", "kart_baslik"
    ],
    "hukuki_soru": [
        "hukuki_soru", "soru", "karar_sorusu"
    ],
    "emsal_ilke": [
        "emsal_ilke", "emsal", "ilke", "hukuki_ilke"
    ],
    "mevzuat": [
        "mevzuat", "dayanak", "yasal_dayanak", "ilgili_mevzuat"
    ],
}


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def latest_file(pattern):
    files = glob.glob(pattern)
    return max(files, key=os.path.getmtime) if files else None


def read_jsonl(path, limit=None):
    rows, errors = [], []
    with open(path, "r", encoding="utf-8") as f:
        for no, line in enumerate(f, 1):
            if limit and len(rows) >= limit:
                break
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                errors.append({"line": no, "error": str(e), "raw": line[:300]})
    return rows, errors


def table_columns(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def resolve(cols, aliases):
    lower = {c.lower(): c for c in cols}
    for a in aliases:
        if a.lower() in lower:
            return lower[a.lower()]
    return None


def count_nonempty_db(cur, col):
    if not col:
        return 0
    cur.execute(f"""
        SELECT COUNT(*)
        FROM hukuki_kartlar
        WHERE COALESCE(aktif,1)=1
          AND {col} IS NOT NULL
          AND TRIM({col}) <> ''
    """)
    return cur.fetchone()[0]


def count_nonempty_export(rows, aliases):
    count = 0
    example_keys = set()
    for r in rows:
        for k in r.keys():
            example_keys.add(k)
        found = False
        for a in aliases:
            if a in r and str(r.get(a) or "").strip():
                found = True
                break
        if found:
            count += 1
    return count, sorted(example_keys)


def main():
    print("=" * 80)
    print("165A - WEB ALAN KAYNAK TESPİT")
    print("=" * 80)

    t = tag()

    web_path = latest_file(WEB_PATTERN)
    if not web_path:
        raise FileNotFoundError("Web export JSONL bulunamadı.")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cols = table_columns(cur, "hukuki_kartlar")

    cur.execute("SELECT COUNT(*) FROM hukuki_kartlar WHERE COALESCE(aktif,1)=1")
    active_count = cur.fetchone()[0]

    db_results = {}
    for logical, aliases in FIELD_ALIASES.items():
        col = resolve(cols, aliases)
        db_results[logical] = {
            "db_column": col,
            "db_nonempty": count_nonempty_db(cur, col),
        }

    web_rows, web_errors = read_jsonl(web_path)
    sample_rows, _ = read_jsonl(web_path, limit=5)

    export_results = {}
    export_keys = set()

    for logical, aliases in FIELD_ALIASES.items():
        count, keys = count_nonempty_export(web_rows, aliases)
        export_results[logical] = {
            "export_nonempty": count,
            "aliases_checked": aliases,
        }
        export_keys.update(keys)

    con.close()

    diagnosis = []

    for logical in ["konu_ozeti", "anahtar"]:
        db_col = db_results[logical]["db_column"]
        db_non = db_results[logical]["db_nonempty"]
        ex_non = export_results[logical]["export_nonempty"]

        if db_col and db_non > 0 and ex_non == 0:
            diagnosis.append(f"{logical}: DB'de var ama export'a aktarılmıyor. 151 export güncellenmeli.")
        elif (not db_col or db_non == 0) and ex_non == 0:
            diagnosis.append(f"{logical}: DB'de de export'ta da yok. 158 üretim formatı / DB şeması revizyonu gerekir.")
        elif ex_non > 0:
            diagnosis.append(f"{logical}: export'ta mevcut.")
        else:
            diagnosis.append(f"{logical}: belirsiz durum.")

    state = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "db_path": DB_PATH,
        "web_path": web_path,
        "active_count": active_count,
        "db_columns": cols,
        "db_results": db_results,
        "export_results": export_results,
        "export_keys": sorted(export_keys),
        "web_errors": len(web_errors),
        "diagnosis": diagnosis,
    }

    state_path = os.path.join(STATE_DIR, f"165A_web_alan_kaynak_tespit_state_{t}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"165A_web_alan_kaynak_tespit_raporu_{t}.txt")

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("165A - WEB ALAN KAYNAK TESPİT RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                 : {DB_PATH}\n")
        f.write(f"Web JSONL           : {web_path}\n")
        f.write(f"Aktif kart          : {active_count}\n")
        f.write(f"Web JSON hata       : {len(web_errors)}\n\n")

        f.write("DB KOLONLARI\n")
        f.write("-" * 80 + "\n")
        f.write(", ".join(cols) + "\n\n")

        f.write("DB ALAN DOLULUK\n")
        f.write("-" * 80 + "\n")
        for logical, info in db_results.items():
            f.write(f"{logical:20} | kolon={str(info['db_column']):25} | dolu={info['db_nonempty']}\n")

        f.write("\nEXPORT ALAN DOLULUK\n")
        f.write("-" * 80 + "\n")
        for logical, info in export_results.items():
            f.write(f"{logical:20} | dolu={info['export_nonempty']}\n")

        f.write("\nEXPORT ANAHTARLARI\n")
        f.write("-" * 80 + "\n")
        f.write(", ".join(sorted(export_keys)) + "\n\n")

        f.write("İLK 5 EXPORT ÖRNEĞİ\n")
        f.write("-" * 80 + "\n")
        for i, r in enumerate(sample_rows, 1):
            f.write(f"\n--- ÖRNEK {i} ---\n")
            f.write(json.dumps(r, ensure_ascii=False, indent=2)[:3000] + "\n")

        f.write("\nTEŞHİS\n")
        f.write("-" * 80 + "\n")
        for d in diagnosis:
            f.write(f"- {d}\n")

        f.write("\nSONUÇ\n")
        f.write("-" * 80 + "\n")
        if any("158 üretim formatı" in d for d in diagnosis):
            f.write("✗ Hedef 1 WEB için gerekli bazı alanlar üretim şemasında eksik görünüyor.\n")
            f.write("Önce 158 üretim formatı ve DB şeması konu özeti / anahtar alanları bakımından revize edilmeli.\n")
        elif any("151 export" in d for d in diagnosis):
            f.write("! Alanlar DB'de var ancak export'a aktarılmıyor. 151 export motoru revize edilmeli.\n")
        else:
            f.write("✓ Alan kaynakları temel olarak uygun görünüyor.\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"State JSON          : {state_path}\n")
        f.write(f"Rapor               : {rapor_path}\n")

    print("\n165A WEB ALAN KAYNAK TESPİT TAMAMLANDI")
    print("-" * 80)
    print(f"Aktif kart     : {active_count}")
    print(f"Web JSONL      : {web_path}")
    print("\nTeşhis:")
    for d in diagnosis:
        print("-", d)
    print("\nDosya:")
    print(rapor_path)


if __name__ == "__main__":
    main()