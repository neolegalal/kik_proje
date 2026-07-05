# -*- coding: utf-8 -*-
"""
177 - HUKUKI DOGRULUK HAKEMI

Amaç:
- 168 production output JSONL dosyasındaki kartları karar metniyle karşılaştırır.
- Her kart için hukuki doğruluk denetimi yapar:
  * Sonuç özeti karar metniyle uyumlu mu?
  * Sonuç tipi doğru mu?
  * Emsal ilke karardan makul biçimde çıkarılabilir mi?
  * Hukuki soru karardaki gerçek meseleye dayanıyor mu?
  * Mevzuat kararla ilişkili mi?
  * Hallüsinasyon / aşırı genelleme riski var mı?
- Karar bazında ve kart bazında PASS/WARNING/FAIL üretir.

Kullanım:
  python ".py\\177_Hukuki_Dogruluk_Hakemi.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\uretim_output\\168_production_output_20260630_182904.jsonl"

Limitli:
  python ".py\\177_Hukuki_Dogruluk_Hakemi.py" "C:\\...\\168_production_output_x.jsonl" 2

Not:
- API maliyeti oluşur.
- DB'ye yazmaz.
- Büyük üretim öncesi hukuki doğruluk güvenlik katmanıdır.
"""

import os
import re
import sys
import glob
import json
import time
import traceback
from datetime import datetime
from collections import defaultdict

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


# =============================================================================
# AYARLAR
# =============================================================================

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

INPUT_PATTERN = os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl")

MODEL = os.getenv("OPENAI_LEGAL_JUDGE_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
MAX_TEXT_CHARS = 38000
SLEEP_SECONDS = 0.5

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


# =============================================================================
# YARDIMCI FONKSIYONLAR
# =============================================================================

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
        env1 = os.path.join(BASE_DIR, ".env")
        env2 = os.path.join(PY_DIR, ".env")
        if os.path.exists(env1):
            load_dotenv(env1)
        if os.path.exists(env2):
            load_dotenv(env2)
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


def flatten_rows_by_decision(rows):
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
        for idx, k in enumerate(kartlar, start=1):
            if not isinstance(k, dict):
                continue
            cards.append({
                "card_index": idx,
                "baslik": str(k.get("baslik", "")).strip(),
                "hukuki_soru": str(k.get("hukuki_soru", "")).strip(),
                "konu_ozeti": str(k.get("konu_ozeti", "")).strip(),
                "sonuc_ozeti": str(k.get("sonuc_ozeti", "")).strip(),
                "sonuc": str(k.get("sonuc", "")).strip(),
                "sonuc_tipi": str(k.get("sonuc_tipi", "")).strip(),
                "emsal_ilke": str(k.get("emsal_ilke", "")).strip(),
                "anahtar": normalize_list(k.get("anahtar")),
                "mevzuat": normalize_list(k.get("mevzuat")),
                "guven": str(k.get("guven", "")).strip(),
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


# =============================================================================
# PROMPT
# =============================================================================

def build_prompt(karar_no, karar_metni, cards):
    system = """
Sen Kamu İhale Hukuku alanında çalışan sert bir hukuki doğruluk hakemisin.
Görevin üretilmiş karar kartlarını asıl Kamu İhale Kurulu karar metniyle karşılaştırmaktır.

Yalnızca geçerli JSON üret.
Markdown, açıklama veya kod bloğu yazma.

Her kart için şu soruları cevapla:
1. Sonuç özeti karar metniyle uyumlu mu?
2. Sonuç tipi doğru mu?
3. Hukuki soru karardaki gerçek hukuki meseleye dayanıyor mu?
4. Emsal ilke karardan makul ve güvenli biçimde çıkarılabilir mi?
5. Emsal ilke kararı aşırı genelleştiriyor mu?
6. Mevzuat listesi karar metniyle ilişkili mi?
7. Kartta hallüsinasyon, yanlış sonuç veya çarpıtma var mı?

Özel dikkat:
- Kurul somut olayda ret kararı vermişse, kart kabul/iptal gibi göstermemeli.
- Kararda sadece somut olay nedeniyle aykırılık yok denmişse, bunu genel ve sınırsız hukuk kuralına çevirmemeli.
- "İdarenin takdirindedir" gibi ifadeler karar metninde dayanağı yoksa aşırı genelleme sayılabilir.
- Emsal ilke, Kurul kararındaki gerekçeden daha geniş bir kural üretmemeli.
- Mevzuat kararda gerçekten geçmeli veya kararın hukuki dayanağıyla doğrudan ilgili olmalı.

JSON şeması:
{
  "karar_no": "",
  "overall_score": 0,
  "decision": "PASS|WARNING|FAIL",
  "summary": "",
  "card_reviews": [
    {
      "card_index": 1,
      "card_title": "",
      "legal_accuracy_score": 0,
      "result_accuracy_score": 0,
      "question_accuracy_score": 0,
      "principle_accuracy_score": 0,
      "legislation_accuracy_score": 0,
      "overgeneralization_risk": "LOW|MEDIUM|HIGH",
      "hallucination_risk": "LOW|MEDIUM|HIGH",
      "decision": "PASS|WARNING|FAIL",
      "issues": ["..."],
      "correction_suggestion": {
        "hukuki_soru": "",
        "sonuc_ozeti": "",
        "emsal_ilke": ""
      },
      "reason": "Kısa gerekçe"
    }
  ],
  "critical_errors": ["..."],
  "improvement_notes": ["..."]
}

Puanlama:
- 90-100: Hukuken güvenli ve kararla uyumlu
- 75-89: Kullanılabilir ama revizyon önerilir
- 60-74: Riskli
- 0-59: Hukuken hatalı veya yanıltıcı

Karar:
- Tüm kartlar güvenli ve ortalama >= 88 ise PASS.
- Birkaç orta risk varsa WARNING.
- Herhangi bir kartta ciddi sonuç hatası, açık hallüsinasyon veya yüksek hukuki yanıltma varsa FAIL.
""".strip()

    user = f"""
KARAR NO:
{karar_no}

ASIL KARAR METNI:
{karar_metni}

URETILEN KARTLAR:
{json.dumps(cards, ensure_ascii=False, indent=2)}
""".strip()

    return system, user


def normalize_review(obj, karar_no, cards):
    if not isinstance(obj, dict):
        obj = {}

    def score_from_dict(d, key, default=0):
        try:
            return max(0, min(100, int(float(d.get(key, default)))))
        except Exception:
            return default

    card_reviews = obj.get("card_reviews", [])
    if not isinstance(card_reviews, list):
        card_reviews = []

    normalized_cards = []
    for cr in card_reviews:
        if not isinstance(cr, dict):
            continue

        decision = str(cr.get("decision", "")).strip().upper()
        if decision not in {"PASS", "WARNING", "FAIL"}:
            s = score_from_dict(cr, "legal_accuracy_score", 0)
            decision = "PASS" if s >= 88 else "WARNING" if s >= 75 else "FAIL"

        issues = cr.get("issues", [])
        if not isinstance(issues, list):
            issues = [str(issues)]

        corr = cr.get("correction_suggestion", {})
        if not isinstance(corr, dict):
            corr = {}

        normalized_cards.append({
            "card_index": cr.get("card_index"),
            "card_title": str(cr.get("card_title", "")).strip(),
            "legal_accuracy_score": score_from_dict(cr, "legal_accuracy_score"),
            "result_accuracy_score": score_from_dict(cr, "result_accuracy_score"),
            "question_accuracy_score": score_from_dict(cr, "question_accuracy_score"),
            "principle_accuracy_score": score_from_dict(cr, "principle_accuracy_score"),
            "legislation_accuracy_score": score_from_dict(cr, "legislation_accuracy_score"),
            "overgeneralization_risk": str(cr.get("overgeneralization_risk", "LOW")).strip().upper(),
            "hallucination_risk": str(cr.get("hallucination_risk", "LOW")).strip().upper(),
            "decision": decision,
            "issues": [str(x).strip() for x in issues if str(x).strip()],
            "correction_suggestion": {
                "hukuki_soru": str(corr.get("hukuki_soru", "")).strip(),
                "sonuc_ozeti": str(corr.get("sonuc_ozeti", "")).strip(),
                "emsal_ilke": str(corr.get("emsal_ilke", "")).strip(),
            },
            "reason": str(cr.get("reason", "")).strip(),
        })

    # Eğer model eksik review döndürürse kart sayısına göre doldur.
    reviewed_indexes = {str(x.get("card_index")) for x in normalized_cards}
    for card in cards:
        if str(card.get("card_index")) not in reviewed_indexes:
            normalized_cards.append({
                "card_index": card.get("card_index"),
                "card_title": card.get("baslik", ""),
                "legal_accuracy_score": 0,
                "result_accuracy_score": 0,
                "question_accuracy_score": 0,
                "principle_accuracy_score": 0,
                "legislation_accuracy_score": 0,
                "overgeneralization_risk": "UNKNOWN",
                "hallucination_risk": "UNKNOWN",
                "decision": "FAIL",
                "issues": ["AI hakem bu kart için değerlendirme döndürmedi."],
                "correction_suggestion": {"hukuki_soru": "", "sonuc_ozeti": "", "emsal_ilke": ""},
                "reason": "Eksik hakem çıktısı.",
            })

    try:
        overall = max(0, min(100, int(float(obj.get("overall_score", 0)))))
    except Exception:
        if normalized_cards:
            overall = int(sum(c["legal_accuracy_score"] for c in normalized_cards) / len(normalized_cards))
        else:
            overall = 0

    decision = str(obj.get("decision", "")).strip().upper()
    if decision not in {"PASS", "WARNING", "FAIL"}:
        fail_cards = sum(1 for c in normalized_cards if c["decision"] == "FAIL")
        warn_cards = sum(1 for c in normalized_cards if c["decision"] == "WARNING")
        high_risk = any(c["hallucination_risk"] == "HIGH" or c["overgeneralization_risk"] == "HIGH" for c in normalized_cards)
        if fail_cards or high_risk or overall < 75:
            decision = "FAIL"
        elif warn_cards or overall < 88:
            decision = "WARNING"
        else:
            decision = "PASS"

    crit = obj.get("critical_errors", [])
    if not isinstance(crit, list):
        crit = [str(crit)]

    notes = obj.get("improvement_notes", [])
    if not isinstance(notes, list):
        notes = [str(notes)]

    return {
        "karar_no": str(obj.get("karar_no") or karar_no).strip(),
        "overall_score": overall,
        "decision": decision,
        "summary": str(obj.get("summary", "")).strip(),
        "card_reviews": normalized_cards,
        "critical_errors": [str(x).strip() for x in crit if str(x).strip()],
        "improvement_notes": [str(x).strip() for x in notes if str(x).strip()],
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
    review = normalize_review(parsed, karar_no, cards)

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


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 80)
    print("177 - HUKUKI DOGRULUK HAKEMI")
    print("=" * 80)

    run_tag = tag()

    if len(sys.argv) >= 2:
        input_path = sys.argv[1]
    else:
        input_path = latest_file(INPUT_PATTERN)

    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError("168 production output JSONL bulunamadı.")

    api_key = load_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY bulunamadı.")

    if OpenAI is None:
        raise RuntimeError("openai paketi yüklü değil. Komut: pip install openai")

    client = OpenAI(api_key=api_key)

    rows = read_jsonl(input_path)
    items = flatten_rows_by_decision(rows)

    limit = get_limit()
    if limit:
        items = items[:limit]

    detail_path = os.path.join(LOG_DIR, f"177_hukuki_dogruluk_detay_{run_tag}.jsonl")
    raw_dir = os.path.join(LOG_DIR, f"177_hukuki_dogruluk_raw_{run_tag}")
    os.makedirs(raw_dir, exist_ok=True)

    state_path = os.path.join(STATE_DIR, f"177_hukuki_dogruluk_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"177_hukuki_dogruluk_hakemi_raporu_{run_tag}.txt")

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
    total_cards = 0
    fail_cards = 0
    warning_cards = 0
    high_hallucination_cards = 0
    high_overgeneralization_cards = 0

    all_results = []

    for idx, item in enumerate(items, start=1):
        karar_no = item["karar_no"]
        dosya_yolu = item["dosya_yolu"]
        cards = item["kartlar"]

        print(f"[{idx}/{len(items)}] Hukuki doğruluk: {karar_no} | Kart: {len(cards)}")

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

            total_score += review["overall_score"]

            for cr in review["card_reviews"]:
                total_cards += 1
                if cr["decision"] == "FAIL":
                    fail_cards += 1
                elif cr["decision"] == "WARNING":
                    warning_cards += 1
                if cr["hallucination_risk"] == "HIGH":
                    high_hallucination_cards += 1
                if cr["overgeneralization_risk"] == "HIGH":
                    high_overgeneralization_cards += 1

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

            print(f"{decision} | Skor: {review['overall_score']} | Token: {usage.get('total_tokens')}")

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
    fail_rate = round((fail_count / decision_count) * 100, 2) if decision_count else 0
    fail_card_rate = round((fail_cards / total_cards) * 100, 2) if total_cards else 0

    ready_for_178 = (
        decision_count > 0
        and error_count == 0
        and fail_count == 0
        and fail_cards == 0
        and high_hallucination_cards == 0
        and high_overgeneralization_cards == 0
        and avg_score >= 85
    )

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_path": input_path,
        "model": MODEL,
        "decision_count": decision_count,
        "total_cards": total_cards,
        "pass_count": pass_count,
        "warning_count": warning_count,
        "fail_count": fail_count,
        "error_count": error_count,
        "avg_legal_accuracy_score": avg_score,
        "fail_rate": fail_rate,
        "fail_cards": fail_cards,
        "warning_cards": warning_cards,
        "fail_card_rate": fail_card_rate,
        "high_hallucination_cards": high_hallucination_cards,
        "high_overgeneralization_cards": high_overgeneralization_cards,
        "total_tokens": total_tokens,
        "detail_path": detail_path,
        "raw_dir": raw_dir,
        "ready_for_178": ready_for_178,
        "next_step": "178_Final_Master_Production_Controller.py",
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("177 - HUKUKI DOGRULUK HAKEMI RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input                         : {input_path}\n")
        f.write(f"Model                         : {MODEL}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Karar sayısı                   : {decision_count}\n")
        f.write(f"Kart sayısı                    : {total_cards}\n")
        f.write(f"PASS karar                     : {pass_count}\n")
        f.write(f"WARNING karar                  : {warning_count}\n")
        f.write(f"FAIL karar                     : {fail_count}\n")
        f.write(f"Hata                           : {error_count}\n")
        f.write(f"Ortalama hukuki doğruluk       : {avg_score} / 100\n")
        f.write(f"FAIL kart                      : {fail_cards}\n")
        f.write(f"WARNING kart                   : {warning_cards}\n")
        f.write(f"Yüksek hallüsinasyon riski     : {high_hallucination_cards}\n")
        f.write(f"Yüksek aşırı genelleme riski   : {high_overgeneralization_cards}\n")
        f.write(f"Toplam token                   : {total_tokens}\n")
        f.write(f"178'e geçilebilir mi           : {'EVET' if ready_for_178 else 'HAYIR'}\n\n")

        f.write("KARAR BAZLI HUKUKI DOGRULUK\n")
        f.write("-" * 80 + "\n")
        for r in all_results:
            if r["status"] != "OK":
                f.write(f"\nKarar: {r.get('karar_no')} | ERROR | {r.get('error')}\n")
                continue

            rev = r["review"]
            f.write(f"\nKarar: {r['karar_no']} | {rev['decision']} | Skor: {rev['overall_score']}\n")
            f.write(f"Özet: {rev.get('summary','')}\n")

            if rev.get("critical_errors"):
                f.write("Kritik hatalar:\n")
                for ce in rev["critical_errors"]:
                    f.write(f"  - {ce}\n")

            for cr in rev["card_reviews"]:
                f.write(f"  Kart {cr['card_index']} | {cr['decision']} | Hukuki: {cr['legal_accuracy_score']} | Sonuç: {cr['result_accuracy_score']} | İlke: {cr['principle_accuracy_score']} | Hallüsinasyon: {cr['hallucination_risk']} | Genelleme: {cr['overgeneralization_risk']}\n")
                f.write(f"    Başlık: {cr['card_title']}\n")
                if cr["issues"]:
                    f.write(f"    Issues: {cr['issues']}\n")
                if cr.get("reason"):
                    f.write(f"    Gerekçe: {cr['reason']}\n")
                corr = cr.get("correction_suggestion", {})
                if any(corr.values()):
                    f.write("    Düzeltme önerisi:\n")
                    if corr.get("hukuki_soru"):
                        f.write(f"      Hukuki soru: {corr.get('hukuki_soru')}\n")
                    if corr.get("sonuc_ozeti"):
                        f.write(f"      Sonuç özeti: {corr.get('sonuc_ozeti')}\n")
                    if corr.get("emsal_ilke"):
                        f.write(f"      Emsal ilke: {corr.get('emsal_ilke')}\n")

            if rev.get("improvement_notes"):
                f.write("İyileştirme notları:\n")
                for note in rev["improvement_notes"]:
                    f.write(f"  - {note}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Detay JSONL                    : {detail_path}\n")
        f.write(f"Raw klasör                     : {raw_dir}\n")
        f.write(f"State JSON                     : {state_path}\n")
        f.write(f"Rapor                          : {rapor_path}\n")

    print("\n177 HUKUKI DOGRULUK HAKEMI TAMAMLANDI")
    print("-" * 80)
    print(f"Karar sayısı                   : {decision_count}")
    print(f"Kart sayısı                    : {total_cards}")
    print(f"PASS karar                     : {pass_count}")
    print(f"WARNING karar                  : {warning_count}")
    print(f"FAIL karar                     : {fail_count}")
    print(f"Hata                           : {error_count}")
    print(f"Ortalama hukuki doğruluk       : {avg_score} / 100")
    print(f"FAIL kart                      : {fail_cards}")
    print(f"WARNING kart                   : {warning_cards}")
    print(f"Yüksek hallüsinasyon riski     : {high_hallucination_cards}")
    print(f"Yüksek aşırı genelleme riski   : {high_overgeneralization_cards}")
    print(f"Toplam token                   : {total_tokens}")
    print(f"178'e geçilebilir mi           : {'EVET' if ready_for_178 else 'HAYIR'}")
    print("\nDosyalar:")
    print(detail_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
