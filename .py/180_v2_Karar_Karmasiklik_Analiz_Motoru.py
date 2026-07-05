# -*- coding: utf-8 -*-
"""
180 v2 - KARAR KARMAŞIKLIK ANALIZ MOTORU

v2 farkı:
- 180 v1 çıktısında görülen çelişki giderildi:
  Optimal aralık 3-5 ve mevcut 3 ise "eksik" sayılmaz.
  Optimal aralık 6-8 ve mevcut 6 ise "eksik" sayılmaz.
- AI'nın card_count_status alanı yerine, optimal_card_min / optimal_card_max / actual_card_count sayısal kontrolü esas alınır.
- Planlama puanı düşük olsa bile kart sayısı optimal aralıktaysa FAIL üretmez; REVIEW/WARNING olarak bırakır.
- 181'e geçişte esas koşullar:
  * hata yok
  * FAIL yok
  * sayısal olarak eksik kartlı karar yok
  * ortalama planlama puanı >= 70
"""

import os
import re
import sys
import glob
import json
import time
import traceback
from datetime import datetime

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

try:
    from pypdf import PdfReader
except Exception:
    try:
        from PyPDF2 import PdfReader
    except Exception:
        PdfReader = None


BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

INPUT_PATTERN_179 = os.path.join(URETIM_OUTPUT_DIR, "179_optimized_production_output_*.jsonl")
INPUT_PATTERN_168 = os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl")

MODEL = os.getenv("OPENAI_COMPLEXITY_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
MAX_TEXT_CHARS = 38000
SLEEP_SECONDS = 0.5

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
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


def load_api_key():
    if load_dotenv:
        for envp in [os.path.join(BASE_DIR, ".env"), os.path.join(PY_DIR, ".env")]:
            if os.path.exists(envp):
                load_dotenv(envp)
    return os.getenv("OPENAI_API_KEY", "").strip()


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


def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def clean_text(text):
    text = text or ""
    text = text.replace("\x00", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def truncate_text(text, max_chars=MAX_TEXT_CHARS):
    text = text or ""
    if len(text) <= max_chars:
        return text
    head = text[:int(max_chars * 0.70)]
    tail = text[-int(max_chars * 0.30):]
    return head + "\n\n...[METIN ORTADAN KISALTILDI]...\n\n" + tail


def extract_text_from_pdf(path):
    if PdfReader is None:
        raise RuntimeError("pypdf/PyPDF2 yüklü değil. Komut: pip install pypdf")
    reader = PdfReader(path)
    parts = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""
        if txt.strip():
            parts.append(f"\n\n--- SAYFA {i} ---\n{txt}")
    return "\n".join(parts).strip()


def extract_text_from_txt(path):
    for enc in ["utf-8", "utf-8-sig", "cp1254", "latin-1"]:
        try:
            with open(path, "r", encoding=enc, errors="ignore") as f:
                return f.read()
        except Exception:
            continue
    return ""


def extract_text(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    if ext == ".txt":
        return extract_text_from_txt(path)
    raise RuntimeError(f"Desteklenmeyen dosya uzantısı: {ext}")


def parse_json_response(raw):
    raw = (raw or "").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?", "", raw, flags=re.I).strip()
        raw = re.sub(r"```$", "", raw).strip()
    try:
        return json.loads(raw)
    except Exception:
        pass
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if m:
        return json.loads(m.group(0))
    raise ValueError("AI yanıtı JSON parse edilemedi.")


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


def rows_by_decision(rows):
    items = []
    for row in rows:
        if "_json_error" in row or row.get("status") != "OK":
            continue

        karar_no = str(row.get("karar_no") or row.get("orijinal_karar_no") or "").strip()
        if not karar_no:
            continue

        kartlar = row.get("kartlar", [])
        if not isinstance(kartlar, list):
            kartlar = []

        cards = []
        for i, k in enumerate(kartlar, start=1):
            if not isinstance(k, dict):
                continue
            cards.append({
                "card_index": i,
                "baslik": str(k.get("baslik", "")).strip(),
                "hukuki_soru": str(k.get("hukuki_soru", "")).strip(),
                "konu_ozeti": str(k.get("konu_ozeti", "")).strip(),
                "sonuc_ozeti": str(k.get("sonuc_ozeti", "")).strip(),
                "sonuc_tipi": str(k.get("sonuc_tipi", "")).strip(),
                "emsal_ilke": str(k.get("emsal_ilke", "")).strip(),
                "anahtar": normalize_list(k.get("anahtar")),
                "mevzuat": normalize_list(k.get("mevzuat")),
            })

        items.append({
            "karar_no": karar_no,
            "dosya_adi": str(row.get("dosya_adi") or "").strip(),
            "dosya_yolu": str(row.get("dosya_yolu") or "").strip(),
            "kartlar": cards,
        })
    return items


def get_limit():
    if len(sys.argv) >= 3:
        try:
            return int(sys.argv[2])
        except Exception:
            return None
    return None


def build_prompt(karar_no, karar_metni, cards):
    system = """
Sen Kamu İhale Kurulu kararları için karar karmaşıklığı ve optimal kart sayısı hakemisin.

Görevin:
- Karar metnindeki bilgi yoğunluğunu ve hukuki karmaşıklığı analiz etmek.
- Kararda kaç ayrı iddia/hukuki mesele/mevzuat ekseni/Kurul sonucu bulunduğunu belirlemek.
- Bu karar için WEB ve AI/RAG hedefleri açısından optimal kart sayısı aralığını söylemek.
- Mevcut üretilen kart sayısının eksik, yeterli veya fazla olup olmadığını değerlendirmek.
- Eksik kart türlerini veya fazla kart riskini belirtmek.

Yalnızca geçerli JSON üret.
Markdown, açıklama veya kod bloğu yazma.

Önemli:
- Mevcut kart sayısı optimal_card_min ile optimal_card_max arasındaysa card_count_status ENOUGH olmalıdır.
- Mevcut kart sayısı optimal_card_min'e eşitse eksik sayma.
- Mevcut kart sayısı optimal_card_max'a eşitse fazla sayma.
- WARNING verebilirsin ama sayı aralık içindeyse TOO_FEW/TOO_MANY deme.

JSON şeması:
{
  "karar_no": "",
  "complexity_level": "LOW|MEDIUM|HIGH|VERY_HIGH",
  "complexity_score": 0,
  "claim_count": 0,
  "legal_issue_count": 0,
  "legislation_axis_count": 0,
  "separate_result_count": 0,
  "high_value_issue_count": 0,
  "optimal_card_min": 0,
  "optimal_card_max": 0,
  "recommended_card_count": 0,
  "actual_card_count": 0,
  "card_count_status": "ENOUGH|TOO_FEW|TOO_MANY|REVIEW",
  "missing_card_topics": [
    {"topic": "", "reason": "", "importance": 0}
  ],
  "excess_card_risks": [
    {"topic": "", "reason": ""}
  ],
  "web_planning_score": 0,
  "rag_planning_score": 0,
  "overall_planning_score": 0,
  "decision": "PASS|WARNING|FAIL",
  "notes": ["..."]
}
""".strip()

    user = f"""
KARAR NO:
{karar_no}

ASIL KARAR METNI:
{karar_metni}

MEVCUT URETILEN/OPTIMIZE EDILEN KARTLAR:
{json.dumps(cards, ensure_ascii=False, indent=2)}
""".strip()

    return system, user


def normalize_review(obj, karar_no, actual_count):
    if not isinstance(obj, dict):
        obj = {}

    def as_int(key, default=0):
        try:
            return int(float(obj.get(key, default)))
        except Exception:
            return default

    def as_score(key, default=0):
        return max(0, min(100, as_int(key, default)))

    level = str(obj.get("complexity_level", "")).strip().upper()
    if level not in {"LOW", "MEDIUM", "HIGH", "VERY_HIGH"}:
        score = as_score("complexity_score", 0)
        if score >= 85:
            level = "VERY_HIGH"
        elif score >= 65:
            level = "HIGH"
        elif score >= 35:
            level = "MEDIUM"
        else:
            level = "LOW"

    mn = as_int("optimal_card_min", actual_count)
    mx = as_int("optimal_card_max", actual_count)
    actual = as_int("actual_card_count", actual_count)

    if mn <= 0:
        mn = actual
    if mx < mn:
        mx = mn

    # v2: sayısal aralık gerçeği esastır
    if actual < mn:
        numeric_status = "TOO_FEW"
    elif actual > mx:
        numeric_status = "TOO_MANY"
    else:
        numeric_status = "ENOUGH"

    ai_status = str(obj.get("card_count_status", "")).strip().upper()
    if ai_status not in {"ENOUGH", "TOO_FEW", "TOO_MANY", "REVIEW"}:
        ai_status = numeric_status

    # Eğer AI status ile sayı çelişirse sayı kazanır.
    status = numeric_status

    missing = obj.get("missing_card_topics", [])
    if not isinstance(missing, list):
        missing = []

    excess = obj.get("excess_card_risks", [])
    if not isinstance(excess, list):
        excess = []

    overall = as_score("overall_planning_score", 0)

    decision = str(obj.get("decision", "")).strip().upper()
    if decision not in {"PASS", "WARNING", "FAIL"}:
        if status == "ENOUGH" and overall >= 80:
            decision = "PASS"
        elif status == "TOO_FEW" or overall < 70:
            decision = "WARNING"
        else:
            decision = "WARNING"

    # v2: aralık içindeyse ve AI FAIL vermiş ama kritik eksik yoksa WARNING'a indir.
    if status == "ENOUGH" and decision == "FAIL":
        high_missing = []
        for m in missing:
            if isinstance(m, dict):
                try:
                    if int(float(m.get("importance", 0))) >= 90:
                        high_missing.append(m)
                except Exception:
                    pass
        if not high_missing:
            decision = "WARNING"

    notes = obj.get("notes", [])
    if not isinstance(notes, list):
        notes = [str(notes)]

    return {
        "karar_no": str(obj.get("karar_no") or karar_no).strip(),
        "complexity_level": level,
        "complexity_score": as_score("complexity_score", 0),
        "claim_count": as_int("claim_count", 0),
        "legal_issue_count": as_int("legal_issue_count", 0),
        "legislation_axis_count": as_int("legislation_axis_count", 0),
        "separate_result_count": as_int("separate_result_count", 0),
        "high_value_issue_count": as_int("high_value_issue_count", 0),
        "optimal_card_min": mn,
        "optimal_card_max": mx,
        "recommended_card_count": as_int("recommended_card_count", actual),
        "actual_card_count": actual,
        "ai_card_count_status": ai_status,
        "card_count_status": status,
        "missing_card_topics": missing,
        "excess_card_risks": excess,
        "web_planning_score": as_score("web_planning_score", 0),
        "rag_planning_score": as_score("rag_planning_score", 0),
        "overall_planning_score": overall,
        "decision": decision,
        "notes": [str(x).strip() for x in notes if str(x).strip()],
    }


def call_ai(client, karar_no, karar_metni, cards):
    system, user = build_prompt(karar_no, karar_metni, cards)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0,
    )
    raw = resp.choices[0].message.content
    parsed = parse_json_response(raw)
    review = normalize_review(parsed, karar_no, len(cards))

    usage = {}
    try:
        usage = {
            "prompt_tokens": getattr(resp.usage, "prompt_tokens", None),
            "completion_tokens": getattr(resp.usage, "completion_tokens", None),
            "total_tokens": getattr(resp.usage, "total_tokens", None),
        }
    except Exception:
        usage = {}
    return raw, review, usage


def main():
    print("=" * 80)
    print("180 v2 - KARAR KARMAŞIKLIK ANALIZ MOTORU")
    print("=" * 80)

    run_tag = tag()

    if len(sys.argv) >= 2:
        input_path = sys.argv[1]
    else:
        input_path = latest_file(INPUT_PATTERN_179) or latest_file(INPUT_PATTERN_168)

    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError("179 optimize veya 168 production output JSONL bulunamadı.")

    api_key = load_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY bulunamadı.")

    if OpenAI is None:
        raise RuntimeError("openai paketi yüklü değil. Komut: pip install openai")

    client = OpenAI(api_key=api_key)

    rows = read_jsonl(input_path)
    items = rows_by_decision(rows)

    limit = get_limit()
    if limit:
        items = items[:limit]

    detail_path = os.path.join(LOG_DIR, f"180_v2_karmasiklik_detay_{run_tag}.jsonl")
    raw_dir = os.path.join(LOG_DIR, f"180_v2_karmasiklik_raw_{run_tag}")
    os.makedirs(raw_dir, exist_ok=True)

    state_path = os.path.join(STATE_DIR, f"180_v2_karmasiklik_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"180_v2_karar_karmasiklik_analiz_raporu_{run_tag}.txt")

    print(f"\nInput       : {input_path}")
    print(f"Model       : {MODEL}")
    print(f"Karar sayısı : {len(items)}")
    print("-" * 80)

    pass_count = 0
    warning_count = 0
    fail_count = 0
    error_count = 0
    total_score = 0
    total_tokens = 0
    total_actual_cards = 0
    total_recommended_cards = 0
    too_few_count = 0
    too_many_count = 0
    review_count = 0

    all_results = []

    for idx, item in enumerate(items, start=1):
        karar_no = item["karar_no"]
        dosya_yolu = item["dosya_yolu"]
        cards = item["kartlar"]

        print(f"[{idx}/{len(items)}] Karmaşıklık analizi: {karar_no} | Kart: {len(cards)}")

        try:
            if not dosya_yolu or not os.path.exists(dosya_yolu):
                raise RuntimeError(f"Dosya bulunamadı: {dosya_yolu}")

            metin = clean_text(extract_text(dosya_yolu))
            if len(metin) < 300:
                raise RuntimeError(f"Karar metni çok kısa veya okunamadı: {len(metin)}")

            metin = truncate_text(metin)
            raw, review, usage = call_ai(client, karar_no, metin, cards)

            raw_path = os.path.join(raw_dir, f"{idx:04d}_{re.sub(r'[^0-9A-Za-z_.-]+', '_', karar_no)}.txt")
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(raw or "")

            decision = review["decision"]
            if decision == "PASS":
                pass_count += 1
            elif decision == "WARNING":
                warning_count += 1
            else:
                fail_count += 1

            if review["card_count_status"] == "TOO_FEW":
                too_few_count += 1
            elif review["card_count_status"] == "TOO_MANY":
                too_many_count += 1
            elif review["card_count_status"] == "REVIEW":
                review_count += 1

            total_score += review["overall_planning_score"]
            total_actual_cards += review["actual_card_count"]
            total_recommended_cards += review["recommended_card_count"]

            try:
                if usage.get("total_tokens"):
                    total_tokens += int(usage["total_tokens"])
            except Exception:
                pass

            row = {
                "run_id": run_tag,
                "time": now(),
                "status": "OK",
                "input_path": input_path,
                "karar_no": karar_no,
                "dosya_yolu": dosya_yolu,
                "kart_sayisi": len(cards),
                "review": review,
                "usage": usage,
                "raw_response_path": raw_path,
            }
            append_jsonl(detail_path, row)
            all_results.append(row)

            print(f"{decision} | Plan: {review['overall_planning_score']} | Karmaşıklık: {review['complexity_level']} | Optimal: {review['optimal_card_min']}-{review['optimal_card_max']} | Actual: {review['actual_card_count']} | Status: {review['card_count_status']} | Token: {usage.get('total_tokens')}")

        except Exception as e:
            error_count += 1
            row = {
                "run_id": run_tag,
                "time": now(),
                "status": "ERROR",
                "input_path": input_path,
                "karar_no": karar_no,
                "dosya_yolu": dosya_yolu,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
            append_jsonl(detail_path, row)
            all_results.append(row)
            print(f"HATA | {str(e)}")

        time.sleep(SLEEP_SECONDS)

    decision_count = len(items)
    avg_score = round(total_score / decision_count, 2) if decision_count else 0
    avg_actual = round(total_actual_cards / decision_count, 2) if decision_count else 0
    avg_recommended = round(total_recommended_cards / decision_count, 2) if decision_count else 0

    ready_for_181 = (
        decision_count > 0
        and error_count == 0
        and fail_count == 0
        and avg_score >= 70
        and too_few_count == 0
    )

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_path": input_path,
        "model": MODEL,
        "decision_count": decision_count,
        "pass_count": pass_count,
        "warning_count": warning_count,
        "fail_count": fail_count,
        "error_count": error_count,
        "avg_planning_score": avg_score,
        "avg_actual_cards": avg_actual,
        "avg_recommended_cards": avg_recommended,
        "too_few_count": too_few_count,
        "too_many_count": too_many_count,
        "review_count": review_count,
        "total_tokens": total_tokens,
        "detail_path": detail_path,
        "raw_dir": raw_dir,
        "ready_for_181": ready_for_181,
        "next_step": "181_Final_Master_Production_Controller.py",
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("180 v2 - KARAR KARMAŞIKLIK ANALIZ MOTORU RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input                         : {input_path}\n")
        f.write(f"Model                         : {MODEL}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Karar sayısı                   : {decision_count}\n")
        f.write(f"PASS                           : {pass_count}\n")
        f.write(f"WARNING                        : {warning_count}\n")
        f.write(f"FAIL                           : {fail_count}\n")
        f.write(f"Hata                           : {error_count}\n")
        f.write(f"Ortalama planlama puanı        : {avg_score} / 100\n")
        f.write(f"Ortalama mevcut kart           : {avg_actual}\n")
        f.write(f"Ortalama önerilen kart         : {avg_recommended}\n")
        f.write(f"Eksik kartlı karar             : {too_few_count}\n")
        f.write(f"Fazla kartlı karar             : {too_many_count}\n")
        f.write(f"Review gereken                 : {review_count}\n")
        f.write(f"Toplam token                   : {total_tokens}\n")
        f.write(f"181'e geçilebilir mi           : {'EVET' if ready_for_181 else 'HAYIR'}\n\n")

        f.write("KARAR BAZLI KARMAŞIKLIK\n")
        f.write("-" * 80 + "\n")
        for r in all_results:
            if r["status"] != "OK":
                f.write(f"\nKarar: {r.get('karar_no')} | ERROR | {r.get('error')}\n")
                continue

            rev = r["review"]
            f.write(f"\nKarar: {r['karar_no']} | {rev['decision']} | Plan: {rev['overall_planning_score']} | Karmaşıklık: {rev['complexity_level']} ({rev['complexity_score']})\n")
            f.write(f"İddia: {rev['claim_count']} | Mesele: {rev['legal_issue_count']} | Mevzuat ekseni: {rev['legislation_axis_count']} | Ayrı sonuç: {rev['separate_result_count']} | Yüksek değerli mesele: {rev['high_value_issue_count']}\n")
            f.write(f"Optimal kart: {rev['optimal_card_min']}-{rev['optimal_card_max']} | Önerilen: {rev['recommended_card_count']} | Mevcut: {rev['actual_card_count']} | Durum: {rev['card_count_status']} | AI Durum: {rev['ai_card_count_status']}\n")

            if rev.get("missing_card_topics"):
                f.write("Eksik kart konuları:\n")
                for m in rev["missing_card_topics"]:
                    f.write(f"  - {m.get('importance')} | {m.get('topic')} | {m.get('reason')}\n")

            if rev.get("excess_card_risks"):
                f.write("Fazla kart riskleri:\n")
                for ex in rev["excess_card_risks"]:
                    f.write(f"  - {ex.get('topic')} | {ex.get('reason')}\n")

            if rev.get("notes"):
                f.write("Notlar:\n")
                for n in rev["notes"]:
                    f.write(f"  - {n}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Detay JSONL                    : {detail_path}\n")
        f.write(f"Raw klasör                     : {raw_dir}\n")
        f.write(f"State JSON                     : {state_path}\n")
        f.write(f"Rapor                          : {rapor_path}\n")

    print("\n180 v2 KARMAŞIKLIK ANALIZI TAMAMLANDI")
    print("-" * 80)
    print(f"Karar sayısı                   : {decision_count}")
    print(f"PASS                           : {pass_count}")
    print(f"WARNING                        : {warning_count}")
    print(f"FAIL                           : {fail_count}")
    print(f"Hata                           : {error_count}")
    print(f"Ortalama planlama puanı        : {avg_score} / 100")
    print(f"Ortalama mevcut kart           : {avg_actual}")
    print(f"Ortalama önerilen kart         : {avg_recommended}")
    print(f"Eksik kartlı karar             : {too_few_count}")
    print(f"Fazla kartlı karar             : {too_many_count}")
    print(f"Toplam token                   : {total_tokens}")
    print(f"181'e geçilebilir mi           : {'EVET' if ready_for_181 else 'HAYIR'}")

    print("\nDosyalar:")
    print(detail_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
