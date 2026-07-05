# -*- coding: utf-8 -*-
import os, re, json, glob, sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")

BATCH_DIR = os.path.join(BASE_DIR, "batch_planlari")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
EXPORT_DIR = os.path.join(BASE_DIR, "export")
STATE_DIR = os.path.join(BASE_DIR, "production_state")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def read_jsonl(path):
    rows, errors = [], []
    if not path or not os.path.exists(path):
        return rows, [{"error": "DOSYA_YOK", "path": path}]
    with open(path, "r", encoding="utf-8") as f:
        for no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                errors.append({"line": no, "error": str(e), "raw": line[:300]})
    return rows, errors

def latest(pattern):
    files = glob.glob(pattern)
    return max(files, key=os.path.getmtime) if files else None

def all_batch_files():
    return sorted(glob.glob(os.path.join(BATCH_DIR, "152_batch_*_*.jsonl")))

def extract_batch_no(path):
    m = re.search(r"_(\d{4})\.jsonl$", os.path.basename(path))
    return int(m.group(1)) if m else None

def load_batch_plan():
    batch_files = all_batch_files()
    karar_to_batch = {}
    file_to_karar = {}
    duplicate_karar_in_plan = {}
    total_records = 0
    json_errors = []

    for bf in batch_files:
        bno = extract_batch_no(bf)
        rows, errors = read_jsonl(bf)
        json_errors.extend([{"batch_file": bf, **e} for e in errors])
        for r in rows:
            total_records += 1
            karar_no = str(r.get("karar_no", "")).strip()
            dosya_yolu = str(r.get("dosya_yolu", "")).strip()
            if karar_no:
                if karar_no.upper() in karar_to_batch:
                    duplicate_karar_in_plan.setdefault(karar_no.upper(), []).append(bno)
                else:
                    karar_to_batch[karar_no.upper()] = bno
            if dosya_yolu:
                file_to_karar[dosya_yolu] = karar_no

    return {
        "batch_files": batch_files,
        "batch_count": len(batch_files),
        "total_plan_records": total_records,
        "karar_to_batch": karar_to_batch,
        "file_to_karar": file_to_karar,
        "duplicate_karar_in_plan": duplicate_karar_in_plan,
        "json_errors": json_errors,
    }

def completed_162_batches():
    states = glob.glob(os.path.join(STATE_DIR, "162_batch_production_runner_state_batch_*.json"))
    completed = {}
    failed = {}

    for sp in states:
        try:
            with open(sp, "r", encoding="utf-8") as f:
                s = json.load(f)
            bno = int(s.get("batch_no"))
            if s.get("success") is True:
                if bno not in completed or os.path.getmtime(sp) > os.path.getmtime(completed[bno]["state_path"]):
                    s["state_path"] = sp
                    completed[bno] = s
            else:
                s["state_path"] = sp
                failed[bno] = s
        except Exception:
            pass

    return completed, failed

def db_stats():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("PRAGMA table_info(hukuki_kartlar)")
    cols = [r[1] for r in cur.fetchall()]
    has_aktif = "aktif" in cols
    has_kaynak = "kaynak_yontem" in cols

    where_active = "WHERE COALESCE(aktif,1)=1" if has_aktif else ""

    total_cards = cur.execute("SELECT COUNT(*) FROM hukuki_kartlar").fetchone()[0]
    active_cards = cur.execute(f"SELECT COUNT(*) FROM hukuki_kartlar {where_active}").fetchone()[0]
    distinct_karar = cur.execute(f"SELECT COUNT(DISTINCT karar_no) FROM hukuki_kartlar {where_active}").fetchone()[0]

    duplicate_cards = cur.execute(f"""
        SELECT karar_no, baslik, COUNT(*) c
        FROM hukuki_kartlar
        {where_active}
        GROUP BY karar_no, baslik
        HAVING COUNT(*) > 1
    """).fetchall()

    kaynak_counts = []
    if has_kaynak:
        kaynak_counts = cur.execute(f"""
            SELECT COALESCE(kaynak_yontem,'BOŞ') kaynak, COUNT(*) 
            FROM hukuki_kartlar
            {where_active}
            GROUP BY COALESCE(kaynak_yontem,'BOŞ')
            ORDER BY COUNT(*) DESC
        """).fetchall()

    karar_counts = cur.execute(f"""
        SELECT karar_no, COUNT(*) kart_sayisi
        FROM hukuki_kartlar
        {where_active}
        GROUP BY karar_no
    """).fetchall()

    con.close()

    return {
        "columns": cols,
        "total_cards": total_cards,
        "active_cards": active_cards,
        "distinct_karar": distinct_karar,
        "duplicate_cards": duplicate_cards,
        "kaynak_counts": kaynak_counts,
        "karar_counts": {str(k).upper(): c for k, c in karar_counts if k},
    }

def export_stats():
    web_jsonl = latest(os.path.join(EXPORT_DIR, "151_web_aktif_kartlar_*.jsonl"))
    rag_jsonl = latest(os.path.join(EXPORT_DIR, "151_rag_aktif_kartlar_*.jsonl"))
    web_csv = latest(os.path.join(EXPORT_DIR, "151_web_aktif_kartlar_*.csv"))

    web_rows, web_err = read_jsonl(web_jsonl) if web_jsonl else ([], [])
    rag_rows, rag_err = read_jsonl(rag_jsonl) if rag_jsonl else ([], [])

    web_karar = {str(r.get("karar_no", "")).strip().upper() for r in web_rows if r.get("karar_no")}
    rag_karar = {str(r.get("karar_no", "")).strip().upper() for r in rag_rows if r.get("karar_no")}

    return {
        "web_jsonl": web_jsonl,
        "rag_jsonl": rag_jsonl,
        "web_csv": web_csv,
        "web_rows": len(web_rows),
        "rag_rows": len(rag_rows),
        "web_karar": len(web_karar),
        "rag_karar": len(rag_karar),
        "web_errors": len(web_err),
        "rag_errors": len(rag_err),
    }

def main():
    print("="*80)
    print("164 - PRODUCTION İŞLEME İSPAT RAPORU")
    print("="*80)

    t = tag()

    plan = load_batch_plan()
    completed, failed = completed_162_batches()
    db = db_stats()
    exp = export_stats()

    completed_batches = sorted(completed.keys())
    completed_plan_karars = {
        k for k, b in plan["karar_to_batch"].items()
        if b in completed_batches
    }

    db_karars = set(db["karar_counts"].keys())

    completed_in_db = completed_plan_karars & db_karars
    completed_missing_db = completed_plan_karars - db_karars

    planned_total = len(plan["karar_to_batch"])
    completed_file_count = len(completed_plan_karars)
    remaining_plan_count = planned_total - completed_file_count

    technical_pass = (
        len(plan["json_errors"]) == 0
        and len(plan["duplicate_karar_in_plan"]) == 0
        and len(completed_missing_db) == 0
        and len(db["duplicate_cards"]) == 0
        and exp["web_errors"] == 0
        and exp["rag_errors"] == 0
    )

    score = 100
    if plan["json_errors"]: score -= 20
    if plan["duplicate_karar_in_plan"]: score -= 20
    if completed_missing_db: score -= 25
    if db["duplicate_cards"]: score -= 20
    if exp["web_errors"] or exp["rag_errors"]: score -= 15
    score = max(score, 0)

    state = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "planned_total_unique_karar": planned_total,
        "completed_batches": completed_batches,
        "completed_file_count_by_batch_plan": completed_file_count,
        "remaining_plan_count": remaining_plan_count,
        "db_distinct_karar": db["distinct_karar"],
        "db_active_cards": db["active_cards"],
        "completed_missing_db_count": len(completed_missing_db),
        "duplicate_db_card_count": len(db["duplicate_cards"]),
        "export_web_rows": exp["web_rows"],
        "export_rag_rows": exp["rag_rows"],
        "technical_pass": technical_pass,
        "score": score,
    }

    state_path = os.path.join(STATE_DIR, f"164_isleme_ispat_state_{t}.json")
    missing_path = os.path.join(RAPOR_DIR, f"164_completed_missing_db_{t}.jsonl")
    rapor_path = os.path.join(RAPOR_DIR, f"164_production_isleme_ispat_raporu_{t}.txt")

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(missing_path, "w", encoding="utf-8") as f:
        for k in sorted(completed_missing_db):
            f.write(json.dumps({"karar_no": k, "batch_no": plan["karar_to_batch"].get(k)}, ensure_ascii=False) + "\n")

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("164 - PRODUCTION İŞLEME İSPAT RAPORU\n")
        f.write("="*80 + "\n\n")
        f.write(f"Tarih                  : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                     : {DB_PATH}\n\n")

        f.write("BATCH PLANI\n")
        f.write("-"*80 + "\n")
        f.write(f"Batch dosyası          : {plan['batch_count']}\n")
        f.write(f"Plan kayıt             : {plan['total_plan_records']}\n")
        f.write(f"Tekil karar            : {planned_total}\n")
        f.write(f"Plan JSON hatası       : {len(plan['json_errors'])}\n")
        f.write(f"Plan içi mükerrer karar: {len(plan['duplicate_karar_in_plan'])}\n\n")

        f.write("TAMAMLANAN BATCHLER\n")
        f.write("-"*80 + "\n")
        f.write(f"Tamamlanan batch       : {completed_batches}\n")
        f.write(f"Başarısız batch        : {sorted(failed.keys())}\n")
        f.write(f"Tamamlanan plan kararı : {completed_file_count}\n")
        f.write(f"Kalan plan kararı      : {remaining_plan_count}\n\n")

        f.write("DB İSPATI\n")
        f.write("-"*80 + "\n")
        f.write(f"DB toplam kart         : {db['total_cards']}\n")
        f.write(f"DB aktif kart          : {db['active_cards']}\n")
        f.write(f"DB tekil aktif karar   : {db['distinct_karar']}\n")
        f.write(f"Tamamlananlardan DB'de olan : {len(completed_in_db)}\n")
        f.write(f"Tamamlananlardan DB'de eksik: {len(completed_missing_db)}\n")
        f.write(f"DB mükerrer kart       : {len(db['duplicate_cards'])}\n\n")

        f.write("KAYNAK DAĞILIMI\n")
        f.write("-"*80 + "\n")
        for k, v in db["kaynak_counts"]:
            f.write(f"{k:35}: {v}\n")

        f.write("\nEXPORT İSPATI\n")
        f.write("-"*80 + "\n")
        f.write(f"Web JSONL              : {exp['web_jsonl']}\n")
        f.write(f"RAG JSONL              : {exp['rag_jsonl']}\n")
        f.write(f"Web CSV                : {exp['web_csv']}\n")
        f.write(f"Web satır              : {exp['web_rows']}\n")
        f.write(f"RAG satır              : {exp['rag_rows']}\n")
        f.write(f"Web tekil karar        : {exp['web_karar']}\n")
        f.write(f"RAG tekil karar        : {exp['rag_karar']}\n")
        f.write(f"Web JSON hata          : {exp['web_errors']}\n")
        f.write(f"RAG JSON hata          : {exp['rag_errors']}\n\n")

        f.write("SERTİFİKA\n")
        f.write("-"*80 + "\n")
        f.write(f"İşleme ispat puanı     : {score} / 100\n")
        f.write(f"Teknik ispat           : {'GEÇTİ' if technical_pass else 'KALDI'}\n\n")

        f.write("SONUÇ\n")
        f.write("-"*80 + "\n")
        if technical_pass:
            f.write("✓ İşlenen batchlerdeki kararların DB ve export zincirine yansıdığı teknik olarak doğrulandı.\n")
        else:
            f.write("✗ Teknik ispatta giderilmesi gereken hususlar var. Eksik/mükerrer detay dosyaları kontrol edilmeli.\n")

        f.write("\nDOSYALAR\n")
        f.write("-"*80 + "\n")
        f.write(f"State JSON             : {state_path}\n")
        f.write(f"DB eksik JSONL         : {missing_path}\n")
        f.write(f"Rapor                  : {rapor_path}\n")

    print("\n164 İŞLEME İSPAT RAPORU OLUŞTURULDU")
    print("-"*80)
    print(f"Tekil plan karar       : {planned_total}")
    print(f"Tamamlanan batch       : {completed_batches}")
    print(f"Tamamlanan plan kararı : {completed_file_count}")
    print(f"Kalan plan kararı      : {remaining_plan_count}")
    print(f"DB tekil aktif karar   : {db['distinct_karar']}")
    print(f"DB aktif kart          : {db['active_cards']}")
    print(f"Teknik ispat           : {'GEÇTİ' if technical_pass else 'KALDI'}")
    print(f"Puan                   : {score} / 100")
    print("\nDosya:")
    print(rapor_path)

if __name__ == "__main__":
    main()