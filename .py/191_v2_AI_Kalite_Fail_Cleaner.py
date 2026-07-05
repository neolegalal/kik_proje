# -*- coding: utf-8 -*-
"""
191 v2 - AI KALITE FAIL CLEANER

172 detay formatı:
{
  "status": "OK",
  "card": {"row_index": 1, "card_index": 1, "karar_no": "..."},
  "judgement": {"decision": "PASS/FAIL/WARNING", ...}
}

Kullanım:
  python ".py\\191_v2_AI_Kalite_Fail_Cleaner.py" "INPUT_JSONL" "172_DETAIL_JSONL"
"""

import os
import sys
import json
import glob
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

os.makedirs(URETIM_OUTPUT_DIR, exist_ok=True)
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

def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                rows.append({"_json_error": str(e), "_line_no": line_no, "_raw": line[:500]})
    return rows

def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def safe(v):
    return "" if v is None else str(v).strip()

def get_karar_no(row):
    return safe(row.get("karar_no") or row.get("orijinal_karar_no") or row.get("decision_no") or row.get("karar"))

def is_fail_value(v):
    return safe(v).upper() in {"FAIL", "FAILED", "BLOCK", "RED", "HAYIR"}

def load_fail_cards(detail_path):
    fail_cards = []
    warning_cards = 0
    pass_cards = 0
    malformed = 0

    for row in read_jsonl(detail_path):
        if row.get("_json_error"):
            malformed += 1
            continue

        card = row.get("card") if isinstance(row.get("card"), dict) else {}
        judgement = row.get("judgement") if isinstance(row.get("judgement"), dict) else {}

        karar_no = safe(card.get("karar_no") or row.get("karar_no") or row.get("decision_no"))

        try:
            card_index = int(card.get("card_index") or row.get("card_index") or row.get("kart_index"))
        except Exception:
            card_index = None

        try:
            row_index = int(card.get("row_index") or row.get("row_index"))
        except Exception:
            row_index = None

        decision = (
            judgement.get("decision")
            or row.get("decision")
            or row.get("ai_decision")
            or row.get("quality_decision")
            or row.get("result")
        )

        decision_upper = safe(decision).upper()
        if decision_upper == "PASS":
            pass_cards += 1
        elif decision_upper == "WARNING":
            warning_cards += 1

        if karar_no and card_index is not None and is_fail_value(decision):
            fail_cards.append({
                "karar_no": karar_no,
                "row_index": row_index,
                "card_index": card_index,
                "decision": decision,
                "score": judgement.get("overall_score"),
                "issues": judgement.get("issues", []),
                "reason": judgement.get("reason"),
                "baslik": card.get("baslik"),
                "raw_response_path": row.get("raw_response_path"),
            })

    seen = set()
    uniq = []
    for x in fail_cards:
        key = (x["karar_no"], x["card_index"])
        if key not in seen:
            seen.add(key)
            uniq.append(x)

    return uniq, {
        "pass_cards": pass_cards,
        "warning_cards": warning_cards,
        "malformed": malformed,
    }

def main():
    print("=" * 80)
    print("191 v2 - AI KALITE FAIL CLEANER")
    print("=" * 80)

    run_tag = tag()

    input_output = sys.argv[1] if len(sys.argv) >= 2 else latest_file(os.path.join(URETIM_OUTPUT_DIR, "*production_output_*.jsonl"))
    detail_path = sys.argv[2] if len(sys.argv) >= 3 else latest_file(os.path.join(LOG_DIR, "172_ai_kalite_hakemi_detay_*.jsonl"))

    if not input_output or not os.path.exists(input_output):
        raise FileNotFoundError("Production output JSONL bulunamadı.")
    if not detail_path or not os.path.exists(detail_path):
        raise FileNotFoundError("172 detay JSONL bulunamadı.")

    print(f"\nInput output : {input_output}")
    print(f"172 detay    : {detail_path}")
    print("-" * 80)

    fail_cards, stats = load_fail_cards(detail_path)

    output_path = os.path.join(URETIM_OUTPUT_DIR, f"191_v2_ai_cleaned_production_output_{run_tag}.jsonl")
    quarantine_path = os.path.join(LOG_DIR, f"191_v2_ai_fail_quarantine_{run_tag}.jsonl")
    detail_out = os.path.join(LOG_DIR, f"191_v2_ai_fail_cleaner_detay_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"191_v2_ai_fail_cleaner_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"191_v2_ai_kalite_fail_cleaner_raporu_{run_tag}.txt")

    remove_map = {}
    for item in fail_cards:
        remove_map.setdefault(item["karar_no"], set()).add(item["card_index"])

    rows = read_jsonl(input_output)
    cleaned_rows = []
    total_cards = 0
    kept_cards = 0
    removed_cards = 0
    affected_decisions = set()

    for row in rows:
        if row.get("_json_error") or row.get("status") != "OK":
            cleaned_rows.append(row)
            continue

        karar_no = get_karar_no(row)
        kartlar = row.get("kartlar", [])
        if not isinstance(kartlar, list):
            cleaned_rows.append(row)
            continue

        total_cards += len(kartlar)
        to_remove = remove_map.get(karar_no, set())
        new_kartlar = []

        for idx, card in enumerate(kartlar, start=1):
            if idx in to_remove:
                removed_cards += 1
                affected_decisions.add(karar_no)
                fail_info = next((x for x in fail_cards if x["karar_no"] == karar_no and x["card_index"] == idx), {})
                append_jsonl(quarantine_path, {
                    "karar_no": karar_no,
                    "card_index": idx,
                    "action": "AI_QUALITY_FAIL_REMOVED",
                    "card": card,
                    "fail_info": fail_info,
                })
                continue
            kept_cards += 1
            new_kartlar.append(card)

        new_row = dict(row)
        new_row["kartlar"] = new_kartlar
        new_row["kart_sayisi"] = len(new_kartlar)
        new_row["ai_quality_cleaning"] = {
            "source": "191_v2_AI_Kalite_Fail_Cleaner",
            "created_at": now(),
            "original_card_count": len(kartlar),
            "new_card_count": len(new_kartlar),
            "removed_count": len(kartlar) - len(new_kartlar),
        }
        cleaned_rows.append(new_row)

    write_jsonl(output_path, cleaned_rows)

    for item in fail_cards:
        append_jsonl(detail_out, {"action": "REMOVE_AI_FAIL", **item})

    ready = removed_cards == len(fail_cards) and removed_cards > 0

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_output": input_output,
        "detail_path": detail_path,
        "output_path": output_path,
        "total_cards": total_cards,
        "kept_cards": kept_cards,
        "removed_cards": removed_cards,
        "fail_cards_detected": len(fail_cards),
        "pass_cards_in_172_detail": stats["pass_cards"],
        "warning_cards_in_172_detail": stats["warning_cards"],
        "malformed_detail_rows": stats["malformed"],
        "affected_decisions": sorted(affected_decisions),
        "affected_decision_count": len(affected_decisions),
        "quarantine_path": quarantine_path,
        "detail_out": detail_out,
        "rapor_path": rapor_path,
        "ready_for_172_recheck": ready,
        "ready_for_175": ready,
        "recommended_172_recheck": f'python ".py\\172_AI_Kalite_Hakemi.py" "{output_path}"',
        "recommended_next_175": f'python ".py\\175_v2_AI_Hukuki_Mesele_Kapsam_Analiz_Motoru.py" "{output_path}"',
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("191 v2 - AI KALITE FAIL CLEANER RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input output                  : {input_output}\n")
        f.write(f"172 detay                     : {detail_path}\n\n")
        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam kart                    : {total_cards}\n")
        f.write(f"Korunan kart                   : {kept_cards}\n")
        f.write(f"Çıkarılan AI FAIL kart         : {removed_cards}\n")
        f.write(f"Tespit edilen FAIL kart        : {len(fail_cards)}\n")
        f.write(f"Etkilenen karar                : {len(affected_decisions)}\n")
        f.write(f"172 tekrar kontrol hazır mı    : {'EVET' if ready else 'HAYIR'}\n\n")
        f.write("ETKILENEN KARARLAR\n")
        f.write("-" * 80 + "\n")
        for k in sorted(affected_decisions):
            f.write(f"- {k}\n")
        f.write("\nÖNERILEN KOMUTLAR\n")
        f.write("-" * 80 + "\n")
        f.write(state["recommended_172_recheck"] + "\n")
        f.write(state["recommended_next_175"] + "\n\n")
        f.write("DOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Clean output                   : {output_path}\n")
        f.write(f"Quarantine JSONL               : {quarantine_path}\n")
        f.write(f"Detay JSONL                    : {detail_out}\n")
        f.write(f"State JSON                     : {state_path}\n")
        f.write(f"Rapor                          : {rapor_path}\n")

    print("\n191 v2 AI KALITE FAIL CLEANER TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam kart                    : {total_cards}")
    print(f"Korunan kart                   : {kept_cards}")
    print(f"Çıkarılan AI FAIL kart         : {removed_cards}")
    print(f"Tespit edilen FAIL kart        : {len(fail_cards)}")
    print(f"Etkilenen karar                : {len(affected_decisions)}")
    print(f"172 tekrar kontrol hazır mı    : {'EVET' if ready else 'HAYIR'}")

    print("\nClean output:")
    print(output_path)

    print("\nÖnerilen komut:")
    print(state["recommended_172_recheck"])

    print("\nDosyalar:")
    print(quarantine_path)
    print(detail_out)
    print(state_path)
    print(rapor_path)

if __name__ == "__main__":
    main()
