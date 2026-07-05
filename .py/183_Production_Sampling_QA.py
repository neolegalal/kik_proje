# -*- coding: utf-8 -*-
"""
183 - PRODUCTION SAMPLING QA

Amaç:
- Son üretim/export havuzundan örnek kararlar seçer.
- Örnek kararların 168/179 üretim çıktılarını bulur.
- Seçilen örnekler için kalite hakemlerini tekrar çalıştırmaya hazır "sampling package" üretir.
- API kullanmaz.
- DB'ye yazmaz.

Kullanım:
  python ".py\\183_Production_Sampling_QA.py"

Belirli export ile:
  python ".py\\183_Production_Sampling_QA.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\exports\\web_export_170_YYYYMMDD_HHMMSS.jsonl"

Örnek sayısı:
  python ".py\\183_Production_Sampling_QA.py" 10

Belirli export + örnek sayısı:
  python ".py\\183_Production_Sampling_QA.py" "C:\\...\\web_export_170_x.jsonl" 10

Not:
- Varsayılan örnek sayısı: 10
- Yeni model kartları öncelikli örnekler.
- Çıktı olarak karar bazlı örnek JSONL üretir.
- Bu JSONL daha sonra 172/175/177/180 gibi hakemlere gönderilebilir.
"""

import os
import re
import sys
import csv
import json
import glob
import random
import sqlite3
from datetime import datetime
from collections import defaultdict, Counter


BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")

EXPORT_DIR = os.path.join(BASE_DIR, "exports")
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
SAMPLE_DIR = os.path.join(BASE_DIR, "sampling")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

WEB_JSONL_PATTERN = os.path.join(EXPORT_DIR, "web_export_170_*.jsonl")
WEB_CSV_PATTERN = os.path.join(EXPORT_DIR, "web_export_170_*.csv")
PRODUCTION_OUTPUT_PATTERNS = [
    os.path.join(URETIM_OUTPUT_DIR, "179_optimized_production_output_*.jsonl"),
    os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl"),
]

TABLE_NAME = "hukuki_kartlar"

os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(RAPOR_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def latest_file(pattern):
    files = glob.glob(pattern)
    return max(files, key=os.path.getmtime) if files else None


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def safe(v):
    return "" if v is None else str(v).strip()


def parse_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    s = str(v).strip()
    if not s:
        return []
    try:
        obj = json.loads(s)
        if isinstance(obj, list):
            return [str(x).strip() for x in obj if str(x).strip()]
    except Exception:
        pass
    if s.startswith("[") and s.endswith("]"):
        try:
            import ast
            obj = ast.literal_eval(s)
            if isinstance(obj, list):
                return [str(x).strip() for x in obj if str(x).strip()]
        except Exception:
            pass
    return [p.strip(" -•\t\r\n") for p in re.split(r"[,;]\s*", s) if p.strip(" -•\t\r\n")]


def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                rows.append({"_json_error": True, "_line_no": line_no, "_raw": line[:300]})
    return rows


def read_csv(path):
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def read_db():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"DB bulunamadı: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cols = [r[1] for r in cur.execute(f"PRAGMA table_info({TABLE_NAME})").fetchall()]
    if "aktif" in cols:
        where = "WHERE COALESCE(aktif, 1) = 1"
    elif "is_active" in cols:
        where = "WHERE COALESCE(is_active, 1) = 1"
    else:
        where = ""

    rows = [dict(r) for r in cur.execute(f"SELECT * FROM {TABLE_NAME} {where}").fetchall()]
    conn.close()
    return rows


def standardize_card(row):
    karar_no = safe(row.get("karar_no") or row.get("kararNo") or row.get("karar"))
    baslik = safe(row.get("baslik") or row.get("başlık"))
    hukuki_soru = safe(row.get("hukuki_soru") or row.get("hukukiSoru"))
    konu_ozeti = safe(row.get("konu_ozeti") or row.get("konuOzeti"))
    sonuc_ozeti = safe(row.get("sonuc_ozeti") or row.get("sonucOzeti") or row.get("sonuc"))
    sonuc_tipi = safe(row.get("sonuc_tipi") or row.get("sonucTipi"))
    emsal_ilke = safe(row.get("emsal_ilke") or row.get("emsalIlke"))
    guven = safe(row.get("guven") or row.get("güven"))
    mevzuat = parse_list(row.get("mevzuat"))
    anahtar = parse_list(row.get("anahtar") or row.get("anahtarlar"))

    return {
        "karar_no": karar_no,
        "baslik": baslik,
        "hukuki_soru": hukuki_soru,
        "konu_ozeti": konu_ozeti,
        "sonuc_ozeti": sonuc_ozeti,
        "sonuc_tipi": sonuc_tipi,
        "emsal_ilke": emsal_ilke,
        "mevzuat": mevzuat,
        "anahtar": anahtar,
        "guven": guven,
        "is_new_model": bool(konu_ozeti and anahtar),
    }


def resolve_args():
    input_path = None
    sample_n = 10
    use_db = False

    for arg in sys.argv[1:]:
        if arg == "--db":
            use_db = True
        elif os.path.exists(arg):
            input_path = arg
        else:
            try:
                sample_n = max(1, int(arg))
            except Exception:
                pass

    if use_db:
        return "DB", DB_PATH, sample_n

    if input_path:
        ext = os.path.splitext(input_path)[1].lower()
        if ext == ".jsonl":
            return "JSONL", input_path, sample_n
        if ext == ".csv":
            return "CSV", input_path, sample_n
        raise RuntimeError("Desteklenmeyen input uzantısı.")

    latest_jsonl = latest_file(WEB_JSONL_PATTERN)
    if latest_jsonl:
        return "JSONL", latest_jsonl, sample_n

    latest_csv = latest_file(WEB_CSV_PATTERN)
    if latest_csv:
        return "CSV", latest_csv, sample_n

    return "DB", DB_PATH, sample_n


def load_cards(source_type, input_path):
    if source_type == "JSONL":
        rows = read_jsonl(input_path)
    elif source_type == "CSV":
        rows = read_csv(input_path)
    elif source_type == "DB":
        rows = read_db()
    else:
        raise RuntimeError(f"Bilinmeyen kaynak: {source_type}")

    cards = []
    errors = 0
    for r in rows:
        if isinstance(r, dict) and r.get("_json_error"):
            errors += 1
            continue
        cards.append(standardize_card(r))
    return cards, errors


def group_by_decision(cards):
    grouped = defaultdict(list)
    for c in cards:
        if c["karar_no"]:
            grouped[c["karar_no"]].append(c)
    return dict(grouped)


def score_decision_for_sampling(karar_no, cards):
    # Yeni model, çok kartlı kararlar, boş mevzuatlı kartlar ve düşük güvenli kartlar öncelikli.
    score = 0
    new_count = sum(1 for c in cards if c["is_new_model"])
    mevzuat_empty = sum(1 for c in cards if not c["mevzuat"])
    anahtar_empty = sum(1 for c in cards if not c["anahtar"])
    konu_empty = sum(1 for c in cards if not c["konu_ozeti"])

    score += new_count * 10
    score += min(20, len(cards) * 3)
    score += mevzuat_empty * 4
    score += anahtar_empty * 3
    score += konu_empty * 3

    return score


def choose_samples(grouped, sample_n):
    kararlar = list(grouped.keys())

    new_model_decisions = [k for k in kararlar if any(c["is_new_model"] for c in grouped[k])]
    legacy_decisions = [k for k in kararlar if k not in new_model_decisions]

    random.seed(42)

    # Yeni model kararları önceliklendir.
    scored_new = sorted(
        [(score_decision_for_sampling(k, grouped[k]), k) for k in new_model_decisions],
        reverse=True
    )

    selected = []
    for _, k in scored_new:
        if len(selected) >= sample_n:
            break
        selected.append(k)

    # Yeterli değilse rastgele legacy ekle.
    remaining_needed = sample_n - len(selected)
    if remaining_needed > 0 and legacy_decisions:
        selected.extend(random.sample(legacy_decisions, min(remaining_needed, len(legacy_decisions))))

    # Hala boşsa genel havuzdan tamamla.
    if len(selected) < sample_n:
        remaining = [k for k in kararlar if k not in selected]
        selected.extend(random.sample(remaining, min(sample_n - len(selected), len(remaining))))

    return selected[:sample_n]


def find_production_rows_for_decisions(decision_ids):
    decision_set = set(decision_ids)
    found = {}
    source_files = []

    files = []
    for pattern in PRODUCTION_OUTPUT_PATTERNS:
        files.extend(glob.glob(pattern))
    files = sorted(files, key=os.path.getmtime, reverse=True)

    for path in files:
        if len(found) == len(decision_set):
            break

        rows = read_jsonl(path)
        hit_in_file = 0
        for r in rows:
            if r.get("status") != "OK":
                continue
            karar_no = safe(r.get("karar_no") or r.get("orijinal_karar_no"))
            if karar_no in decision_set and karar_no not in found:
                found[karar_no] = dict(r)
                found[karar_no]["_source_output_file"] = path
                hit_in_file += 1

        if hit_in_file:
            source_files.append(path)

    return found, source_files


def create_sampling_package(selected, grouped, production_rows):
    package_rows = []
    missing_production_rows = []

    for karar_no in selected:
        if karar_no in production_rows:
            row = dict(production_rows[karar_no])
            row["sampling_info"] = {
                "selected_at": now(),
                "sampling_reason": "production_sampling_qa",
            }
            package_rows.append(row)
        else:
            # Eğer 168/179 satırı bulunamazsa export kartlarından minimal karar paketi üret.
            cards = grouped.get(karar_no, [])
            package_rows.append({
                "status": "OK",
                "karar_no": karar_no,
                "dosya_adi": "",
                "dosya_yolu": "",
                "kartlar": [
                    {
                        "baslik": c["baslik"],
                        "hukuki_soru": c["hukuki_soru"],
                        "konu_ozeti": c["konu_ozeti"],
                        "sonuc_ozeti": c["sonuc_ozeti"],
                        "sonuc_tipi": c["sonuc_tipi"],
                        "emsal_ilke": c["emsal_ilke"],
                        "mevzuat": c["mevzuat"],
                        "anahtar": c["anahtar"],
                        "guven": c["guven"],
                    }
                    for c in cards
                ],
                "sampling_info": {
                    "selected_at": now(),
                    "sampling_reason": "production_sampling_qa_export_only",
                    "warning": "Orijinal 168/179 üretim satırı bulunamadı; export kartlarından minimal paket oluşturuldu."
                }
            })
            missing_production_rows.append(karar_no)

    return package_rows, missing_production_rows


def main():
    print("=" * 80)
    print("183 - PRODUCTION SAMPLING QA")
    print("=" * 80)

    run_tag = tag()
    source_type, input_path, sample_n = resolve_args()

    print(f"\nKaynak tipi   : {source_type}")
    print(f"Input         : {input_path}")
    print(f"Örnek sayısı  : {sample_n}")
    print("-" * 80)

    cards, errors = load_cards(source_type, input_path)
    grouped = group_by_decision(cards)
    selected = choose_samples(grouped, sample_n)

    production_rows, source_files = find_production_rows_for_decisions(selected)
    package_rows, missing_rows = create_sampling_package(selected, grouped, production_rows)

    sample_path = os.path.join(SAMPLE_DIR, f"183_sampling_package_{run_tag}.jsonl")
    detail_path = os.path.join(LOG_DIR, f"183_sampling_qa_detay_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"183_sampling_qa_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"183_production_sampling_qa_raporu_{run_tag}.txt")

    write_jsonl(sample_path, package_rows)

    for karar_no in selected:
        cards_for_decision = grouped.get(karar_no, [])
        append_jsonl(detail_path, {
            "karar_no": karar_no,
            "kart_sayisi": len(cards_for_decision),
            "new_model_kart": sum(1 for c in cards_for_decision if c["is_new_model"]),
            "sampling_score": score_decision_for_sampling(karar_no, cards_for_decision),
            "production_row_found": karar_no in production_rows,
        })

    ready_for_ai_qa = len(package_rows) > 0 and len(missing_rows) == 0

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "source_type": source_type,
        "input_path": input_path,
        "sample_count_requested": sample_n,
        "sample_count_created": len(package_rows),
        "total_cards": len(cards),
        "total_decisions": len(grouped),
        "json_errors": errors,
        "selected_decisions": selected,
        "production_source_files": source_files,
        "missing_production_rows": missing_rows,
        "sample_package_path": sample_path,
        "detail_path": detail_path,
        "rapor_path": rapor_path,
        "ready_for_ai_qa": ready_for_ai_qa,
        "ready_for_184": True,
        "next_step": "184_Production_Dashboard.py",
        "recommended_commands": {
            "171_structural": f'python ".py\\171_v2_Mini_Uretim_Kalite_Kontrol_Motoru.py" "{sample_path}"',
            "175_coverage": f'python ".py\\175_v2_AI_Hukuki_Mesele_Kapsam_Analiz_Motoru.py" "{sample_path}"',
            "177_legal_accuracy": f'python ".py\\177_Hukuki_Dogruluk_Hakemi.py" "{sample_path}"',
            "180_complexity": f'python ".py\\180_v2_Karar_Karmasiklik_Analiz_Motoru.py" "{sample_path}"',
        }
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("183 - PRODUCTION SAMPLING QA RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Kaynak tipi                   : {source_type}\n")
        f.write(f"Input                         : {input_path}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam karar                   : {len(grouped)}\n")
        f.write(f"Toplam kart                    : {len(cards)}\n")
        f.write(f"İstenen örnek                  : {sample_n}\n")
        f.write(f"Oluşturulan örnek              : {len(package_rows)}\n")
        f.write(f"Production satırı bulunamayan  : {len(missing_rows)}\n")
        f.write(f"AI QA'ya hazır mı              : {'EVET' if ready_for_ai_qa else 'KISMEN'}\n")
        f.write(f"184'e geçilebilir mi           : EVET\n\n")

        f.write("SEÇILEN KARARLAR\n")
        f.write("-" * 80 + "\n")
        for karar_no in selected:
            cards_for_decision = grouped.get(karar_no, [])
            f.write(
                f"{karar_no:<22} | kart={len(cards_for_decision):<3} | "
                f"yeni_model={sum(1 for c in cards_for_decision if c['is_new_model']):<3} | "
                f"production_row={'EVET' if karar_no in production_rows else 'HAYIR'}\n"
            )

        f.write("\nÖNERILEN QA KOMUTLARI\n")
        f.write("-" * 80 + "\n")
        for name, cmd in state["recommended_commands"].items():
            f.write(f"{name}: {cmd}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Sampling package               : {sample_path}\n")
        f.write(f"Detay JSONL                    : {detail_path}\n")
        f.write(f"State JSON                     : {state_path}\n")
        f.write(f"Rapor                          : {rapor_path}\n")

    print("\n183 PRODUCTION SAMPLING QA TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam karar                   : {len(grouped)}")
    print(f"Toplam kart                    : {len(cards)}")
    print(f"Oluşturulan örnek              : {len(package_rows)}")
    print(f"Production satırı bulunamayan  : {len(missing_rows)}")
    print(f"AI QA'ya hazır mı              : {'EVET' if ready_for_ai_qa else 'KISMEN'}")
    print(f"184'e geçilebilir mi           : EVET")

    print("\nSampling package:")
    print(sample_path)

    print("\nÖnerilen QA komutları:")
    for cmd in state["recommended_commands"].values():
        print(cmd)

    print("\nDosyalar:")
    print(detail_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
