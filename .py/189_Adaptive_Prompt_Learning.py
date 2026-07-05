# -*- coding: utf-8 -*-
"""
189 - ADAPTIVE PROMPT LEARNING

Amaç:
- Son üretimlerdeki kalite raporlarını/loglarını analiz eder.
- 171 ve 177 kaynaklarından tekrar eden kalite sorunlarını çıkarır.
- 168 üretim prompt'una eklenebilecek "öğrenilmiş üretim kuralları" üretir.
- Otomatik olarak 168 dosyasını değiştirmez; güvenli öneri dosyası üretir.
- DB'ye yazmaz, API kullanmaz.

Kullanım:
  python ".py\\189_Adaptive_Prompt_Learning.py"
  python ".py\\189_Adaptive_Prompt_Learning.py" 20
"""

import os
import re
import sys
import json
import glob
from datetime import datetime
from collections import Counter, defaultdict


BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
PROMPT_DIR = os.path.join(BASE_DIR, "prompt_learning")

os.makedirs(STATE_DIR, exist_ok=True)
os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(PROMPT_DIR, exist_ok=True)


QUALITY_RULES = {
    "KONU_OZETI_COK_KISA": {
        "severity": "HIGH",
        "field": "konu_ozeti",
        "rule": "konu_ozeti en az 2 cümle ve tercihen 35-80 kelime olmalıdır.",
        "prompt": "konu_ozeti alanında sadece kısa bir sonuç cümlesi yazma. En az iki cümle kur: ilk cümlede olay/iddia, ikinci cümlede Kurulun incelediği hukuki mesele anlatılsın.",
    },
    "SONUC_OZETI_COK_KISA": {
        "severity": "HIGH",
        "field": "sonuc_ozeti",
        "rule": "sonuc_ozeti Kurulun vardığı sonucu, gerekçeyi ve işlem sonucunu açıkça göstermelidir.",
        "prompt": "sonuc_ozeti alanını tek kısa cümle bırakma. Kurulun tespitini, hukuki sonucunu ve başvurunun/ihalenin akıbetini açıkça yaz.",
    },
    "ANAHTAR_YETERSIZ": {
        "severity": "HIGH",
        "field": "anahtar",
        "rule": "anahtar listesi en az 5, tercihen 6-8 adet anlamlı terim içermelidir.",
        "prompt": "anahtar alanı mutlaka liste olsun ve en az 5 öğe içersin. Genel kelimeler yerine hukuki mesele, belge türü, usul, sonuç ve mevzuat terimlerini kullan.",
    },
    "MEVZUAT_YOK": {
        "severity": "MEDIUM",
        "field": "mevzuat",
        "rule": "mevzuat alanı karar metninde açık dayanak varsa boş bırakılmamalıdır.",
        "prompt": "Kararda açık mevzuat dayanağı geçiyorsa mevzuat alanını boş bırakma. Kanun, yönetmelik, tebliğ ve madde numaralarını mümkün olduğunca listele.",
    },
    "KONU_OZETI_SONUCA_KAYMIS_OLABILIR": {
        "severity": "MEDIUM",
        "field": "konu_ozeti",
        "rule": "konu_ozeti sonuç özeti gibi yazılmamalı; olay ve incelenen hukuki meseleyi anlatmalıdır.",
        "prompt": "konu_ozeti içinde Kurulun nihai kararını öne çıkarma. Bu alan kararın ne hakkında olduğunu ve hangi hukuki meselenin incelendiğini anlatmalıdır.",
    },
    "SONUC_TIPI_STANDART_DISI": {
        "severity": "MEDIUM",
        "field": "sonuc_tipi",
        "rule": "sonuc_tipi standart değerlerden biri olmalıdır.",
        "prompt": "sonuc_tipi alanında standart ve kısa değer kullan: RET, KABUL, DÜZELTİCİ İŞLEM, İPTAL, KISMEN KABUL veya KARAR VERİLMESİNE YER OLMADI.",
    },
    "EMSAL_ILKE_SONUC_TEKRARI_OLABILIR": {
        "severity": "MEDIUM",
        "field": "emsal_ilke",
        "rule": "emsal_ilke sonuç özetinin tekrarı değil, genellenebilir hukuki ilke olmalıdır.",
        "prompt": "emsal_ilke alanında olaya özel sonucu tekrar etme. Benzer ihalelerde uygulanabilecek genel ve danışmanlıkta kullanılabilir hukuki ilke yaz.",
    },
    "HUKUKI_SORUDA_KURUM_SIRKET_ADI_OLABILIR": {
        "severity": "LOW",
        "field": "hukuki_soru",
        "rule": "hukuki_soru kurum/şirket adı içermeden genelleştirilmelidir.",
        "prompt": "hukuki_soru alanında idare, şirket, kişi veya yer adı kullanma. Soruyu danışmanlıkta tekrar kullanılabilecek genel bir soru haline getir.",
    },
    "BASLIKTA_KURUM_SIRKET_ADI_OLABILIR": {
        "severity": "LOW",
        "field": "baslik",
        "rule": "baslik kurum/şirket adı içermeden yayınlanabilir olmalıdır.",
        "prompt": "baslik alanında idare, şirket veya kişi adı kullanma. Başlığı hukuki mesele odaklı ve webde yayınlanabilir şekilde yaz.",
    },
}


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def safe(v):
    return "" if v is None else str(v).strip()


def parse_n():
    if len(sys.argv) >= 2:
        try:
            return max(1, int(sys.argv[1]))
        except Exception:
            pass
    return 20


def latest_files(pattern, n):
    files = glob.glob(pattern)
    files = sorted(files, key=os.path.getmtime, reverse=True)
    return files[:n]


def read_jsonl(path):
    rows = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except Exception:
                    rows.append({"_json_error": True, "_line_no": line_no, "_raw": line[:500]})
    except Exception:
        pass
    return rows


def extract_issues_from_171_detail(path):
    issues = Counter()
    warnings = Counter()
    examples = defaultdict(list)

    for row in read_jsonl(path):
        if row.get("_json_error"):
            continue

        row_issues = row.get("issues") or row.get("block_reasons") or row.get("sebepler") or []
        row_warnings = row.get("warnings") or row.get("warning_reasons") or []

        if isinstance(row_issues, str):
            row_issues = re.findall(r"[A-ZÇĞİÖŞÜ_]{4,}", row_issues)
        if isinstance(row_warnings, str):
            row_warnings = re.findall(r"[A-ZÇĞİÖŞÜ_]{4,}", row_warnings)

        for x in row_issues or []:
            x = safe(x)
            if x:
                issues[x] += 1
                if len(examples[x]) < 5:
                    examples[x].append({
                        "source": os.path.basename(path),
                        "karar_no": row.get("karar_no"),
                        "card_index": row.get("card_index") or row.get("kart_index"),
                        "baslik": row.get("baslik") or row.get("title"),
                    })

        for x in row_warnings or []:
            x = safe(x)
            if x:
                warnings[x] += 1
                if len(examples[x]) < 5:
                    examples[x].append({
                        "source": os.path.basename(path),
                        "karar_no": row.get("karar_no"),
                        "card_index": row.get("card_index") or row.get("kart_index"),
                        "baslik": row.get("baslik") or row.get("title"),
                    })

    return issues, warnings, examples


def extract_from_text_report(path):
    issues = Counter()
    warnings = Counter()
    try:
        text = open(path, "r", encoding="utf-8").read()
    except Exception:
        return issues, warnings

    block_section = re.search(r"BLOCK SEBEPLERI\s*-+\s*(.*?)(?:WARNING SEBEPLERI|KARAR BAZLI|DOSYALAR|$)", text, flags=re.S)
    if block_section:
        for name, count in re.findall(r"([A-ZÇĞİÖŞÜ_]{4,})\s*:\s*(\d+)", block_section.group(1)):
            issues[name] += int(count)

    warn_section = re.search(r"WARNING SEBEPLERI\s*-+\s*(.*?)(?:KARAR BAZLI|ORNEK|DOSYALAR|$)", text, flags=re.S)
    if warn_section:
        for name, count in re.findall(r"([A-ZÇĞİÖŞÜ_]{4,})\s*:\s*(\d+)", warn_section.group(1)):
            warnings[name] += int(count)

    return issues, warnings


def extract_177_risks(path):
    risks = Counter()
    examples = defaultdict(list)

    for row in read_jsonl(path):
        if row.get("_json_error"):
            continue
        review = row.get("review")
        karar_no = row.get("karar_no")
        if not isinstance(review, dict):
            continue

        card_reviews = review.get("card_reviews", [])
        if not isinstance(card_reviews, list):
            continue

        for cr in card_reviews:
            decision = safe(cr.get("decision")).upper()
            halluc = safe(cr.get("hallucination_risk")).upper()
            overgen = safe(cr.get("overgeneralization_risk")).upper()
            issues = cr.get("issues") or []

            if decision == "FAIL":
                risks["177_FAIL_CARD"] += 1
            if decision == "WARNING":
                risks["177_WARNING_CARD"] += 1
            if halluc == "HIGH":
                risks["177_HIGH_HALLUCINATION"] += 1
            if overgen == "HIGH":
                risks["177_HIGH_OVERGENERALIZATION"] += 1

            for issue in issues:
                issue = safe(issue)
                if issue:
                    key = "177_" + re.sub(r"[^A-Za-zÇĞİÖŞÜçğıöşü0-9]+", "_", issue.upper()).strip("_")[:80]
                    risks[key] += 1

            if decision in {"FAIL", "WARNING"} or halluc == "HIGH" or overgen == "HIGH":
                key = "177_REVIEW_EXAMPLE"
                if len(examples[key]) < 10:
                    examples[key].append({
                        "source": os.path.basename(path),
                        "karar_no": karar_no,
                        "card_index": cr.get("card_index"),
                        "decision": decision,
                        "hallucination": halluc,
                        "overgeneralization": overgen,
                        "issues": issues,
                    })

    return risks, examples


def collect_inputs(n):
    return {
        "171_details": latest_files(os.path.join(LOG_DIR, "171_v2_mini_kalite_detay_*.jsonl"), n),
        "171_reports": latest_files(os.path.join(RAPOR_DIR, "171_v2_mini_uretim_kalite_kontrol_raporu_*.txt"), n),
        "177_details": latest_files(os.path.join(LOG_DIR, "177_hukuki_dogruluk_detay_*.jsonl"), n),
    }


def build_learning(issue_counter, warning_counter, risk_counter):
    combined = Counter()
    for k, v in issue_counter.items():
        combined[k] += v * 3
    for k, v in warning_counter.items():
        combined[k] += v
    for k, v in risk_counter.items():
        combined[k] += v * 4

    recommendations = []

    for key, weighted in combined.most_common():
        rule = QUALITY_RULES.get(key)
        if rule:
            recommendations.append({
                "issue": key,
                "weighted_score": weighted,
                "severity": rule["severity"],
                "field": rule["field"],
                "rule": rule["rule"],
                "prompt_instruction": rule["prompt"],
            })
        elif key.startswith("177_"):
            recommendations.append({
                "issue": key,
                "weighted_score": weighted,
                "severity": "HIGH" if "FAIL" in key or "HIGH" in key else "MEDIUM",
                "field": "hukuki_dogruluk",
                "rule": "177 hakeminde tekrar eden hukuki doğruluk riski var; promptta dayanak metne bağlı kalma ve aşırı genellemeden kaçınma vurgusu artırılmalıdır.",
                "prompt_instruction": "Karar metninde açıkça bulunmayan hukuki sonucu, mevzuat dayanağını veya genelleştirilmiş ilkeyi üretme. Emsal ilke karar metnindeki gerekçeyi aşmamalıdır.",
            })
        else:
            recommendations.append({
                "issue": key,
                "weighted_score": weighted,
                "severity": "MEDIUM",
                "field": "genel",
                "rule": "Tekrar eden kalite sinyali incelenmelidir.",
                "prompt_instruction": f"{key} sorununu azaltacak şekilde ilgili alanı daha açık, mevzuata bağlı ve yeterli ayrıntıda üret.",
            })

    return recommendations


def make_prompt_rules(recommendations, max_rules=12):
    lines = []
    lines.append("ADAPTIVE PROMPT LEARNING - ÖĞRENİLMİŞ ÜRETİM KURALLARI")
    lines.append("=" * 80)
    lines.append("")
    lines.append("Bu kurallar son üretim kalite loglarından otomatik çıkarılmıştır.")
    lines.append("168 üretim promptuna manuel olarak eklenmek üzere öneridir.")
    lines.append("")

    selected = recommendations[:max_rules]
    for i, rec in enumerate(selected, start=1):
        lines.append(f"{i}. {rec['issue']}")
        lines.append(f"   Önem       : {rec['severity']}")
        lines.append(f"   Alan       : {rec['field']}")
        lines.append(f"   Kural      : {rec['rule']}")
        lines.append(f"   Prompt     : {rec['prompt_instruction']}")
        lines.append("")

    lines.append("-" * 80)
    lines.append("ÖNERİLEN GENEL PROMPT EKİ")
    lines.append("-" * 80)
    lines.append("")
    lines.append("ÜRETİM KALİTESİ İÇİN ZORUNLU EK KURALLAR:")
    lines.append("")
    for rec in selected:
        lines.append(f"- {rec['prompt_instruction']}")
    lines.append("")
    lines.append("Bu kurallar mevcut JSON formatını değiştirmez; sadece alanların daha kaliteli doldurulmasını sağlar.")
    return "\n".join(lines)


def main():
    print("=" * 80)
    print("189 - ADAPTIVE PROMPT LEARNING")
    print("=" * 80)

    run_tag = tag()
    n = parse_n()

    print(f"\nAnaliz edilecek son dosya sayısı: {n}")
    print("-" * 80)

    files = collect_inputs(n)

    issue_counter = Counter()
    warning_counter = Counter()
    risk_counter = Counter()
    examples = defaultdict(list)

    for path in files["171_details"]:
        issues, warnings, ex = extract_issues_from_171_detail(path)
        issue_counter.update(issues)
        warning_counter.update(warnings)
        for k, vals in ex.items():
            examples[k].extend(vals)

    for path in files["171_reports"]:
        issues, warnings = extract_from_text_report(path)
        issue_counter.update(issues)
        warning_counter.update(warnings)

    for path in files["177_details"]:
        risks, ex = extract_177_risks(path)
        risk_counter.update(risks)
        for k, vals in ex.items():
            examples[k].extend(vals)

    recommendations = build_learning(issue_counter, warning_counter, risk_counter)

    prompt_rules_text = make_prompt_rules(recommendations)
    rules_path = os.path.join(PROMPT_DIR, f"189_prompt_rules_{run_tag}.txt")
    patch_path = os.path.join(PROMPT_DIR, f"189_prompt_patch_suggestion_{run_tag}.txt")
    state_path = os.path.join(STATE_DIR, f"189_adaptive_prompt_learning_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"189_adaptive_prompt_learning_raporu_{run_tag}.txt")

    with open(rules_path, "w", encoding="utf-8") as f:
        f.write(prompt_rules_text)

    with open(patch_path, "w", encoding="utf-8") as f:
        f.write("# 168 PROMPT ICIN ONERILEN EK BLOK\n")
        f.write("# Bu metni 168 uretim promptunun kalite kurallari bolumune manuel ekleyebilirsin.\n\n")
        f.write('ADAPTIVE_QUALITY_RULES = r"""\n')
        for rec in recommendations[:12]:
            f.write(f"- {rec['prompt_instruction']}\n")
        f.write('"""\n')

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "file_limit": n,
        "input_files": files,
        "issue_counter": dict(issue_counter),
        "warning_counter": dict(warning_counter),
        "risk_counter": dict(risk_counter),
        "recommendations": recommendations[:30],
        "rules_path": rules_path,
        "patch_path": patch_path,
        "rapor_path": rapor_path,
        "ready_for_190": True,
        "next_step": "190_Production_Supervisor.py",
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("189 - ADAPTIVE PROMPT LEARNING RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Analiz edilen son dosya sayısı : {n}\n")
        f.write("190'a geçilebilir mi           : EVET\n\n")

        f.write("EN SIK 171 BLOCK SEBEPLERI\n")
        f.write("-" * 80 + "\n")
        for k, v in issue_counter.most_common(20):
            f.write(f"{k:<45}: {v}\n")

        f.write("\nEN SIK 171 WARNING SEBEPLERI\n")
        f.write("-" * 80 + "\n")
        for k, v in warning_counter.most_common(20):
            f.write(f"{k:<45}: {v}\n")

        f.write("\n177 HUKUKI DOGRULUK RISKLERI\n")
        f.write("-" * 80 + "\n")
        for k, v in risk_counter.most_common(20):
            f.write(f"{k:<60}: {v}\n")

        f.write("\nÖNERILEN PROMPT IYILESTIRMELERI\n")
        f.write("-" * 80 + "\n")
        for i, rec in enumerate(recommendations[:15], start=1):
            f.write(f"{i}. {rec['issue']} | skor={rec['weighted_score']} | önem={rec['severity']} | alan={rec['field']}\n")
            f.write(f"   Kural : {rec['rule']}\n")
            f.write(f"   Prompt: {rec['prompt_instruction']}\n\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Prompt rules                  : {rules_path}\n")
        f.write(f"Patch suggestion              : {patch_path}\n")
        f.write(f"State                         : {state_path}\n")
        f.write(f"Rapor                         : {rapor_path}\n")

    print("\n189 ADAPTIVE PROMPT LEARNING TAMAMLANDI")
    print("-" * 80)
    print(f"171 block issue çeşidi         : {len(issue_counter)}")
    print(f"171 warning issue çeşidi       : {len(warning_counter)}")
    print(f"177 risk çeşidi                : {len(risk_counter)}")
    print(f"Öneri sayısı                   : {len(recommendations)}")
    print("190'a geçilebilir mi           : EVET")

    print("\nEn yüksek öncelikli öneriler:")
    for rec in recommendations[:5]:
        print(f"- {rec['issue']} | skor={rec['weighted_score']} | {rec['field']}")

    print("\nDosyalar:")
    print(rules_path)
    print(patch_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
