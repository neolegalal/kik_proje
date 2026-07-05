# -*- coding: utf-8 -*-
"""
175 v2 - AI DESTEKLI HUKUKI MESELE KAPSAM ANALIZ MOTORU

Amaç:
- 168 production output JSONL dosyasını okur.
- Her kararın PDF/TXT metnini yeniden okur.
- GPT ile karardaki bağımsız hukuki meseleleri çıkarır.
- Üretilen kartların bu meseleleri kapsayıp kapsamadığını değerlendirir.
- Eksik mesele, tekrar eden kart, aşırı genelleme riski ve coverage puanı üretir.

Kullanım:
  python ".py\\175_v2_AI_Hukuki_Mesele_Kapsam_Analiz_Motoru.py"

Belirli 168 çıktısı için:
  python ".py\\175_v2_AI_Hukuki_Mesele_Kapsam_Analiz_Motoru.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\uretim_output\\168_production_output_20260630_182904.jsonl"

Limitli:
  python ".py\\175_v2_AI_Hukuki_Mesele_Kapsam_Analiz_Motoru.py" "C:\\...\\168_production_output_x.jsonl" 5

Not:
- API maliyeti oluşur.
- DB'ye yazmaz.
- Büyük üretim öncesi mini batchlerde kalite/kapsam denetimi için kullanılır.
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

MODEL = os.getenv("OPENAI_COVERAGE_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
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
    by_decision = {}
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
                "sonuc_tipi": str(k.get("sonuc_tipi", "")).strip(),
                "emsal_ilke": str(k.get("emsal_ilke", "")).strip(),
                "anahtar": normalize_list(k.get("anahtar")),
                "mevzuat": normalize_list(k.get("mevzuat")),
                "guven": str(k.get("guven", "")).strip(),
            })
        by_decision[karar_no] = {
            "karar_no": karar_no,
            "dosya_adi": str(row.get("dosya_adi") or "").strip(),
            "dosya_yolu": str(row.get("dosya_yolu") or "").strip(),
            "kartlar": cards,
        }
    return by_decision


def get_limit():
    if len(sys.argv) >= 3:
        try:
            return int(sys.argv[2])
        except Exception:
            return None
    return None


def build_prompt(karar_no, karar_metni, cards):
    system = """
Sen Kamu İhale Kurulu kararları için hukukî kapsam ve kalite hakemisin.

Görevin:
1. Karar metnindeki bağımsız hukuki meseleleri tespit etmek.
2. Üretilen kartların bu meseleleri kapsayıp kapsamadığını değerlendirmek.
3. Eksik kalan önemli meseleleri bulmak.
4. Aynı mesele için gereksiz tekrar eden kartları tespit etmek.
5. Emsal ilke veya hukuki sorularda aşırı genelleme riski varsa belirtmek.
6. WEB ve AI/RAG hedefleri açısından karar kapsam puanı vermek.

Yalnızca geçerli JSON üret.
Markdown, açıklama, kod bloğu yazma.

Bağımsız hukuki mesele:
- Kararda ayrı hukuki değerlendirme konusu yapılan,
- farklı mevzuat hükmüne veya farklı yeterlik/şikayet sebebine dayanan,
- ayrı bir danışmanlık sorusuna dönüşebilen meseledir.

Önem puanı:
- 90-100: Danışmanlık ve içtihat değeri çok yüksek mesele
- 75-89: Önemli mesele
- 50-74: Orta önem
- 0-49: tali/sonuçsal mesele

JSON şeması:
{
  "karar_no": "",
  "decision_summary": "",
  "legal_issues": [
    {
      "issue_id": 1,
      "issue_title": "",
      "issue_question": "",
      "importance": 0,
      "legal_basis": [],
      "source_evidence": "Karar metninden kısa dayanak/parafraz",
      "should_have_card": true
    }
  ],
  "card_coverage": [
    {
      "card_index": 1,
      "covered_issue_ids": [1],
      "coverage_quality": 0,
      "is_duplicate_of_card": null,
      "overgeneralization_risk": "LOW|MEDIUM|HIGH",
      "notes": ""
    }
  ],
  "missing_issues": [
    {
      "issue_id": 2,
      "issue_title": "",
      "importance": 0,
      "reason": ""
    }
  ],
  "duplicate_cards": [
    {
      "card_a": 1,
      "card_b": 3,
      "similarity_reason": ""
    }
  ],
  "coverage_score": 0,
  "web_score": 0,
  "rag_score": 0,
  "decision": "PASS|WARNING|FAIL",
  "improvement_notes": ["..."]
}

Karar kuralları:
- Önemli meselelerin çoğu karta dönüşmüşse PASS.
- 75+ önem puanlı mesele eksikse genelde WARNING veya FAIL.
- Çok tekrar varsa WARNING.
- Coverage score, kararın önemli hukuki meselelerinin ne kadarının kartlara doğru dönüştüğünü göstermeli.
""".strip()

    user = f"""
KARAR NO:
{karar_no}

KARAR METNI:
{karar_metni}

URETILEN KARTLAR:
{json.dumps(cards, ensure_ascii=False, indent=2)}
""".strip()

    return system, user


def normalize_judgement(obj, karar_no):
    if not isinstance(obj, dict):
        obj = {}

    def int_score(name, default=0):
        try:
            return max(0, min(100, int(float(obj.get(name, default)))))
        except Exception:
            return default

    issues = obj.get("legal_issues", [])
    if not isinstance(issues, list):
        issues = []

    coverage = obj.get("card_coverage", [])
    if not isinstance(coverage, list):
        coverage = []

    missing = obj.get("missing_issues", [])
    if not isinstance(missing, list):
        missing = []

    duplicates = obj.get("duplicate_cards", [])
    if not isinstance(duplicates, list):
        duplicates = []

    decision = str(obj.get("decision", "")).strip().upper()
    if decision not in {"PASS", "WARNING", "FAIL"}:
        score = int_score("coverage_score", 0)
        if score >= 85:
            decision = "PASS"
        elif score >= 70:
            decision = "WARNING"
        else:
            decision = "FAIL"

    notes = obj.get("improvement_notes", [])
    if not isinstance(notes, list):
        notes = [str(notes)]

    return {
        "karar_no": str(obj.get("karar_no") or karar_no).strip(),
        "decision_summary": str(obj.get("decision_summary", "")).strip(),
        "legal_issues": issues,
        "card_coverage": coverage,
        "missing_issues": missing,
        "duplicate_cards": duplicates,
        "coverage_score": int_score("coverage_score", 0),
        "web_score": int_score("web_score", 0),
        "rag_score": int_score("rag_score", 0),
        "decision": decision,
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
    judgement = normalize_judgement(parsed, karar_no)

    usage = {}
    try:
        usage = {
            "prompt_tokens": getattr(resp.usage, "prompt_tokens", None),
            "completion_tokens": getattr(resp.usage, "completion_tokens", None),
            "total_tokens": getattr(resp.usage, "total_tokens", None),
        }
    except Exception:
        usage = {}

    return raw, judgement, usage


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 80)
    print("175 v2 - AI DESTEKLI HUKUKI MESELE KAPSAM ANALIZ MOTORU")
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
    by_decision = flatten_rows_by_decision(rows)
    items = list(by_decision.values())

    limit = get_limit()
    if limit:
        items = items[:limit]

    detail_path = os.path.join(LOG_DIR, f"175_v2_ai_kapsam_detay_{run_tag}.jsonl")
    raw_dir = os.path.join(LOG_DIR, f"175_v2_ai_kapsam_raw_{run_tag}")
    os.makedirs(raw_dir, exist_ok=True)

    state_path = os.path.join(STATE_DIR, f"175_v2_ai_kapsam_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"175_v2_ai_hukuki_mesele_kapsam_raporu_{run_tag}.txt")

    print(f"\nInput       : {input_path}")
    print(f"Model       : {MODEL}")
    print(f"Karar sayısı : {len(items)}")
    print("-" * 80)

    pass_count = 0
    warning_count = 0
    fail_count = 0
    error_count = 0
    total_coverage = 0
    total_web = 0
    total_rag = 0
    total_tokens = 0

    all_results = []

    for idx, item in enumerate(items, start=1):
        karar_no = item["karar_no"]
        dosya_yolu = item["dosya_yolu"]
        cards = item["kartlar"]

        print(f"[{idx}/{len(items)}] Kapsam analizi: {karar_no} | Kart: {len(cards)}")

        try:
            if not dosya_yolu or not os.path.exists(dosya_yolu):
                raise RuntimeError(f"Dosya bulunamadı: {dosya_yolu}")

            metin = clean_text(extract_text(dosya_yolu))
            if len(metin) < 300:
                raise RuntimeError(f"Karar metni çok kısa veya okunamadı: {len(metin)}")

            metin = truncate_text(metin)

            raw, judgement, usage = call_ai(client, karar_no, metin, cards)

            raw_path = os.path.join(raw_dir, f"{idx:04d}_{re.sub(r'[^0-9A-Za-z_.-]+', '_', karar_no)}.txt")
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(raw or "")

            decision = judgement["decision"]
            if decision == "PASS":
                pass_count += 1
            elif decision == "WARNING":
                warning_count += 1
            else:
                fail_count += 1

            total_coverage += judgement["coverage_score"]
            total_web += judgement["web_score"]
            total_rag += judgement["rag_score"]

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
                "judgement": judgement,
                "usage": usage,
                "raw_response_path": raw_path,
            }
            append_jsonl(detail_path, row)
            all_results.append(row)

            print(f"{decision} | Coverage: {judgement['coverage_score']} | WEB: {judgement['web_score']} | RAG: {judgement['rag_score']} | Token: {usage.get('total_tokens')}")

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

    total = len(items)
    avg_coverage = round(total_coverage / total, 2) if total else 0
    avg_web = round(total_web / total, 2) if total else 0
    avg_rag = round(total_rag / total, 2) if total else 0
    fail_rate = round((fail_count / total) * 100, 2) if total else 0

    ready_for_176 = total > 0 and error_count == 0 and avg_coverage >= 80 and fail_rate <= 20

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_path": input_path,
        "model": MODEL,
        "decision_count": total,
        "pass_count": pass_count,
        "warning_count": warning_count,
        "fail_count": fail_count,
        "error_count": error_count,
        "avg_coverage_score": avg_coverage,
        "avg_web_score": avg_web,
        "avg_rag_score": avg_rag,
        "fail_rate": fail_rate,
        "total_tokens": total_tokens,
        "detail_path": detail_path,
        "raw_dir": raw_dir,
        "ready_for_176": ready_for_176,
        "next_step": "176_Hukuki_Mesele_Onceliklendirme_Motoru.py",
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("175 v2 - AI DESTEKLI HUKUKI MESELE KAPSAM ANALIZ RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                  : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input                  : {input_path}\n")
        f.write(f"Model                  : {MODEL}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Karar sayısı            : {total}\n")
        f.write(f"PASS                    : {pass_count}\n")
        f.write(f"WARNING                 : {warning_count}\n")
        f.write(f"FAIL                    : {fail_count}\n")
        f.write(f"Hata                    : {error_count}\n")
        f.write(f"Ortalama coverage       : {avg_coverage} / 100\n")
        f.write(f"Ortalama WEB            : {avg_web} / 100\n")
        f.write(f"Ortalama RAG            : {avg_rag} / 100\n")
        f.write(f"FAIL oranı              : %{fail_rate}\n")
        f.write(f"Toplam token            : {total_tokens}\n")
        f.write(f"176'ya geçilebilir mi   : {'EVET' if ready_for_176 else 'HAYIR'}\n\n")

        f.write("KARAR BAZLI OZET\n")
        f.write("-" * 80 + "\n")
        for r in all_results:
            if r["status"] != "OK":
                f.write(f"\nKarar: {r.get('karar_no')} | ERROR | {r.get('error')}\n")
                continue

            j = r["judgement"]
            f.write(f"\nKarar: {r['karar_no']} | {j['decision']} | Coverage: {j['coverage_score']} | WEB: {j['web_score']} | RAG: {j['rag_score']}\n")
            f.write(f"Özet: {j.get('decision_summary','')}\n")
            f.write("Tespit edilen hukuki meseleler:\n")
            for issue in j.get("legal_issues", []):
                f.write(f"  - [{issue.get('issue_id')}] {issue.get('issue_title')} | önem={issue.get('importance')} | kart olmalı={issue.get('should_have_card')}\n")
            if j.get("missing_issues"):
                f.write("Eksik meseleler:\n")
                for m in j.get("missing_issues", []):
                    f.write(f"  - [{m.get('issue_id')}] {m.get('issue_title')} | önem={m.get('importance')} | {m.get('reason')}\n")
            if j.get("duplicate_cards"):
                f.write("Tekrar eden kartlar:\n")
                for d in j.get("duplicate_cards", []):
                    f.write(f"  - Kart {d.get('card_a')} / Kart {d.get('card_b')}: {d.get('similarity_reason')}\n")
            if j.get("improvement_notes"):
                f.write("İyileştirme notları:\n")
                for note in j.get("improvement_notes", []):
                    f.write(f"  - {note}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Detay JSONL             : {detail_path}\n")
        f.write(f"Raw klasör              : {raw_dir}\n")
        f.write(f"State JSON              : {state_path}\n")
        f.write(f"Rapor                   : {rapor_path}\n")

    print("\n175 v2 AI KAPSAM ANALIZI TAMAMLANDI")
    print("-" * 80)
    print(f"Karar sayısı            : {total}")
    print(f"PASS                    : {pass_count}")
    print(f"WARNING                 : {warning_count}")
    print(f"FAIL                    : {fail_count}")
    print(f"Hata                    : {error_count}")
    print(f"Ortalama coverage       : {avg_coverage} / 100")
    print(f"Ortalama WEB            : {avg_web} / 100")
    print(f"Ortalama RAG            : {avg_rag} / 100")
    print(f"Toplam token            : {total_tokens}")
    print(f"176'ya geçilebilir mi   : {'EVET' if ready_for_176 else 'HAYIR'}")
    print("\nDosyalar:")
    print(detail_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
