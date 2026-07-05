# -*- coding: utf-8 -*-
"""
187 - 171 SOFT BLOCK CLEANER

171 v2 detay JSONL çıktısındaki soft block kartları üretim JSONL'den çıkarır.
DB'ye yazmaz.

Soft block sebepleri:
- KONU_OZETI_COK_KISA
- SONUC_OZETI_COK_KISA
- ANAHTAR_YETERSIZ

Kullanım:
  python ".py\\187_171_Soft_Block_Cleaner.py" "C:\\...\\168_production_output_x.jsonl" "C:\\...\\171_v2_mini_kalite_detay_x.jsonl"
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

SOFT_REASONS = {"KONU_OZETI_COK_KISA", "SONUC_OZETI_COK_KISA", "ANAHTAR_YETERSIZ"}

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
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                rows.append({"_json_error": str(e), "_line_no": line_no, "_raw": line[:300]})
    return rows


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def safe(v):
    return "" if v is None else str(v).strip()


def issues_list(v):
    if isinstance(v, list):
        return [safe(x) for x in v if safe(x)]
    if isinstance(v, str):
        try:
            obj = json.loads(v)
            if isinstance(obj, list):
                return [safe(x) for x in obj if safe(x)]
        except Exception:
            pass
        return [x.strip(" '\"[]") for x in v.split(",") if x.strip(" '\"[]")]
    return []


def get_karar_no(row):
    return safe(row.get("karar_no") or row.get("orijinal_karar_no") or row.get("karar"))


def load_blocks(detail_path):
    rows = read_jsonl(detail_path)
    soft_blocks = []
    hard_blocks = []
    missing_index = 0

    for r in rows:
        if r.get("_json_error"):
            continue

        status = safe(r.get("status") or r.get("quality_status") or r.get("result")).upper()
        issues = issues_list(r.get("issues") or r.get("block_reasons") or r.get("sebepler"))

        is_block = status == "BLOCK" or r.get("is_block") is True or r.get("block") is True
        if not is_block and not any(i in SOFT_REASONS for i in issues):
            continue

        karar_no = safe(r.get("karar_no") or r.get("decision_no"))
        idx = r.get("card_index") or r.get("kart_index") or r.get("index") or r.get("kart_no")
        try:
            idx = int(idx)
        except Exception:
            idx = None

        if not karar_no or idx is None:
            missing_index += 1
            continue

        non_soft = [i for i in issues if i and i not in SOFT_REASONS]
        item = {
            "karar_no": karar_no,
            "card_index": idx,
            "issues": issues,
            "non_soft_issues": non_soft,
            "title": r.get("baslik") or r.get("title"),
        }
        if non_soft:
            hard_blocks.append(item)
        else:
            soft_blocks.append(item)

    return soft_blocks, hard_blocks, missing_index


def main():
    print("=" * 80)
    print("187 - 171 SOFT BLOCK CLEANER")
    print("=" * 80)

    run_tag = tag()

    input_output = sys.argv[1] if len(sys.argv) >= 2 else latest_file(os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl"))
    detail_path = sys.argv[2] if len(sys.argv) >= 3 else latest_file(os.path.join(LOG_DIR, "171_v2_mini_kalite_detay_*.jsonl"))

    if not input_output or not os.path.exists(input_output):
        raise FileNotFoundError("Production output JSONL bulunamadı.")
    if not detail_path or not os.path.exists(detail_path):
        raise FileNotFoundError("171 detay JSONL bulunamadı.")

    print(f"\nInput output : {input_output}")
    print(f"171 detay    : {detail_path}")
    print("-" * 80)

    soft_blocks, hard_blocks, missing_index = load_blocks(detail_path)

    output_path = os.path.join(URETIM_OUTPUT_DIR, f"187_cleaned_production_output_{run_tag}.jsonl")
    quarantine_path = os.path.join(LOG_DIR, f"187_soft_block_quarantine_{run_tag}.jsonl")
    detail_out = os.path.join(LOG_DIR, f"187_soft_block_cleaner_detay_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"187_soft_block_cleaner_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"187_171_soft_block_cleaner_raporu_{run_tag}.txt")

    if hard_blocks:
        state = {
            "run_id": run_tag,
            "created_at": now(),
            "input_output": input_output,
            "detail_path": detail_path,
            "output_path": None,
            "soft_block_count": len(soft_blocks),
            "hard_block_count": len(hard_blocks),
            "missing_index_rows": missing_index,
            "ready_for_171_recheck": False,
            "reason": "Hard block bulundu; otomatik temizleme yapılmadı.",
        }
        write_json(state_path, state)
        with open(rapor_path, "w", encoding="utf-8") as f:
            f.write("187 - 171 SOFT BLOCK CLEANER RAPORU\n")
            f.write("=" * 80 + "\n\n")
            f.write("SONUC: HAYIR\nHard block bulundu; otomatik temizleme yapılmadı.\n")
            for b in hard_blocks:
                f.write(f"- {b['karar_no']} kart={b['card_index']} issues={b['issues']}\n")
        print("\n187 DURDU")
        print(f"Hard block: {len(hard_blocks)}")
        print(f"Soft block: {len(soft_blocks)}")
        print("171 tekrar kontrol hazır mı: HAYIR")
        print(state_path)
        print(rapor_path)
        return

    remove_map = {}
    for b in soft_blocks:
        remove_map.setdefault(b["karar_no"], set()).add(b["card_index"])

    rows = read_jsonl(input_output)
    cleaned = []

    total_cards = 0
    kept_cards = 0
    removed_cards = 0
    affected = set()

    for row in rows:
        if row.get("_json_error") or row.get("status") != "OK":
            cleaned.append(row)
            continue

        karar_no = get_karar_no(row)
        cards = row.get("kartlar", [])
        if not isinstance(cards, list):
            cleaned.append(row)
            continue

        total_cards += len(cards)
        to_remove = remove_map.get(karar_no, set())
        new_cards = []

        for idx, card in enumerate(cards, 1):
            if idx in to_remove:
                removed_cards += 1
                affected.add(karar_no)
                q = next((x for x in soft_blocks if x["karar_no"] == karar_no and x["card_index"] == idx), {})
                append_jsonl(quarantine_path, {
                    "karar_no": karar_no,
                    "card_index": idx,
                    "action": "SOFT_BLOCK_REMOVED",
                    "issues": q.get("issues", []),
                    "card": card,
                })
            else:
                kept_cards += 1
                new_cards.append(card)

        new_row = dict(row)
        new_row["kartlar"] = new_cards
        new_row["kart_sayisi"] = len(new_cards)
        new_row["soft_block_cleaning"] = {
            "source": "187_171_Soft_Block_Cleaner",
            "created_at": now(),
            "original_card_count": len(cards),
            "new_card_count": len(new_cards),
            "removed_count": len(cards) - len(new_cards),
        }
        cleaned.append(new_row)

    write_jsonl(output_path, cleaned)

    for b in soft_blocks:
        append_jsonl(detail_out, {"action": "REMOVE_SOFT_BLOCK", **b})

    ready = removed_cards > 0 and removed_cards <= len(soft_blocks)

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_output": input_output,
        "detail_path": detail_path,
        "output_path": output_path,
        "total_cards": total_cards,
        "kept_cards": kept_cards,
        "removed_cards": removed_cards,
        "soft_block_count": len(soft_blocks),
        "hard_block_count": len(hard_blocks),
        "missing_index_rows": missing_index,
        "affected_decisions": sorted(affected),
        "affected_decision_count": len(affected),
        "quarantine_path": quarantine_path,
        "detail_out": detail_out,
        "rapor_path": rapor_path,
        "ready_for_171_recheck": ready,
        "ready_for_177": ready,
        "recommended_171_recheck": f'python ".py\\171_v2_Mini_Uretim_Kalite_Kontrol_Motoru.py" "{output_path}"',
        "recommended_next_177": f'python ".py\\177_Hukuki_Dogruluk_Hakemi.py" "{output_path}"',
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("187 - 171 SOFT BLOCK CLEANER RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input output                  : {input_output}\n")
        f.write(f"171 detay                     : {detail_path}\n\n")
        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam kart                    : {total_cards}\n")
        f.write(f"Korunan kart                   : {kept_cards}\n")
        f.write(f"Çıkarılan soft block kart      : {removed_cards}\n")
        f.write(f"Etkilenen karar                : {len(affected)}\n")
        f.write(f"Hard block                     : {len(hard_blocks)}\n")
        f.write(f"Indexi okunamayan detay        : {missing_index}\n")
        f.write(f"171 tekrar kontrol hazır mı    : {'EVET' if ready else 'HAYIR'}\n\n")
        f.write("ÖNERILEN KOMUTLAR\n")
        f.write("-" * 80 + "\n")
        f.write(state["recommended_171_recheck"] + "\n")
        f.write(state["recommended_next_177"] + "\n\n")
        f.write("DOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Clean output                   : {output_path}\n")
        f.write(f"Quarantine JSONL               : {quarantine_path}\n")
        f.write(f"Detay JSONL                    : {detail_out}\n")
        f.write(f"State JSON                     : {state_path}\n")
        f.write(f"Rapor                          : {rapor_path}\n")

    print("\n187 SOFT BLOCK CLEANER TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam kart                    : {total_cards}")
    print(f"Korunan kart                   : {kept_cards}")
    print(f"Çıkarılan soft block kart      : {removed_cards}")
    print(f"Etkilenen karar                : {len(affected)}")
    print(f"Hard block                     : {len(hard_blocks)}")
    print(f"171 tekrar kontrol hazır mı    : {'EVET' if ready else 'HAYIR'}")

    print("\nClean output:")
    print(output_path)

    print("\nÖnerilen komut:")
    print(state["recommended_171_recheck"])

    print("\nDosyalar:")
    print(quarantine_path)
    print(detail_out)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
