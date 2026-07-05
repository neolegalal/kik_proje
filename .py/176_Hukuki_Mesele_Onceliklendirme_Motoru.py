# -*- coding: utf-8 -*-
"""
176 - HUKUKI MESELE ONCELIKLENDIRME MOTORU

Amaç:
- 175 v2 AI kapsam analizinin detay JSONL çıktısını okur.
- Karar bazında tespit edilen hukuki meseleleri önem puanına göre sınıflandırır.
- Hangi meselelerin mutlaka karta dönüşmesi gerektiğini belirler.
- Eksik önemli meseleleri ve düşük öncelikli/tali meseleleri ayırır.
- 177 Akıllı Kart Üretim Planlayıcısı için plan çıktısı üretir.

Kullanım:
  python ".py\\176_Hukuki_Mesele_Onceliklendirme_Motoru.py"

Belirli 175 v2 detay dosyası için:
  python ".py\\176_Hukuki_Mesele_Onceliklendirme_Motoru.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\production_logs\\175_v2_ai_kapsam_detay_YYYYMMDD_HHMMSS.jsonl"

Not:
- API kullanmaz.
- DB'ye yazmaz.
- 175 v2'nin AI analiz sonucunu üretim planına dönüştürür.
"""

import os
import sys
import glob
import json
from datetime import datetime
from collections import Counter, defaultdict


BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

INPUT_PATTERN = os.path.join(LOG_DIR, "175_v2_ai_kapsam_detay_*.jsonl")

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
                rows.append({"status": "JSON_ERROR", "line_no": line_no, "error": str(e), "raw": line[:500]})
    return rows


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def importance_band(score):
    try:
        s = int(float(score))
    except Exception:
        s = 0
    if s >= 90:
        return "KRITIK"
    if s >= 75:
        return "ONEMLI"
    if s >= 50:
        return "ORTA"
    return "TALI"


def should_card(score, flag=True):
    try:
        s = int(float(score))
    except Exception:
        s = 0
    return bool(flag) and s >= 75


def norm_bool(v):
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.strip().lower() in {"true", "evet", "yes", "1"}
    return bool(v)


def analyze_row(row):
    karar_no = row.get("karar_no", "")
    judgement = row.get("judgement", {}) if isinstance(row.get("judgement"), dict) else {}
    legal_issues = judgement.get("legal_issues", [])
    card_coverage = judgement.get("card_coverage", [])
    missing_issues = judgement.get("missing_issues", [])
    duplicate_cards = judgement.get("duplicate_cards", [])

    if not isinstance(legal_issues, list):
        legal_issues = []
    if not isinstance(card_coverage, list):
        card_coverage = []
    if not isinstance(missing_issues, list):
        missing_issues = []
    if not isinstance(duplicate_cards, list):
        duplicate_cards = []

    covered_issue_ids = set()
    low_quality_covered = []

    for cc in card_coverage:
        if not isinstance(cc, dict):
            continue
        ids = cc.get("covered_issue_ids", [])
        if not isinstance(ids, list):
            ids = [ids]
        for x in ids:
            try:
                covered_issue_ids.add(int(x))
            except Exception:
                pass
        try:
            cq = int(float(cc.get("coverage_quality", 0)))
        except Exception:
            cq = 0
        if cq < 75:
            low_quality_covered.append(cc)

    required = []
    optional = []
    covered_required = []
    missing_required = []
    high_value_missing = []

    issue_by_id = {}

    for issue in legal_issues:
        if not isinstance(issue, dict):
            continue
        try:
            issue_id = int(issue.get("issue_id"))
        except Exception:
            continue
        issue_by_id[issue_id] = issue

        imp = int(float(issue.get("importance", 0) or 0))
        flag = norm_bool(issue.get("should_have_card", True))
        band = importance_band(imp)

        item = {
            "issue_id": issue_id,
            "issue_title": str(issue.get("issue_title", "")).strip(),
            "issue_question": str(issue.get("issue_question", "")).strip(),
            "importance": imp,
            "band": band,
            "legal_basis": issue.get("legal_basis", []),
            "source_evidence": str(issue.get("source_evidence", "")).strip(),
            "should_have_card": should_card(imp, flag),
            "covered": issue_id in covered_issue_ids,
        }

        if item["should_have_card"]:
            required.append(item)
            if item["covered"]:
                covered_required.append(item)
            else:
                missing_required.append(item)
                if imp >= 90:
                    high_value_missing.append(item)
        else:
            optional.append(item)

    # 175 v2'nin explicit missing_issues listesini de ek sinyal olarak kullan.
    explicit_missing_ids = set()
    for mi in missing_issues:
        if not isinstance(mi, dict):
            continue
        try:
            mid = int(mi.get("issue_id"))
            explicit_missing_ids.add(mid)
        except Exception:
            pass

    # Explicit missing ama required listede yoksa ayrıca işaretle.
    for mid in explicit_missing_ids:
        if mid in issue_by_id and all(x["issue_id"] != mid for x in missing_required):
            issue = issue_by_id[mid]
            imp = int(float(issue.get("importance", 0) or 0))
            if imp >= 75:
                missing_required.append({
                    "issue_id": mid,
                    "issue_title": str(issue.get("issue_title", "")).strip(),
                    "issue_question": str(issue.get("issue_question", "")).strip(),
                    "importance": imp,
                    "band": importance_band(imp),
                    "legal_basis": issue.get("legal_basis", []),
                    "source_evidence": str(issue.get("source_evidence", "")).strip(),
                    "should_have_card": True,
                    "covered": False,
                    "explicit_missing": True,
                })

    required_count = len(required)
    covered_required_count = len(covered_required)
    missing_required_count = len(missing_required)

    priority_coverage = round((covered_required_count / required_count) * 100, 2) if required_count else 100.0

    # Üretim kararı
    if high_value_missing:
        decision = "REGENERATE_REQUIRED"
        reason = "90+ önem puanlı hukuki meselelerden en az biri karta dönüşmemiş."
    elif missing_required_count > 0:
        decision = "REVIEW_OR_SUPPLEMENT"
        reason = "75+ önem puanlı bazı meseleler eksik veya düşük kapsamda."
    elif duplicate_cards:
        decision = "PASS_WITH_DUPLICATE_REVIEW"
        reason = "Önemli meseleler kapsanmış; ancak tekrar eden kart ihtimali var."
    elif low_quality_covered:
        decision = "PASS_WITH_QUALITY_REVIEW"
        reason = "Meseleler kapsanmış; bazı kartların coverage kalitesi düşük."
    else:
        decision = "PASS"
        reason = "Önemli hukuki meseleler yeterli kapsamda karta dönüşmüş."

    return {
        "karar_no": karar_no,
        "coverage_score": judgement.get("coverage_score"),
        "web_score": judgement.get("web_score"),
        "rag_score": judgement.get("rag_score"),
        "ai_decision": judgement.get("decision"),
        "required_issue_count": required_count,
        "covered_required_issue_count": covered_required_count,
        "missing_required_issue_count": missing_required_count,
        "priority_coverage": priority_coverage,
        "required_issues": required,
        "optional_issues": optional,
        "missing_required_issues": missing_required,
        "high_value_missing_issues": high_value_missing,
        "duplicate_cards": duplicate_cards,
        "low_quality_covered_cards": low_quality_covered,
        "production_decision": decision,
        "decision_reason": reason,
    }


def main():
    print("=" * 80)
    print("176 - HUKUKI MESELE ONCELIKLENDIRME MOTORU")
    print("=" * 80)

    run_tag = tag()

    if len(sys.argv) >= 2:
        input_path = sys.argv[1]
    else:
        input_path = latest_file(INPUT_PATTERN)

    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError("175 v2 detay JSONL bulunamadı.")

    rows = read_jsonl(input_path)

    detail_path = os.path.join(LOG_DIR, f"176_onceliklendirme_detay_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"176_onceliklendirme_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"176_hukuki_mesele_onceliklendirme_raporu_{run_tag}.txt")

    analyses = []
    decision_counter = Counter()
    issue_band_counter = Counter()
    all_missing_required = []

    for row in rows:
        if row.get("status") != "OK":
            continue
        analysis = analyze_row(row)
        analyses.append(analysis)
        append_jsonl(detail_path, analysis)

        decision_counter[analysis["production_decision"]] += 1

        for issue in analysis["required_issues"] + analysis["optional_issues"]:
            issue_band_counter[issue["band"]] += 1

        for mi in analysis["missing_required_issues"]:
            all_missing_required.append({
                "karar_no": analysis["karar_no"],
                **mi
            })

    total_decisions = len(analyses)
    avg_priority_coverage = round(sum(a["priority_coverage"] for a in analyses) / total_decisions, 2) if total_decisions else 0
    needs_regenerate = decision_counter["REGENERATE_REQUIRED"]
    needs_review = decision_counter["REVIEW_OR_SUPPLEMENT"]

    # 177'ye geçiş:
    # - REGENERATE_REQUIRED yoksa
    # - ortalama priority coverage >= 90 ise
    ready_for_177 = total_decisions > 0 and needs_regenerate == 0 and avg_priority_coverage >= 90

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_path": input_path,
        "decision_count": total_decisions,
        "avg_priority_coverage": avg_priority_coverage,
        "production_decision_counts": dict(decision_counter),
        "issue_band_counts": dict(issue_band_counter),
        "missing_required_count": len(all_missing_required),
        "needs_regenerate_count": needs_regenerate,
        "needs_review_count": needs_review,
        "ready_for_177": ready_for_177,
        "detail_path": detail_path,
        "rapor_path": rapor_path,
        "next_step": "177_Akilli_Kart_Uretim_Planlayicisi.py",
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("176 - HUKUKI MESELE ONCELIKLENDIRME MOTORU RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input                         : {input_path}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Karar sayısı                   : {total_decisions}\n")
        f.write(f"Ortalama öncelikli kapsam      : {avg_priority_coverage} / 100\n")
        f.write(f"Üretim kararları               : {dict(decision_counter)}\n")
        f.write(f"Mesele önem dağılımı           : {dict(issue_band_counter)}\n")
        f.write(f"Eksik zorunlu mesele           : {len(all_missing_required)}\n")
        f.write(f"Yeniden üretim gereken karar   : {needs_regenerate}\n")
        f.write(f"Review/supplement gereken      : {needs_review}\n")
        f.write(f"177'ye geçilebilir mi          : {'EVET' if ready_for_177 else 'HAYIR'}\n\n")

        f.write("KARAR BAZLI ÖNCELIKLENDIRME\n")
        f.write("-" * 80 + "\n")
        for a in analyses:
            f.write(f"\nKarar: {a['karar_no']} | Öncelikli kapsam: {a['priority_coverage']} | Karar: {a['production_decision']}\n")
            f.write(f"Neden: {a['decision_reason']}\n")
            f.write(f"Zorunlu mesele: {a['required_issue_count']} | Kapsanan: {a['covered_required_issue_count']} | Eksik: {a['missing_required_issue_count']}\n")

            f.write("Zorunlu meseleler:\n")
            for issue in a["required_issues"]:
                f.write(f"  - [{issue['band']}] {issue['importance']} | {'KAPSANDI' if issue['covered'] else 'EKSİK'} | {issue['issue_title']}\n")

            if a["optional_issues"]:
                f.write("Opsiyonel/tali meseleler:\n")
                for issue in a["optional_issues"]:
                    f.write(f"  - [{issue['band']}] {issue['importance']} | {issue['issue_title']}\n")

            if a["missing_required_issues"]:
                f.write("Eksik zorunlu meseleler:\n")
                for issue in a["missing_required_issues"]:
                    f.write(f"  - {issue['importance']} | {issue['issue_title']} | Soru: {issue.get('issue_question','')}\n")

            if a["duplicate_cards"]:
                f.write("Tekrar kontrolü gereken kartlar:\n")
                for d in a["duplicate_cards"]:
                    f.write(f"  - Kart {d.get('card_a')} / Kart {d.get('card_b')}: {d.get('similarity_reason')}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Detay JSONL                    : {detail_path}\n")
        f.write(f"State JSON                     : {state_path}\n")
        f.write(f"Rapor                          : {rapor_path}\n")

    print("\n176 ONCELIKLENDIRME TAMAMLANDI")
    print("-" * 80)
    print(f"Karar sayısı                   : {total_decisions}")
    print(f"Ortalama öncelikli kapsam      : {avg_priority_coverage} / 100")
    print(f"Üretim kararları               : {dict(decision_counter)}")
    print(f"Eksik zorunlu mesele           : {len(all_missing_required)}")
    print(f"Yeniden üretim gereken karar   : {needs_regenerate}")
    print(f"177'ye geçilebilir mi          : {'EVET' if ready_for_177 else 'HAYIR'}")
    print("\nDosyalar:")
    print(detail_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
