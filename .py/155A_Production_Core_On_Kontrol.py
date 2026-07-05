# -*- coding: utf-8 -*-
import os
import glob
import json
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")
PILOT_DIR = os.path.join(BASE_DIR, "pilot_uretim")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

REQUIRED_SCRIPTS = [
    "136E_Batch_Guvenli_Sadeleme_Motoru.py",
    "137_Batch_Guvenli_Kartlari_DB_Yukleme_Motoru.py",
    "139_Batch_Kart_Validator_Motoru.py",
    "146_Aktif_Kart_Son_Kalite_Raporu.py",
    "151_Aktif_Kart_RAG_Web_Export_Motoru.py",
]

PILOT_PATTERN = os.path.join(PILOT_DIR, "154_pilot_batch_*.jsonl")


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def read_jsonl(path):
    rows = []
    if not path or not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                rows.append({
                    "_json_error": str(e),
                    "_line_no": line_no,
                    "_raw": line[:300],
                })
    return rows


def db_check():
    if not os.path.exists(DB_PATH):
        return {
            "db_var": False,
            "hukuki_kartlar_var": False,
            "kart_sayisi": 0,
        }

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hukuki_kartlar'")
        table_exists = cur.fetchone() is not None
    except Exception:
        table_exists = False

    kart_sayisi = 0
    if table_exists:
        try:
            kart_sayisi = cur.execute("SELECT COUNT(*) FROM hukuki_kartlar").fetchone()[0]
        except Exception:
            kart_sayisi = 0

    con.close()

    return {
        "db_var": True,
        "hukuki_kartlar_var": table_exists,
        "kart_sayisi": kart_sayisi,
    }


def main():
    print("=" * 80)
    print("155A - PRODUCTION CORE ÖN KONTROL")
    print("=" * 80)

    t = tag()

    pilot_path = latest_file(PILOT_PATTERN)
    pilot_rows = read_jsonl(pilot_path) if pilot_path else []

    script_results = []
    missing_scripts = []

    for script in REQUIRED_SCRIPTS:
        path = os.path.join(PY_DIR, script)
        exists = os.path.exists(path)
        script_results.append({
            "script": script,
            "path": path,
            "exists": exists,
        })
        if not exists:
            missing_scripts.append(script)

    json_errors = [r for r in pilot_rows if "_json_error" in r]
    clean_rows = [r for r in pilot_rows if "_json_error" not in r]

    dosya_yok = []
    karar_no_yok = []

    for r in clean_rows:
        if not os.path.exists(str(r.get("dosya_yolu", ""))):
            dosya_yok.append(r)
        if not str(r.get("karar_no", "")).strip():
            karar_no_yok.append(r)

    db = db_check()

    production_ready = (
        pilot_path is not None
        and len(clean_rows) > 0
        and len(json_errors) == 0
        and len(dosya_yok) == 0
        and len(karar_no_yok) == 0
        and db["db_var"]
        and db["hukuki_kartlar_var"]
    )

    state = {
        "run_id": t,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pilot_path": pilot_path,
        "pilot_count": len(clean_rows),
        "db_path": DB_PATH,
        "db_kart_sayisi": db["kart_sayisi"],
        "production_ready": production_ready,
        "missing_scripts": missing_scripts,
        "next_step": "155B_Production_Core_Pilot_Runner.py" if production_ready else "EKSIKLERI_GIDER",
    }

    state_path = os.path.join(STATE_DIR, f"155A_production_state_{t}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"155A_production_core_on_kontrol_raporu_{t}.txt")

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("155A - PRODUCTION CORE ÖN KONTROL RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"BASE_DIR           : {BASE_DIR}\n")
        f.write(f"PY_DIR             : {PY_DIR}\n")
        f.write(f"DB                 : {DB_PATH}\n")
        f.write(f"Pilot JSONL         : {pilot_path}\n\n")

        f.write("PİLOT KONTROL\n")
        f.write("-" * 80 + "\n")
        f.write(f"Pilot kayıt         : {len(clean_rows)}\n")
        f.write(f"JSON hata           : {len(json_errors)}\n")
        f.write(f"Dosya yok           : {len(dosya_yok)}\n")
        f.write(f"Karar no yok        : {len(karar_no_yok)}\n\n")

        f.write("DB KONTROL\n")
        f.write("-" * 80 + "\n")
        f.write(f"DB var              : {db['db_var']}\n")
        f.write(f"hukuki_kartlar var  : {db['hukuki_kartlar_var']}\n")
        f.write(f"DB kart sayısı      : {db['kart_sayisi']}\n\n")

        f.write("SCRIPT KONTROL\n")
        f.write("-" * 80 + "\n")
        for s in script_results:
            f.write(f"{'VAR' if s['exists'] else 'YOK'} | {s['script']} | {s['path']}\n")

        f.write("\nSONUÇ\n")
        f.write("-" * 80 + "\n")
        f.write(f"Production Ready    : {'EVET' if production_ready else 'HAYIR'}\n")
        f.write(f"State dosyası       : {state_path}\n")

    print("\nÖN KONTROL TAMAMLANDI")
    print("-" * 80)
    print(f"Pilot kayıt      : {len(clean_rows)}")
    print(f"JSON hata        : {len(json_errors)}")
    print(f"Dosya yok        : {len(dosya_yok)}")
    print(f"Karar no yok     : {len(karar_no_yok)}")
    print(f"DB kart sayısı   : {db['kart_sayisi']}")
    print(f"Eksik script     : {len(missing_scripts)}")
    print(f"Production Ready : {'EVET' if production_ready else 'HAYIR'}")

    print("\nDosyalar:")
    print(rapor_path)
    print(state_path)


if __name__ == "__main__":
    main()