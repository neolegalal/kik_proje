# -*- coding: utf-8 -*-
"""
182 v2 - PRODUCTION DRIFT ANALIZ MOTORU

v2 farkı:
- Eski model kartlar ile yeni model kartları ayrı analiz eder.
- Eski kartlarda konu_ozeti / anahtar boşluğu beklenen durum olduğu için genel drift skorunu haksız düşürmez.
- Yeni model kart kalitesini ayrıca ölçer.
- Genel havuz için "legacy gap" uyarısı verir; production drift kararı yeni model kartlara göre verilir.
- API kullanmaz, DB'ye yazmaz.

Kullanım:
  python ".py\\182_v2_Production_Drift_Analiz_Motoru.py"

Belirli export ile:
  python ".py\\182_v2_Production_Drift_Analiz_Motoru.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\exports\\web_export_170_YYYYMMDD_HHMMSS.jsonl"

DB ile:
  python ".py\\182_v2_Production_Drift_Analiz_Motoru.py" --db
"""

import os
import re
import sys
import csv
import json
import glob
import sqlite3
import statistics
from datetime import datetime
from collections import Counter, defaultdict


BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")

EXPORT_DIR = os.path.join(BASE_DIR, "exports")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

WEB_JSONL_PATTERN = os.path.join(EXPORT_DIR, "web_export_170_*.jsonl")
WEB_CSV_PATTERN = os.path.join(EXPORT_DIR, "web_export_170_*.csv")
TABLE_NAME = "hukuki_kartlar"

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


def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def safe(v):
    return "" if v is None else str(v).strip()


def norm_text(s):
    s = safe(s).lower()
    tr = str.maketrans("çğıöşüâîû", "cgiosuaiu")
    s = s.translate(tr)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def word_count(s):
    s = safe(s)
    return len(s.split()) if s else 0


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


def pct(n, d):
    return round((n / d) * 100, 2) if d else 0.0


def stats_num(values):
    values = [v for v in values if isinstance(v, (int, float))]
    if not values:
        return {"min": 0, "avg": 0, "median": 0, "max": 0}
    return {
        "min": min(values),
        "avg": round(sum(values) / len(values), 2),
        "median": round(statistics.median(values), 2),
        "max": max(values),
    }


def similarity_tokens(a, b):
    aw = set(re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]{4,}", norm_text(a)))
    bw = set(re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]{4,}", norm_text(b)))
    if not aw or not bw:
        return 0.0
    return len(aw & bw) / max(1, min(len(aw), len(bw)))


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
    if not cols:
        raise RuntimeError(f"Tablo bulunamadı: {TABLE_NAME}")

    if "aktif" in cols:
        where = "WHERE COALESCE(aktif, 1) = 1"
    elif "is_active" in cols:
        where = "WHERE COALESCE(is_active, 1) = 1"
    else:
        where = ""

    rows = [dict(r) for r in cur.execute(f"SELECT * FROM {TABLE_NAME} {where}").fetchall()]
    conn.close()
    return rows


def resolve_input():
    args = sys.argv[1:]
    if args and args[0] == "--db":
        return "DB", DB_PATH

    if args and os.path.exists(args[0]):
        p = args[0]
        ext = os.path.splitext(p)[1].lower()
        if ext == ".jsonl":
            return "JSONL", p
        if ext == ".csv":
            return "CSV", p
        raise RuntimeError("Desteklenmeyen input uzantısı. JSONL veya CSV ver.")

    latest_jsonl = latest_file(WEB_JSONL_PATTERN)
    if latest_jsonl:
        return "JSONL", latest_jsonl

    latest_csv = latest_file(WEB_CSV_PATTERN)
    if latest_csv:
        return "CSV", latest_csv

    return "DB", DB_PATH


def standardize_card(row):
    karar_no = safe(row.get("karar_no") or row.get("kararNo") or row.get("karar"))
    baslik = safe(row.get("baslik") or row.get("başlık"))
    hukuki_soru = safe(row.get("hukuki_soru") or row.get("hukukiSoru"))
    konu_ozeti = safe(row.get("konu_ozeti") or row.get("konuOzeti"))
    sonuc_ozeti = safe(row.get("sonuc_ozeti") or row.get("sonucOzeti") or row.get("sonuc"))
    sonuc = safe(row.get("sonuc") or sonuc_ozeti)
    sonuc_tipi = safe(row.get("sonuc_tipi") or row.get("sonucTipi"))
    emsal_ilke = safe(row.get("emsal_ilke") or row.get("emsalIlke"))
    guven = safe(row.get("guven") or row.get("güven"))
    source = safe(row.get("source") or row.get("kaynak_yontem") or row.get("kaynak"))

    mevzuat = parse_list(row.get("mevzuat"))
    anahtar = parse_list(row.get("anahtar") or row.get("anahtarlar"))

    is_new_model = bool(konu_ozeti and anahtar)

    return {
        "karar_no": karar_no,
        "baslik": baslik,
        "hukuki_soru": hukuki_soru,
        "konu_ozeti": konu_ozeti,
        "sonuc_ozeti": sonuc_ozeti,
        "sonuc": sonuc,
        "sonuc_tipi": sonuc_tipi,
        "emsal_ilke": emsal_ilke,
        "mevzuat": mevzuat,
        "anahtar": anahtar,
        "guven": guven,
        "source": source,
        "is_new_model": is_new_model,
    }


def load_cards(source_type, input_path):
    if source_type == "JSONL":
        rows = read_jsonl(input_path)
    elif source_type == "CSV":
        rows = read_csv(input_path)
    elif source_type == "DB":
        rows = read_db()
    else:
        raise RuntimeError(f"Bilinmeyen source_type: {source_type}")

    cards = []
    json_errors = 0
    for r in rows:
        if isinstance(r, dict) and r.get("_json_error"):
            json_errors += 1
            continue
        cards.append(standardize_card(r))

    return cards, json_errors


def analyze_duplicates(cards, field, top_n=20):
    counter = Counter()
    examples = {}
    for c in cards:
        val = safe(c.get(field))
        if not val:
            continue
        key = norm_text(val)
        counter[key] += 1
        examples.setdefault(key, val)

    repeated = []
    for key, count in counter.most_common(top_n):
        if count > 1:
            repeated.append({
                "text": examples[key],
                "count": count,
            })
    return repeated


def analyze_near_duplicates(cards, max_pairs=50):
    groups = defaultdict(list)
    for i, c in enumerate(cards):
        key = norm_text(c.get("hukuki_soru") or c.get("baslik"))[:55]
        if key:
            groups[key].append((i, c))

    pairs = []
    for _, arr in groups.items():
        if len(arr) < 2:
            continue
        for a in range(len(arr)):
            for b in range(a + 1, len(arr)):
                i, c1 = arr[a]
                j, c2 = arr[b]
                text1 = " ".join([c1.get("baslik",""), c1.get("hukuki_soru",""), c1.get("emsal_ilke","")])
                text2 = " ".join([c2.get("baslik",""), c2.get("hukuki_soru",""), c2.get("emsal_ilke","")])
                sim = similarity_tokens(text1, text2)
                if sim >= 0.88:
                    pairs.append({
                        "i": i,
                        "j": j,
                        "similarity": round(sim, 3),
                        "karar_no_i": c1.get("karar_no"),
                        "karar_no_j": c2.get("karar_no"),
                        "baslik_i": c1.get("baslik"),
                        "baslik_j": c2.get("baslik"),
                    })
                    if len(pairs) >= max_pairs:
                        return pairs
    return pairs


def analyze_subset(cards, label, strict_new_model=False):
    total_cards = len(cards)
    karar_set = {c["karar_no"] for c in cards if c["karar_no"]}
    total_decisions = len(karar_set)
    card_per_decision = round(total_cards / total_decisions, 2) if total_decisions else 0

    missing = {
        "karar_no": sum(1 for c in cards if not c["karar_no"]),
        "baslik": sum(1 for c in cards if not c["baslik"]),
        "hukuki_soru": sum(1 for c in cards if not c["hukuki_soru"]),
        "konu_ozeti": sum(1 for c in cards if not c["konu_ozeti"]),
        "sonuc_ozeti": sum(1 for c in cards if not c["sonuc_ozeti"]),
        "emsal_ilke": sum(1 for c in cards if not c["emsal_ilke"]),
        "mevzuat": sum(1 for c in cards if len(c["mevzuat"]) == 0),
        "anahtar": sum(1 for c in cards if len(c["anahtar"]) == 0),
        "guven": sum(1 for c in cards if not c["guven"]),
    }

    title_words = [word_count(c["baslik"]) for c in cards]
    question_words = [word_count(c["hukuki_soru"]) for c in cards]
    konu_words = [word_count(c["konu_ozeti"]) for c in cards]
    sonuc_words = [word_count(c["sonuc_ozeti"]) for c in cards]
    emsal_words = [word_count(c["emsal_ilke"]) for c in cards]
    anahtar_counts = [len(c["anahtar"]) for c in cards]
    mevzuat_counts = [len(c["mevzuat"]) for c in cards]

    question_mark_count = sum(1 for c in cards if "?" in c["hukuki_soru"])
    question_form_count = sum(
        1 for c in cards
        if "?" in c["hukuki_soru"]
        or any(x in norm_text(c["hukuki_soru"]) for x in [" mi", " mu", " mudur", " midir", " nasil", " hangi"])
    )

    result_type_counter = Counter(c["sonuc_tipi"] or "BOS" for c in cards)
    guven_counter = Counter(c["guven"] or "BOS" for c in cards)

    all_keywords = []
    for c in cards:
        all_keywords.extend([x.lower() for x in c["anahtar"]])
    keyword_counter = Counter(all_keywords)

    all_laws = []
    for c in cards:
        all_laws.extend([x for x in c["mevzuat"]])
    law_counter = Counter(all_laws)

    repeated_titles = analyze_duplicates(cards, "baslik", 25)
    repeated_questions = analyze_duplicates(cards, "hukuki_soru", 25)
    repeated_principles = analyze_duplicates(cards, "emsal_ilke", 25)
    near_duplicates = analyze_near_duplicates(cards, 50)

    missing_rates = {k: pct(v, total_cards) for k, v in missing.items()}

    warnings = []
    score = 100

    if total_cards == 0:
        return {
            "label": label,
            "total_cards": 0,
            "total_decisions": 0,
            "card_per_decision": 0,
            "decision": "NO_DATA",
            "drift_score": 0,
            "warnings": ["Analiz edilecek kart yok."],
        }

    # Yeni model katı analizi
    if strict_new_model:
        critical_fields = ["baslik", "hukuki_soru", "konu_ozeti", "sonuc_ozeti", "emsal_ilke", "anahtar"]
        for field in critical_fields:
            rate = missing_rates.get(field, 0)
            if rate > 0:
                warnings.append(f"{label}: {field} boş oranı %{rate}")
                score -= min(25, int(rate * 1.5) + 5)

        mev_rate = missing_rates.get("mevzuat", 0)
        if mev_rate > 20:
            warnings.append(f"{label}: mevzuat boş oranı yüksek %{mev_rate}")
            score -= min(15, int(mev_rate / 3))

    # Legacy analizinde konu_ozeti/anahtar boşluğu ceza değil, sadece uyarı
    else:
        for field in ["baslik", "hukuki_soru", "sonuc_ozeti", "emsal_ilke"]:
            rate = missing_rates.get(field, 0)
            if rate > 10:
                warnings.append(f"{label}: {field} boş oranı yüksek %{rate}")
                score -= min(20, int(rate / 3))

    q_rate = pct(question_form_count, total_cards)
    if q_rate < 80:
        warnings.append(f"{label}: hukuki soru formu oranı düşük %{q_rate}")
        score -= 10

    if total_decisions and card_per_decision < 1.0:
        warnings.append(f"{label}: kart/karar oranı düşük {card_per_decision}")
        score -= 10
    if card_per_decision > 8:
        warnings.append(f"{label}: kart/karar oranı yüksek {card_per_decision}")
        score -= 10

    if repeated_titles and repeated_titles[0]["count"] > max(10, total_cards * 0.03):
        warnings.append(f"{label}: tekrarlayan başlık riski var.")
        score -= 8

    if repeated_questions and repeated_questions[0]["count"] > max(10, total_cards * 0.03):
        warnings.append(f"{label}: tekrarlayan hukuki soru riski var.")
        score -= 8

    if near_duplicates:
        warnings.append(f"{label}: benzer kart çifti tespit edildi: {len(near_duplicates)}")
        score -= min(10, len(near_duplicates))

    score = max(0, min(100, score))

    if score >= 90:
        decision = "PASS"
    elif score >= 75:
        decision = "WARNING"
    else:
        decision = "FAIL"

    return {
        "label": label,
        "total_cards": total_cards,
        "total_decisions": total_decisions,
        "card_per_decision": card_per_decision,
        "missing_counts": missing,
        "missing_rates": missing_rates,
        "length_stats": {
            "baslik_words": stats_num(title_words),
            "hukuki_soru_words": stats_num(question_words),
            "konu_ozeti_words": stats_num(konu_words),
            "sonuc_ozeti_words": stats_num(sonuc_words),
            "emsal_ilke_words": stats_num(emsal_words),
            "anahtar_count": stats_num(anahtar_counts),
            "mevzuat_count": stats_num(mevzuat_counts),
        },
        "question_form": {
            "question_mark_count": question_mark_count,
            "question_form_count": question_form_count,
            "question_form_rate": q_rate,
        },
        "result_type_distribution": result_type_counter.most_common(30),
        "guven_distribution": guven_counter.most_common(30),
        "top_keywords": keyword_counter.most_common(50),
        "top_mevzuat": law_counter.most_common(50),
        "repeated_titles": repeated_titles,
        "repeated_questions": repeated_questions,
        "repeated_principles": repeated_principles,
        "near_duplicate_pairs": near_duplicates,
        "warnings": warnings,
        "drift_score": score,
        "decision": decision,
    }


def main():
    print("=" * 80)
    print("182 v2 - PRODUCTION DRIFT ANALIZ MOTORU")
    print("=" * 80)

    run_tag = tag()
    source_type, input_path = resolve_input()

    print(f"\nKaynak tipi   : {source_type}")
    print(f"Input         : {input_path}")
    print("-" * 80)

    cards, json_errors = load_cards(source_type, input_path)

    new_cards = [c for c in cards if c["is_new_model"]]
    legacy_cards = [c for c in cards if not c["is_new_model"]]

    all_analysis = analyze_subset(cards, "GENEL_HAVUZ", strict_new_model=False)
    new_analysis = analyze_subset(new_cards, "YENI_MODEL", strict_new_model=True)
    legacy_analysis = analyze_subset(legacy_cards, "ESKI_MODEL", strict_new_model=False)

    # Final karar yeni model üzerinden verilir.
    if len(new_cards) == 0:
        final_decision = "WARNING"
        final_score = all_analysis["drift_score"]
        final_warnings = ["Yeni model kart bulunamadı; drift kararı genel havuz üzerinden verildi."]
    else:
        final_decision = new_analysis["decision"]
        final_score = new_analysis["drift_score"]
        final_warnings = list(new_analysis.get("warnings", []))

    # Eski model boşlukları ayrı not edilir.
    legacy_gap_note = ""
    if legacy_cards:
        legacy_gap_note = (
            f"Eski model kart sayısı {len(legacy_cards)}. "
            "Bu kartlarda konu_ozeti/anahtar boşluğu beklenen geçiş dönemi durumudur; "
            "final drift skorunu düşürmek için kullanılmadı."
        )

    if json_errors:
        final_warnings.append(f"JSON hata satırı var: {json_errors}")
        if final_decision == "PASS":
            final_decision = "WARNING"

    ready_for_183 = final_decision in {"PASS", "WARNING"}

    detail_path = os.path.join(LOG_DIR, f"182_v2_production_drift_detay_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"182_v2_production_drift_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"182_v2_production_drift_analiz_raporu_{run_tag}.txt")

    for scope, analysis in [("GENEL", all_analysis), ("YENI_MODEL", new_analysis), ("ESKI_MODEL", legacy_analysis)]:
        for key in ["repeated_titles", "repeated_questions", "repeated_principles", "near_duplicate_pairs"]:
            for item in analysis.get(key, []):
                append_jsonl(detail_path, {"scope": scope, "type": key, **item})

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "source_type": source_type,
        "input_path": input_path,
        "json_errors": json_errors,
        "total_cards": len(cards),
        "new_model_cards": len(new_cards),
        "legacy_cards": len(legacy_cards),
        "legacy_gap_note": legacy_gap_note,
        "general_analysis": all_analysis,
        "new_model_analysis": new_analysis,
        "legacy_analysis": legacy_analysis,
        "final_drift_score": final_score,
        "final_decision": final_decision,
        "final_warnings": final_warnings,
        "detail_path": detail_path,
        "rapor_path": rapor_path,
        "ready_for_183": ready_for_183,
        "next_step": "183_Production_Sampling_QA.py",
    }
    write_json(state_path, state)

    def write_section(f, title, analysis):
        f.write(f"\n{title}\n")
        f.write("-" * 80 + "\n")
        f.write(f"Karar sayısı                   : {analysis.get('total_decisions', 0)}\n")
        f.write(f"Kart sayısı                    : {analysis.get('total_cards', 0)}\n")
        f.write(f"Kart / karar                   : {analysis.get('card_per_decision', 0)}\n")
        f.write(f"Drift skoru                    : {analysis.get('drift_score', 0)} / 100\n")
        f.write(f"Karar                          : {analysis.get('decision')}\n")

        if analysis.get("missing_counts"):
            f.write("\nAlan boşlukları:\n")
            for k, v in analysis["missing_counts"].items():
                f.write(f"  {k:<18}: {v:<8} (%{analysis['missing_rates'][k]})\n")

        if analysis.get("length_stats"):
            f.write("\nUzunluk istatistikleri:\n")
            for k, v in analysis["length_stats"].items():
                f.write(f"  {k:<24}: min={v['min']} avg={v['avg']} median={v['median']} max={v['max']}\n")

        if analysis.get("question_form"):
            f.write(f"\nHukuki soru formu oranı        : %{analysis['question_form']['question_form_rate']}\n")

        if analysis.get("top_keywords"):
            f.write("\nEn sık anahtarlar:\n")
            for k, v in analysis["top_keywords"][:15]:
                f.write(f"  {k:<45}: {v}\n")

        if analysis.get("top_mevzuat"):
            f.write("\nEn sık mevzuat:\n")
            for k, v in analysis["top_mevzuat"][:15]:
                f.write(f"  {k:<70}: {v}\n")

        if analysis.get("warnings"):
            f.write("\nUyarılar:\n")
            for w in analysis["warnings"]:
                f.write(f"  - {w}\n")
        else:
            f.write("\nUyarılar: Yok\n")

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("182 v2 - PRODUCTION DRIFT ANALIZ MOTORU RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Kaynak tipi                   : {source_type}\n")
        f.write(f"Input                         : {input_path}\n\n")

        f.write("FINAL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam kart                    : {len(cards)}\n")
        f.write(f"Yeni model kart                : {len(new_cards)}\n")
        f.write(f"Eski model kart                : {len(legacy_cards)}\n")
        f.write(f"Final drift skoru              : {final_score} / 100\n")
        f.write(f"Final drift kararı             : {final_decision}\n")
        f.write(f"183'e geçilebilir mi           : {'EVET' if ready_for_183 else 'HAYIR'}\n")
        if legacy_gap_note:
            f.write(f"Not                            : {legacy_gap_note}\n")

        if final_warnings:
            f.write("\nFinal uyarılar:\n")
            for w in final_warnings:
                f.write(f"- {w}\n")

        write_section(f, "YENI MODEL ANALIZI", new_analysis)
        write_section(f, "GENEL HAVUZ ANALIZI", all_analysis)
        write_section(f, "ESKI MODEL ANALIZI", legacy_analysis)

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Detay JSONL                    : {detail_path}\n")
        f.write(f"State JSON                     : {state_path}\n")
        f.write(f"Rapor                          : {rapor_path}\n")

    print("\n182 v2 PRODUCTION DRIFT ANALIZI TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam kart                    : {len(cards)}")
    print(f"Yeni model kart                : {len(new_cards)}")
    print(f"Eski model kart                : {len(legacy_cards)}")
    print(f"Yeni model drift skoru         : {new_analysis.get('drift_score')} / 100")
    print(f"Genel havuz drift skoru        : {all_analysis.get('drift_score')} / 100")
    print(f"Final drift kararı             : {final_decision}")
    print(f"Final uyarı sayısı             : {len(final_warnings)}")
    print(f"183'e geçilebilir mi           : {'EVET' if ready_for_183 else 'HAYIR'}")

    print("\nDosyalar:")
    print(detail_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
