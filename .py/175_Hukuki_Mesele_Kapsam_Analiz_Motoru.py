# -*- coding: utf-8 -*-
"""
175 - HUKUKI MESELE KAPSAM ANALIZ MOTORU

Amaç:
- 168 production output JSONL dosyasındaki kartları karar bazında inceler.
- Aynı karar içindeki kartların hangi hukuki meseleleri kapsadığını çıkarır.
- Karar bazında coverage / kapsam kontrolü yapar.
- Bu sürüm API kullanmaz; mevcut kartlar üzerinden kural tabanlı kapsam analizi yapar.
- 176/177/178 için temel veri üretir.

Kullanım:
  python ".py\\175_Hukuki_Mesele_Kapsam_Analiz_Motoru.py"

Belirli 168 çıktısı için:
  python ".py\\175_Hukuki_Mesele_Kapsam_Analiz_Motoru.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\uretim_output\\168_production_output_20260630_182904.jsonl"

Not:
- DB'ye yazmaz.
- API kullanmaz.
- Karar kapsamını tam karar metninden değil, üretilen kartlardan ve bilinen mesele ipuçlarından analiz eder.
- Amaç büyük üretim öncesi kart çeşitliliği ve kapsam kalitesini ölçmektir.
"""

import os
import re
import sys
import json
import glob
from datetime import datetime
from collections import defaultdict, Counter


BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

INPUT_PATTERN = os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


ISSUE_TAXONOMY = [
    {
        "code": "ASIRI_DUSUK_TEKLIF",
        "label": "Aşırı düşük teklif",
        "keywords": ["aşırı düşük", "asiri dusuk", "düşük teklif", "teklif sorgulama", "yazılı açıklama"],
        "priority": 92,
    },
    {
        "code": "KENDI_MALI_EKIPMAN",
        "label": "Makine/ekipman kendi malı olma şartı",
        "keywords": ["kendi malı", "kendi mali", "araçların kendi malı", "makine ekipman", "model yılı", "model şartı"],
        "priority": 96,
    },
    {
        "code": "EK_BELGE_TEYIT_YAZISI",
        "label": "Mevzuatta öngörülmeyen ek belge / teyit yazısı",
        "keywords": ["teyit yazısı", "trafik şube", "ek belge", "noter tasdikli", "tevsik"],
        "priority": 93,
    },
    {
        "code": "BENZER_IS",
        "label": "Benzer iş tanımı",
        "keywords": ["benzer iş", "benzer is", "birlikte yapılması", "tamamının birlikte", "iş deneyim"],
        "priority": 97,
    },
    {
        "code": "YETKI_BELGESI",
        "label": "Yetki belgesi / faaliyet izni",
        "keywords": ["yetki belgesi", "k-1", "k1", "karayolu taşıma", "taşıma kanunu", "ulaştırma"],
        "priority": 95,
    },
    {
        "code": "DOKUMAN_BEDELI_REKABET",
        "label": "Doküman bedeli ve rekabet",
        "keywords": ["doküman bedeli", "dokuman bedeli", "basım maliyeti", "rekabeti engellemeyecek", "doküman satın"],
        "priority": 88,
    },
    {
        "code": "REKABET_TEMEL_ILKELER",
        "label": "Rekabet / temel ilkeler",
        "keywords": ["rekabet", "temel ilkeler", "4734 m.5", "katılımı sınırlayıcı", "katılımı zorlaştırıcı"],
        "priority": 90,
    },
    {
        "code": "GIDA_BELGESI",
        "label": "Gıda sicil / üretim belgeleri",
        "keywords": ["gıda sicil", "gıda üretim", "tarım", "sağlık bakanlığı", "5179", "560 sayılı"],
        "priority": 94,
    },
    {
        "code": "ANAHTAR_TEKNIK_PERSONEL",
        "label": "Anahtar teknik personel / personel belgesi",
        "keywords": ["anahtar teknik personel", "ustalık belgesi", "aşçı başı", "personel belgesi", "taahhütname"],
        "priority": 96,
    },
    {
        "code": "DUZELTICI_ISLEM_IPTAL",
        "label": "Düzeltici işlemle giderilememe / iptal",
        "keywords": ["düzeltici işlem", "giderilemeyecek", "ihale işlemlerinin iptali", "ihale kararının iptali", "iptaline karar"],
        "priority": 82,
    },
    {
        "code": "KARAR_VERILMESINE_YER_YOK",
        "label": "Karar verilmesine yer olmadığı",
        "keywords": ["karar verilmesine yer olmadığı", "yeni bir karar alınmasına gerek", "önceki karar", "daha önce yapılan"],
        "priority": 55,
    },
]


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


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def norm(s):
    s = "" if s is None else str(s)
    s = s.lower()
    tr = str.maketrans("çğıöşüâîû", "cgiosuaiu")
    return s.translate(tr)


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
    return [p.strip() for p in re.split(r"[,;]\s*", s) if p.strip()]


def card_text(card):
    parts = [
        card.get("baslik", ""),
        card.get("hukuki_soru", ""),
        card.get("konu_ozeti", ""),
        card.get("sonuc_ozeti", ""),
        card.get("sonuc", ""),
        card.get("emsal_ilke", ""),
        " ".join(parse_list(card.get("anahtar"))),
        " ".join(parse_list(card.get("mevzuat"))),
    ]
    return " ".join(str(p) for p in parts if p)


def flatten_cards(rows):
    by_decision = defaultdict(list)
    for row_idx, row in enumerate(rows, start=1):
        if "_json_error" in row or row.get("status") != "OK":
            continue
        karar_no = str(row.get("karar_no") or row.get("orijinal_karar_no") or "").strip()
        cards = row.get("kartlar", [])
        if not isinstance(cards, list):
            continue
        for i, c in enumerate(cards, start=1):
            if not isinstance(c, dict):
                continue
            card = dict(c)
            card["_row_index"] = row_idx
            card["_card_index"] = i
            card["_karar_no"] = karar_no
            by_decision[karar_no].append(card)
    return by_decision


def detect_issue_codes(text):
    nt = norm(text)
    found = []
    for item in ISSUE_TAXONOMY:
        hit_count = 0
        for kw in item["keywords"]:
            if norm(kw) in nt:
                hit_count += 1
        if hit_count:
            found.append({
                "code": item["code"],
                "label": item["label"],
                "priority": item["priority"],
                "hit_count": hit_count,
            })
    return sorted(found, key=lambda x: (-x["hit_count"], -x["priority"]))


def primary_issue(card):
    issues = detect_issue_codes(card_text(card))
    if not issues:
        return {
            "code": "DIGER",
            "label": "Diğer / sınıflandırılamayan mesele",
            "priority": 60,
            "hit_count": 0,
        }
    return issues[0]


def text_words(s):
    ws = set(re.findall(r"[a-zA-ZçğıöşüÇĞİÖŞÜ0-9]{3,}", norm(s)))
    return ws


def similarity(a, b):
    aw = text_words(a)
    bw = text_words(b)
    if not aw or not bw:
        return 0.0
    return len(aw & bw) / max(1, min(len(aw), len(bw)))


def card_similarity(c1, c2):
    t1 = " ".join([c1.get("baslik",""), c1.get("hukuki_soru",""), c1.get("emsal_ilke","")])
    t2 = " ".join([c2.get("baslik",""), c2.get("hukuki_soru",""), c2.get("emsal_ilke","")])
    return round(similarity(t1, t2), 3)


def analyze_decision(karar_no, cards):
    card_infos = []
    issue_counter = Counter()

    for c in cards:
        pi = primary_issue(c)
        issue_counter[pi["code"]] += 1
        card_infos.append({
            "card_index": c.get("_card_index"),
            "baslik": c.get("baslik", ""),
            "hukuki_soru": c.get("hukuki_soru", ""),
            "primary_issue": pi,
            "all_issues": detect_issue_codes(card_text(c)),
        })

    unique_issue_codes = list(issue_counter.keys())
    unique_count = len(unique_issue_codes)

    # Aynı meseleye çok kart üretilmiş mi?
    repeated = []
    for code, count in issue_counter.items():
        if code != "DIGER" and count > 1:
            repeated.append({"code": code, "count": count})

    # Kartlar arası benzerlik
    similarities = []
    for i in range(len(cards)):
        for j in range(i + 1, len(cards)):
            sim = card_similarity(cards[i], cards[j])
            if sim >= 0.55:
                similarities.append({
                    "card_a": cards[i].get("_card_index"),
                    "card_b": cards[j].get("_card_index"),
                    "similarity": sim,
                    "baslik_a": cards[i].get("baslik", ""),
                    "baslik_b": cards[j].get("baslik", ""),
                })

    # Kapsam puanı: farklı mesele sayısı ve tekrar riski
    card_count = len(cards)
    diversity_score = min(100, unique_count * 22)
    repeat_penalty = min(30, sum(x["count"] - 1 for x in repeated) * 10)
    similarity_penalty = min(25, len(similarities) * 8)
    coverage_score = max(0, min(100, diversity_score - repeat_penalty - similarity_penalty + min(20, card_count * 3)))

    if coverage_score >= 85:
        status = "YETERLI"
    elif coverage_score >= 65:
        status = "KONTROL"
    else:
        status = "ZAYIF"

    return {
        "karar_no": karar_no,
        "card_count": card_count,
        "unique_issue_count": unique_count,
        "unique_issue_codes": unique_issue_codes,
        "issue_distribution": dict(issue_counter),
        "repeated_issues": repeated,
        "high_similarity_pairs": similarities,
        "coverage_score": coverage_score,
        "coverage_status": status,
        "cards": card_infos,
    }


def main():
    print("=" * 80)
    print("175 - HUKUKI MESELE KAPSAM ANALIZ MOTORU")
    print("=" * 80)

    run_tag = tag()

    if len(sys.argv) >= 2:
        input_path = sys.argv[1]
    else:
        input_path = latest_file(INPUT_PATTERN)

    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError("168 production output JSONL bulunamadı.")

    rows = read_jsonl(input_path)
    by_decision = flatten_cards(rows)

    detail_path = os.path.join(LOG_DIR, f"175_hukuki_mesele_kapsam_detay_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"175_hukuki_mesele_kapsam_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"175_hukuki_mesele_kapsam_analiz_raporu_{run_tag}.txt")

    analyses = []
    for karar_no, cards in by_decision.items():
        analysis = analyze_decision(karar_no, cards)
        analyses.append(analysis)
        append_jsonl(detail_path, analysis)

    total_decisions = len(analyses)
    total_cards = sum(a["card_count"] for a in analyses)
    avg_coverage = round(sum(a["coverage_score"] for a in analyses) / total_decisions, 2) if total_decisions else 0
    weak_count = sum(1 for a in analyses if a["coverage_status"] == "ZAYIF")
    control_count = sum(1 for a in analyses if a["coverage_status"] == "KONTROL")
    enough_count = sum(1 for a in analyses if a["coverage_status"] == "YETERLI")

    # Büyük üretim eşiği:
    # - Ortalama kapsam >= 70
    # - Zayıf karar oranı <= %20
    weak_rate = round((weak_count / total_decisions) * 100, 2) if total_decisions else 0
    ready_for_176 = total_decisions > 0 and avg_coverage >= 70 and weak_rate <= 20

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_path": input_path,
        "decision_count": total_decisions,
        "total_cards": total_cards,
        "avg_coverage_score": avg_coverage,
        "coverage_status_counts": {
            "YETERLI": enough_count,
            "KONTROL": control_count,
            "ZAYIF": weak_count,
        },
        "weak_rate": weak_rate,
        "ready_for_176": ready_for_176,
        "detail_path": detail_path,
        "rapor_path": rapor_path,
        "next_step": "176_Hukuki_Mesele_Onceliklendirme_Motoru.py",
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("175 - HUKUKI MESELE KAPSAM ANALIZ MOTORU RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                  : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input                  : {input_path}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Karar sayısı            : {total_decisions}\n")
        f.write(f"Kart sayısı             : {total_cards}\n")
        f.write(f"Ortalama kapsam puanı   : {avg_coverage} / 100\n")
        f.write(f"Yeterli karar           : {enough_count}\n")
        f.write(f"Kontrol gereken karar    : {control_count}\n")
        f.write(f"Zayıf karar             : {weak_count}\n")
        f.write(f"Zayıf oran              : %{weak_rate}\n")
        f.write(f"176'ya geçilebilir mi   : {'EVET' if ready_for_176 else 'HAYIR'}\n\n")

        f.write("KARAR BAZLI KAPSAM\n")
        f.write("-" * 80 + "\n")
        for a in analyses:
            f.write(f"\nKarar: {a['karar_no']} | Kart: {a['card_count']} | Farklı mesele: {a['unique_issue_count']} | Puan: {a['coverage_score']} | Durum: {a['coverage_status']}\n")
            f.write(f"Mesele dağılımı: {a['issue_distribution']}\n")
            if a["repeated_issues"]:
                f.write(f"Tekrar riski: {a['repeated_issues']}\n")
            if a["high_similarity_pairs"]:
                f.write(f"Benzer kart riski: {a['high_similarity_pairs']}\n")
            for c in a["cards"]:
                f.write(f"  - Kart {c['card_index']}: {c['primary_issue']['label']} | {c['baslik']}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Detay JSONL             : {detail_path}\n")
        f.write(f"State JSON              : {state_path}\n")
        f.write(f"Rapor                   : {rapor_path}\n")

    print("\n175 KAPSAM ANALIZI TAMAMLANDI")
    print("-" * 80)
    print(f"Karar sayısı            : {total_decisions}")
    print(f"Kart sayısı             : {total_cards}")
    print(f"Ortalama kapsam puanı   : {avg_coverage} / 100")
    print(f"Yeterli karar           : {enough_count}")
    print(f"Kontrol gereken karar    : {control_count}")
    print(f"Zayıf karar             : {weak_count}")
    print(f"176'ya geçilebilir mi   : {'EVET' if ready_for_176 else 'HAYIR'}")
    print("\nDosyalar:")
    print(detail_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
