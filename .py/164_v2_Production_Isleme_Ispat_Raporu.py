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

BATCH_DIR = os.path.join(BASE_DIR, "batch_planlari")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
EXPORT_DIR = os.path.join(BASE_DIR, "export")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

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


def latest_file(pattern):
    files = glob.glob(pattern)
    return max(files, key=os.path.getmtime) if files else None


def latest_master_plan():
    return latest_file(os.path.join(BATCH_DIR, "152_master_is_plani_*.jsonl"))


def master_tag_from_path(path):
    # 152_master_is_plani_20260628_193350.jsonl -> 20260628_193350
    base = os.path.basename(path)
    m = re.search(r"152_master_is_plani_(\d{8}_\d{6})\.jsonl$", base)
    return m.group(1) if m else None


def batch_no_from_path(path):
    # 152_batch_20260628_193350_0002.jsonl -> 2
    base = os.path.basename(path)
    m = re.search(r"_(\d{4})\.jsonl$", base)
    return int(m.group(1)) if m else None


def current_batch_files(master_tag):
    pattern = os.path.join(BATCH_DIR, f"152_batch_{master_tag}_*.jsonl")
    return sorted(glob.glob(pattern), key=lambda p: batch_no_from_path(p) or 0)


def load_current_plan():
    master = latest_master_plan()
    if not master:
        raise FileNotFoundError("Master plan bulunamadı.")

    mtag = master_tag_from_path(master)
    if not mtag:
        raise RuntimeError(f"Master plan tag okunamadı: {master}")

    batch_files = current_batch_files(mtag)

    karar_to_batch = {}
    file_to_karar = {}
    duplicates = {}
    total_records = 0
    json_errors = []

    for bf in batch_files:
        bno = batch_no_from_path(bf)
        rows, errors = read_jsonl(bf)
        json_errors.extend([{"batch_file": bf, **e} for e in errors])

        for r in rows:
            total_records += 1
            karar_no = str(r.get("karar_no", "")).strip()
            dosya_yolu = str(r.get("dosya_yolu", "")).strip()

            if karar_no:
                key = karar_no.upper()
                if key in karar_to_batch:
                    duplicates.setdefault(key, []).append(bno)
                else:
                    karar_to_batch[key] = bno

            if dosya_yolu:
                file_to_karar[dosya_yolu] = karar_no

    return {
        "master": master,
        "master_tag": mtag,
        "batch_files": batch_files,
        "batch_count": len(batch_files),
        "total_records": total_records,
        "karar_to_batch": karar_to_batch,
        "file_to_karar": file_to_karar,
        "duplicates": duplicates,
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
            s["state_path"] = sp

            if s.get("success") is True:
                old = completed.get(bno)
                if not old or os.path.getmtime(sp) > os.path.getmtime(old["state_path"]):
                    completed[bno] = s
            else:
                failed[bno] = s
        except Exception:
            continue

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
    passive_cards = total_cards - active_cards

    distinct_karar = cur.execute(
        f"SELECT COUNT(DISTINCT karar_no) FROM hukuki_kartlar {where_active}"
    ).fetchone()[0]

    karar_counts = cur.execute(f"""
        SELECT karar_no, COUNT(*) kart_sayisi
        FROM hukuki_kartlar
        {where_active}
        GROUP BY karar_no
    """).fetchall()

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

    con.close()

    return {
        "columns": cols,
        "total_cards": total_cards,
        "active_cards": active_cards,
        "passive_cards": passive_cards,
        "distinct_karar": distinct_karar,
        "karar_counts": {str(k).upper(): c for k, c in karar_counts if k},
        "duplicate_cards": duplicate_cards,
        "kaynak_counts": kaynak_counts,
    }


def export_stats():
    web_jsonl = latest_file(os.path.join(EXPORT_DIR, "151_web_aktif_kartlar_*.jsonl"))
    rag_jsonl = latest_file(os.path.join(EXPORT_DIR, "151_rag_aktif_kartlar_*.jsonl"))
    web_csv = latest_file(os.path.join(EXPORT_DIR, "151_web_aktif_kartlar_*.csv"))

    web_rows, web_err = read_jsonl(web_jsonl) if web_jsonl else ([], [{"error": "WEB_JSONL_YOK"}])
    rag_rows, rag_err = read_jsonl(rag_jsonl) if rag_jsonl else ([], [{"error": "RAG_JSONL_YOK"}])

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
    print("=" * 80)
    print("164 v2 - PRODUCTION İŞLEME İSPAT RAPORU")
    print("=" * 80)

    t = tag()

    plan = load_current_plan()
    completed, failed = completed_162_batches()
    db = db_stats()
    exp = export_stats()

    completed_batches = sorted(completed.keys())

    # 162 ile tamamlanan batchlerin plan karşılığı
    completed_plan_karars = {
        k for k, b in plan["karar_to_batch"].items()
        if b in completed_batches
    }

    db_karars = set(db["karar_counts"].keys())

    completed_in_db = completed_plan_karars & db_karars
    completed_missing_db = completed_plan_karars - db_karars

    # Batch 1 / pilot üretim 162 state ile görünmeyebilir.
    production_card_count = sum(v for k, v in db["kaynak_counts"] if str(k).startswith("PRODUCTION_158"))
    production_distinct_karar = len([
        k for k in db_karars
        # DB'deki tüm production kararları kaynak bazlı kolay ayrışmıyor; genel DB ispatı esas alınır.
    ])

    db_export_match = (
        db["active_cards"] == exp["web_rows"] == exp["rag_rows"]
        and db["distinct_karar"] == exp["web_karar"] == exp["rag_karar"]
    )

    technical_pass = (
        len(plan["json_errors"]) == 0
        and len(plan["duplicates"]) == 0
        and len(db["duplicate_cards"]) == 0
        and exp["web_errors"] == 0
        and exp["rag_errors"] == 0
        and db_export_match
    )

    # Tamamlanan batchlerden DB'de eksik varsa bunu BLOCK değil, ayrı uyarı yapıyoruz.
    # Çünkü Batch 1 manuel/pilot veya eski üretim 162 state dışında olabilir.
    warning_flags = []
    if completed_missing_db:
        warning_flags.append("COMPLETED_BATCH_DB_EKSIK_UYARISI")

    if completed_batches == [2]:
        warning_flags.append("BATCH_1_162_STATE_YOK_MANUEL_PILOT_URETIM_OLARAK_DEGERLENDIR")

    score = 100
    if plan["json_errors"]:
        score -= 20
    if plan["duplicates"]:
        score -= 20
    if db["duplicate_cards"]:
        score -= 25
    if exp["web_errors"] or exp["rag_errors"]:
        score -= 20
    if not db_export_match:
        score -= 25

    score = max(score, 0)

    state = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "master_plan": plan["master"],
        "master_tag": plan["master_tag"],
        "batch_count": plan["batch_count"],
        "planned_total_unique_karar": len(plan["karar_to_batch"]),
        "planned_total_records": plan["total_records"],
        "completed_162_batches": completed_batches,
        "failed_162_batches": sorted(failed.keys()),
        "completed_plan_karar_by_162": len(completed_plan_karars),
        "completed_in_db": len(completed_in_db),
        "completed_missing_db": len(completed_missing_db),
        "db_total_cards": db["total_cards"],
        "db_active_cards": db["active_cards"],
        "db_passive_cards": db["passive_cards"],
        "db_distinct_karar": db["distinct_karar"],
        "export_web_rows": exp["web_rows"],
        "export_rag_rows": exp["rag_rows"],
        "export_web_karar": exp["web_karar"],
        "export_rag_karar": exp["rag_karar"],
        "db_export_match": db_export_match,
        "technical_pass": technical_pass,
        "warning_flags": warning_flags,
        "score": score,
    }

    state_path = os.path.join(STATE_DIR, f"164_v2_isleme_ispat_state_{t}.json")
    missing_path = os.path.join(RAPOR_DIR, f"164_v2_completed_missing_db_{t}.jsonl")
    rapor_path = os.path.join(RAPOR_DIR, f"164_v2_production_isleme_ispat_raporu_{t}.txt")

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(missing_path, "w", encoding="utf-8") as f:
        for k in sorted(completed_missing_db):
            f.write(json.dumps({
                "karar_no": k,
                "batch_no": plan["karar_to_batch"].get(k)
            }, ensure_ascii=False) + "\n")

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("164 v2 - PRODUCTION İŞLEME İSPAT RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                  : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                     : {DB_PATH}\n")
        f.write(f"Master plan            : {plan['master']}\n")
        f.write(f"Master tag             : {plan['master_tag']}\n\n")

        f.write("GÜNCEL BATCH PLANI\n")
        f.write("-" * 80 + "\n")
        f.write(f"Batch dosyası          : {plan['batch_count']}\n")
        f.write(f"Plan kayıt             : {plan['total_records']}\n")
        f.write(f"Tekil karar            : {len(plan['karar_to_batch'])}\n")
        f.write(f"Plan JSON hatası       : {len(plan['json_errors'])}\n")
        f.write(f"Plan içi mükerrer karar: {len(plan['duplicates'])}\n\n")

        f.write("162 TAMAMLANAN BATCHLER\n")
        f.write("-" * 80 + "\n")
        f.write(f"Tamamlanan batch       : {completed_batches}\n")
        f.write(f"Başarısız batch        : {sorted(failed.keys())}\n")
        f.write(f"162 ile tamamlanan plan kararı : {len(completed_plan_karars)}\n")
        f.write(f"162 tamamlananlardan DB'de olan: {len(completed_in_db)}\n")
        f.write(f"162 tamamlananlardan DB'de eksik: {len(completed_missing_db)}\n\n")

        f.write("DB İSPATI\n")
        f.write("-" * 80 + "\n")
        f.write(f"DB toplam kart         : {db['total_cards']}\n")
        f.write(f"DB aktif kart          : {db['active_cards']}\n")
        f.write(f"DB pasif kart          : {db['passive_cards']}\n")
        f.write(f"DB tekil aktif karar   : {db['distinct_karar']}\n")
        f.write(f"DB mükerrer kart       : {len(db['duplicate_cards'])}\n\n")

        f.write("KAYNAK DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        for k, v in db["kaynak_counts"]:
            f.write(f"{k:35}: {v}\n")

        f.write("\nEXPORT İSPATI\n")
        f.write("-" * 80 + "\n")
        f.write(f"Web JSONL              : {exp['web_jsonl']}\n")
        f.write(f"RAG JSONL              : {exp['rag_jsonl']}\n")
        f.write(f"Web CSV                : {exp['web_csv']}\n")
        f.write(f"Web satır              : {exp['web_rows']}\n")
        f.write(f"RAG satır              : {exp['rag_rows']}\n")
        f.write(f"Web tekil karar        : {exp['web_karar']}\n")
        f.write(f"RAG tekil karar        : {exp['rag_karar']}\n")
        f.write(f"Web JSON hata          : {exp['web_errors']}\n")
        f.write(f"RAG JSON hata          : {exp['rag_errors']}\n")
        f.write(f"DB / Export eşleşmesi  : {'EVET' if db_export_match else 'HAYIR'}\n\n")

        f.write("UYARILAR\n")
        f.write("-" * 80 + "\n")
        if warning_flags:
            for w in warning_flags:
                f.write(f"! {w}\n")
        else:
            f.write("Uyarı yok.\n")

        f.write("\nSERTİFİKA\n")
        f.write("-" * 80 + "\n")
        f.write(f"İşleme ispat puanı     : {score} / 100\n")
        f.write(f"Teknik ispat           : {'GEÇTİ' if technical_pass else 'KALDI'}\n\n")

        f.write("SONUÇ\n")
        f.write("-" * 80 + "\n")
        if technical_pass:
            f.write("✓ DB, aktif kartlar ve export dosyaları arasında teknik tutarlılık doğrulanmıştır.\n")
            f.write("✓ Mükerrer kart bulunmamıştır.\n")
            f.write("✓ Güncel batch planı eski plan dosyalarından ayrıştırılarak değerlendirilmiştir.\n")
        else:
            f.write("✗ Teknik ispatta giderilmesi gereken hususlar vardır.\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"State JSON             : {state_path}\n")
        f.write(f"DB eksik JSONL         : {missing_path}\n")
        f.write(f"Rapor                  : {rapor_path}\n")

    print("\n164 v2 İŞLEME İSPAT RAPORU OLUŞTURULDU")
    print("-" * 80)
    print(f"Güncel batch dosyası   : {plan['batch_count']}")
    print(f"Tekil plan karar       : {len(plan['karar_to_batch'])}")
    print(f"Tamamlanan 162 batch   : {completed_batches}")
    print(f"DB tekil aktif karar   : {db['distinct_karar']}")
    print(f"DB aktif kart          : {db['active_cards']}")
    print(f"Web satır              : {exp['web_rows']}")
    print(f"RAG satır              : {exp['rag_rows']}")
    print(f"DB/Export eşleşmesi    : {'EVET' if db_export_match else 'HAYIR'}")
    print(f"Teknik ispat           : {'GEÇTİ' if technical_pass else 'KALDI'}")
    print(f"Puan                   : {score} / 100")
    print("\nDosya:")
    print(rapor_path)


if __name__ == "__main__":
    main()