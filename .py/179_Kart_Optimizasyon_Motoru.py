# -*- coding: utf-8 -*-
"""
179 - KART OPTIMIZASYON MOTORU

Amaç:
- 168 production output JSONL dosyasını ve 178 Akıllı Kart Birleştirme Hakemi detay çıktısını okur.
- 178'in önerdiği merge_groups / cards_to_drop / cards_to_keep planına göre optimize edilmiş yeni JSONL üretir.
- DB'ye yazmaz.
- 169 importer'a gidecek daha temiz üretim çıktısı oluşturur.

Kullanım:
  python ".py\\179_Kart_Optimizasyon_Motoru.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\uretim_output\\168_production_output_20260630_182904.jsonl"

Belirli 178 detay dosyasıyla:
  python ".py\\179_Kart_Optimizasyon_Motoru.py" "C:\\...\\168_production_output_x.jsonl" "C:\\Users\\MSI\\Desktop\\kik_proje\\production_logs\\178_birlestirme_hakemi_detay_YYYYMMDD_HHMMSS.jsonl"

Not:
- API kullanmaz.
- DB'ye yazmaz.
- Birleştirilmiş kartlar 178'in önerdiği yeni başlık/soru/ilke ile oluşturulur; konu/sonuç/mevzuat/anahtar alanları mevcut kartlardan güvenli şekilde harmanlanır.
"""

import os
import re
import sys
import glob
import json
from datetime import datetime
from collections import defaultdict


BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

INPUT_PATTERN_168 = os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl")
INPUT_PATTERN_178 = os.path.join(LOG_DIR, "178_birlestirme_hakemi_detay_*.jsonl")

os.makedirs(URETIM_OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


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
                rows.append({"_json_error": str(e), "_line_no": line_no, "_raw": line[:300]})
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


def normalize_list(v):
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
    return [p.strip() for p in re.split(r"[,;]\s*", s) if p.strip()]


def unique_keep_order(items):
    seen = set()
    out = []
    for x in items:
        s = str(x).strip()
        key = s.lower()
        if s and key not in seen:
            seen.add(key)
            out.append(s)
    return out


def join_unique_sentences(parts, max_len=900):
    out = []
    seen = set()
    for p in parts:
        p = str(p or "").strip()
        if not p:
            continue
        key = re.sub(r"\s+", " ", p.lower())
        if key not in seen:
            seen.add(key)
            out.append(p)
    text = " ".join(out)
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0].strip() + "..."


def get_card_by_index(cards, idx):
    try:
        idx = int(idx)
    except Exception:
        return None
    if 1 <= idx <= len(cards):
        return cards[idx - 1]
    return None


def merge_cards(cards, group):
    indexes = group.get("cards", [])
    selected = [get_card_by_index(cards, i) for i in indexes]
    selected = [c for c in selected if isinstance(c, dict)]

    if not selected:
        return None

    first = selected[0]

    baslik = str(group.get("recommended_new_title") or first.get("baslik") or "").strip()
    hukuki_soru = str(group.get("recommended_new_hukuki_soru") or first.get("hukuki_soru") or "").strip()
    emsal_ilke = str(group.get("recommended_new_emsal_ilke") or first.get("emsal_ilke") or "").strip()

    konu_ozeti = join_unique_sentences([c.get("konu_ozeti", "") for c in selected], max_len=700)
    sonuc_ozeti = join_unique_sentences([c.get("sonuc_ozeti", "") or c.get("sonuc", "") for c in selected], max_len=700)

    mevzuat = []
    anahtar = []
    guven_vals = []
    sonuc_tipleri = []

    for c in selected:
        mevzuat.extend(normalize_list(c.get("mevzuat")))
        anahtar.extend(normalize_list(c.get("anahtar")))
        if c.get("guven"):
            guven_vals.append(str(c.get("guven")))
        if c.get("sonuc_tipi"):
            sonuc_tipleri.append(str(c.get("sonuc_tipi")))

    merged = {
        "baslik": baslik,
        "hukuki_soru": hukuki_soru,
        "konu_ozeti": konu_ozeti,
        "sonuc_ozeti": sonuc_ozeti,
        "sonuc": sonuc_ozeti,
        "sonuc_tipi": sonuc_tipleri[0] if sonuc_tipleri else first.get("sonuc_tipi", ""),
        "emsal_ilke": emsal_ilke,
        "mevzuat": unique_keep_order(mevzuat),
        "anahtar": unique_keep_order(anahtar)[:12],
        "guven": guven_vals[0] if guven_vals else first.get("guven", ""),
        "optimizasyon_notu": {
            "type": "MERGED",
            "source_card_indexes": indexes,
            "merge_reason": group.get("reason", ""),
            "merge_priority": group.get("priority", ""),
        }
    }

    return merged


def load_merge_plan(path):
    rows = read_jsonl(path)
    plans = {}
    for row in rows:
        if row.get("status") != "OK":
            continue
        karar_no = str(row.get("karar_no", "")).strip()
        review = row.get("review", {})
        if karar_no and isinstance(review, dict):
            plans[karar_no] = review
    return plans


def optimize_decision_row(row, plan):
    original_cards = row.get("kartlar", [])
    if not isinstance(original_cards, list):
        original_cards = []

    if not plan or plan.get("decision") == "PASS":
        new_cards = []
        for c in original_cards:
            if isinstance(c, dict):
                cc = dict(c)
                cc.setdefault("optimizasyon_notu", {"type": "UNCHANGED"})
                new_cards.append(cc)
        return new_cards, {
            "action": "UNCHANGED",
            "original_count": len(original_cards),
            "new_count": len(new_cards),
            "merged_groups": 0,
            "dropped_count": 0,
        }

    merge_groups = plan.get("merge_groups", [])
    if not isinstance(merge_groups, list):
        merge_groups = []

    cards_to_drop_items = plan.get("cards_to_drop", [])
    drop_indexes = set()
    if isinstance(cards_to_drop_items, list):
        for d in cards_to_drop_items:
            if isinstance(d, dict):
                try:
                    drop_indexes.add(int(d.get("card_index")))
                except Exception:
                    pass
            else:
                try:
                    drop_indexes.add(int(d))
                except Exception:
                    pass

    merged_source_indexes = set()
    new_cards = []
    merged_count = 0

    # Önce merge kartlarını ekle
    for g in merge_groups:
        if not isinstance(g, dict):
            continue
        merged = merge_cards(original_cards, g)
        if merged:
            new_cards.append(merged)
            merged_count += 1
            for idx in g.get("cards", []):
                try:
                    merged_source_indexes.add(int(idx))
                except Exception:
                    pass

    # Sonra bağımsız kalanları ekle
    for idx, c in enumerate(original_cards, start=1):
        if not isinstance(c, dict):
            continue
        if idx in merged_source_indexes:
            continue
        if idx in drop_indexes:
            continue
        cc = dict(c)
        cc.setdefault("optimizasyon_notu", {"type": "UNCHANGED"})
        new_cards.append(cc)

    return new_cards, {
        "action": "OPTIMIZED" if (merged_count or drop_indexes) else "UNCHANGED",
        "original_count": len(original_cards),
        "new_count": len(new_cards),
        "merged_groups": merged_count,
        "dropped_count": len(drop_indexes),
    }


def main():
    print("=" * 80)
    print("179 - KART OPTIMIZASYON MOTORU")
    print("=" * 80)

    run_tag = tag()

    if len(sys.argv) >= 2:
        input_168 = sys.argv[1]
    else:
        input_168 = latest_file(INPUT_PATTERN_168)

    if len(sys.argv) >= 3:
        input_178 = sys.argv[2]
    else:
        input_178 = latest_file(INPUT_PATTERN_178)

    if not input_168 or not os.path.exists(input_168):
        raise FileNotFoundError("168 production output JSONL bulunamadı.")
    if not input_178 or not os.path.exists(input_178):
        raise FileNotFoundError("178 birleştirme hakemi detay JSONL bulunamadı.")

    rows = read_jsonl(input_168)
    plans = load_merge_plan(input_178)

    output_jsonl = os.path.join(URETIM_OUTPUT_DIR, f"179_optimized_production_output_{run_tag}.jsonl")
    detail_path = os.path.join(LOG_DIR, f"179_kart_optimizasyon_detay_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"179_kart_optimizasyon_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"179_kart_optimizasyon_raporu_{run_tag}.txt")

    optimized_rows = []
    decision_summaries = []

    total_original = 0
    total_new = 0
    optimized_decisions = 0
    unchanged_decisions = 0
    error_count = 0

    for row in rows:
        if "_json_error" in row:
            optimized_rows.append(row)
            error_count += 1
            continue

        if row.get("status") != "OK":
            optimized_rows.append(row)
            continue

        karar_no = str(row.get("karar_no") or row.get("orijinal_karar_no") or "").strip()
        plan = plans.get(karar_no)

        try:
            new_cards, summary = optimize_decision_row(row, plan)
            new_row = dict(row)
            new_row["kartlar"] = new_cards
            new_row["optimizasyon"] = {
                "source": "179_Kart_Optimizasyon_Motoru",
                "created_at": now(),
                "input_168": input_168,
                "input_178": input_178,
                **summary,
            }

            optimized_rows.append(new_row)

            total_original += summary["original_count"]
            total_new += summary["new_count"]

            if summary["action"] == "OPTIMIZED":
                optimized_decisions += 1
            else:
                unchanged_decisions += 1

            decision_summaries.append({
                "karar_no": karar_no,
                **summary,
            })
            append_jsonl(detail_path, {"karar_no": karar_no, **summary})

        except Exception as e:
            error_count += 1
            new_row = dict(row)
            new_row["optimizasyon_hatasi"] = str(e)
            optimized_rows.append(new_row)
            append_jsonl(detail_path, {
                "karar_no": karar_no,
                "status": "ERROR",
                "error": str(e),
            })

    write_jsonl(output_jsonl, optimized_rows)

    reduction = max(0, total_original - total_new)
    reduction_rate = round((reduction / total_original) * 100, 2) if total_original else 0
    ready_for_180 = error_count == 0 and total_new > 0

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_168": input_168,
        "input_178": input_178,
        "output_jsonl": output_jsonl,
        "decision_count": len(decision_summaries),
        "optimized_decisions": optimized_decisions,
        "unchanged_decisions": unchanged_decisions,
        "total_original_cards": total_original,
        "total_optimized_cards": total_new,
        "reduction_count": reduction,
        "reduction_rate": reduction_rate,
        "error_count": error_count,
        "ready_for_180": ready_for_180,
        "detail_path": detail_path,
        "rapor_path": rapor_path,
        "next_step": "180_Final_Master_Production_Controller.py",
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("179 - KART OPTIMIZASYON MOTORU RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"168 input                     : {input_168}\n")
        f.write(f"178 input                     : {input_178}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Karar sayısı                   : {len(decision_summaries)}\n")
        f.write(f"Optimize edilen karar          : {optimized_decisions}\n")
        f.write(f"Değişmeden kalan karar         : {unchanged_decisions}\n")
        f.write(f"Orijinal kart                  : {total_original}\n")
        f.write(f"Optimize kart                  : {total_new}\n")
        f.write(f"Azalma                         : {reduction} kart (%{reduction_rate})\n")
        f.write(f"Hata                           : {error_count}\n")
        f.write(f"180'e geçilebilir mi           : {'EVET' if ready_for_180 else 'HAYIR'}\n\n")

        f.write("KARAR BAZLI OPTIMIZASYON\n")
        f.write("-" * 80 + "\n")
        for s in decision_summaries:
            f.write(f"{s['karar_no']:<20} | {s['action']:<10} | {s['original_count']} -> {s['new_count']} | merged={s['merged_groups']} | dropped={s['dropped_count']}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Optimize JSONL                 : {output_jsonl}\n")
        f.write(f"Detay JSONL                    : {detail_path}\n")
        f.write(f"State JSON                     : {state_path}\n")
        f.write(f"Rapor                          : {rapor_path}\n")

    print("\n179 KART OPTIMIZASYON TAMAMLANDI")
    print("-" * 80)
    print(f"Karar sayısı                   : {len(decision_summaries)}")
    print(f"Optimize edilen karar          : {optimized_decisions}")
    print(f"Değişmeden kalan karar         : {unchanged_decisions}")
    print(f"Orijinal kart                  : {total_original}")
    print(f"Optimize kart                  : {total_new}")
    print(f"Azalma                         : {reduction} kart (%{reduction_rate})")
    print(f"Hata                           : {error_count}")
    print(f"180'e geçilebilir mi           : {'EVET' if ready_for_180 else 'HAYIR'}")

    print("\nDosyalar:")
    print(output_jsonl)
    print(detail_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
