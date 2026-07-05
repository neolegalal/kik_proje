# -*- coding: utf-8 -*-
"""
172 - AI KALITE HAKEMI

Amaç:
- 168 üretim çıktısındaki kartları GPT ile kalite hakemliğinden geçirir.
- 171 kural tabanlı kontrolden farklı olarak içerik doğruluğunu semantik değerlendirir.
- Özellikle şu kalite alanlarını puanlar:
  * hukuki_soru danışmanlıkta kullanılabilir mi?
  * konu_ozeti gerçekten kararın konusunu anlatıyor mu?
  * sonuc_ozeti gerçekten Kurulun sonucunu anlatıyor mu?
  * konu_ozeti ile sonuc_ozeti ayrımı doğru mu?
  * emsal_ilke genellenebilir hukuk ilkesi mi?
  * anahtar RAG / arama için anlamlı mı?
  * mevzuat kararla ilişkili görünüyor mu?
  * genel WEB + AI danışmanlık kalitesi yeterli mi?

Kullanım:
  python ".py\\172_AI_Kalite_Hakemi.py"

Belirli JSONL için:
  python ".py\\172_AI_Kalite_Hakemi.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\uretim_output\\168_production_output_20260630_180431.jsonl"

Not:
- Bu dosya DB'ye yazmaz.
- API maliyeti oluşur. Mini testlerde kullanılması önerilir.
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

MODEL = os.getenv("OPENAI_JUDGE_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
SLEEP_SECONDS = 0.4

# Mini hakem için default üst sınır. Argümanla JSONL verildiğinde tüm kartları işler.
DEFAULT_MAX_CARDS = 30

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


# =============================================================================
# YARDIMCI FONKSİYONLAR
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
        env_path = os.path.join(BASE_DIR, ".env")
        env_path2 = os.path.join(PY_DIR, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        if os.path.exists(env_path2):
            load_dotenv(env_path2)
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
                rows.append({
                    "_json_error": str(e),
                    "_line_no": line_no,
                    "_raw": line[:500],
                })
    return rows


def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


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

    raise ValueError("Hakem yanıtı JSON olarak parse edilemedi.")


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


def flatten_cards(rows):
    cards = []
    for row_idx, r in enumerate(rows, start=1):
        if "_json_error" in r:
            continue
        if r.get("status") != "OK":
            continue

        karar_no = str(r.get("karar_no") or r.get("orijinal_karar_no") or "").strip()
        dosya_adi = str(r.get("dosya_adi") or "").strip()
        kartlar = r.get("kartlar", [])
        if not isinstance(kartlar, list):
            continue

        for card_idx, k in enumerate(kartlar, start=1):
            if not isinstance(k, dict):
                continue
            cards.append({
                "row_index": row_idx,
                "card_index": card_idx,
                "karar_no": karar_no,
                "dosya_adi": dosya_adi,
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
    return cards


def build_judge_prompt(card):
    system_msg = """
Sen Kamu İhale Kurulu karar kartları için kalite hakemisin.
Görevin verilen kartı WEB yayını ve RAG/AI danışmanlık bilgi tabanı açısından değerlendirmektir.

Yalnızca geçerli JSON üret.
Markdown, açıklama veya kod bloğu yazma.

Her alanı 0-100 arasında puanla.
Puanlamada sert ama adil ol.

Önemli ayrım:
- konu_ozeti: Olayı, başvuru iddiasını ve Kurulun neyi incelediğini anlatmalı. Sonucu esas konu yapmamalı.
- sonuc_ozeti: Kurulun vardığı sonucu ve işlem türünü anlatmalı.
- hukuki_soru: Kurum/şirket adı içermeden genellenebilir danışmanlık sorusu olmalı.
- emsal_ilke: Karardan çıkarılan genellenebilir hukuk ilkesi olmalı.
- anahtar: Arama/RAG için anlamlı anahtar ifadeler olmalı.
- mevzuat: Kararla ilişkili mevzuat maddeleri olmalı; kesin emin olunamıyorsa düşük puan ver ama tamamen uydurma var diyebilmek için güçlü belirti ara.

JSON şeması:
{
  "overall_score": 0,
  "decision": "PASS|WARNING|FAIL",
  "scores": {
    "hukuki_soru": 0,
    "konu_ozeti": 0,
    "sonuc_ozeti": 0,
    "konu_sonuc_ayrimi": 0,
    "emsal_ilke": 0,
    "anahtar": 0,
    "mevzuat": 0,
    "web_kullanilabilirlik": 0,
    "rag_kullanilabilirlik": 0
  },
  "issues": ["..."],
  "reason": "Kısa gerekçe."
}

Karar kuralları:
- overall_score >= 85 ve ciddi sorun yoksa PASS.
- 70-84 arası veya küçük sorun varsa WARNING.
- 70 altı ya da konu/sonuç/hukuki soru ciddi hatalıysa FAIL.
""".strip()

    user_msg = f"""
KART:
{json.dumps(card, ensure_ascii=False, indent=2)}
""".strip()

    return system_msg, user_msg


def normalize_judgement(obj):
    if not isinstance(obj, dict):
        obj = {}

    scores = obj.get("scores", {})
    if not isinstance(scores, dict):
        scores = {}

    def score(name):
        try:
            v = int(float(scores.get(name, 0)))
            return max(0, min(100, v))
        except Exception:
            return 0

    try:
        overall = int(float(obj.get("overall_score", 0)))
        overall = max(0, min(100, overall))
    except Exception:
        vals = [score(k) for k in [
            "hukuki_soru", "konu_ozeti", "sonuc_ozeti", "konu_sonuc_ayrimi",
            "emsal_ilke", "anahtar", "mevzuat", "web_kullanilabilirlik", "rag_kullanilabilirlik"
        ]]
        overall = int(sum(vals) / len(vals)) if vals else 0

    decision = str(obj.get("decision", "")).strip().upper()
    if decision not in {"PASS", "WARNING", "FAIL"}:
        if overall >= 85:
            decision = "PASS"
        elif overall >= 70:
            decision = "WARNING"
        else:
            decision = "FAIL"

    issues = obj.get("issues", [])
    if not isinstance(issues, list):
        issues = [str(issues)]

    return {
        "overall_score": overall,
        "decision": decision,
        "scores": {
            "hukuki_soru": score("hukuki_soru"),
            "konu_ozeti": score("konu_ozeti"),
            "sonuc_ozeti": score("sonuc_ozeti"),
            "konu_sonuc_ayrimi": score("konu_sonuc_ayrimi"),
            "emsal_ilke": score("emsal_ilke"),
            "anahtar": score("anahtar"),
            "mevzuat": score("mevzuat"),
            "web_kullanilabilirlik": score("web_kullanilabilirlik"),
            "rag_kullanilabilirlik": score("rag_kullanilabilirlik"),
        },
        "issues": [str(x).strip() for x in issues if str(x).strip()],
        "reason": str(obj.get("reason", "")).strip(),
    }


def call_judge(client, card):
    system_msg, user_msg = build_judge_prompt(card)

    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0,
    )

    raw = resp.choices[0].message.content
    parsed = parse_json_response(raw)
    judgement = normalize_judgement(parsed)

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
    print("172 - AI KALITE HAKEMI")
    print("=" * 80)

    run_tag = tag()

    if len(sys.argv) >= 2:
        input_path = sys.argv[1]
        max_cards = None
    else:
        input_path = latest_file(INPUT_PATTERN)
        max_cards = DEFAULT_MAX_CARDS

    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError("168 production output JSONL bulunamadı.")

    api_key = load_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY bulunamadı. .env içine OPENAI_API_KEY=... ekle.")

    if OpenAI is None:
        raise RuntimeError("openai paketi yüklü değil. Komut: pip install openai")

    client = OpenAI(api_key=api_key)

    rows = read_jsonl(input_path)
    cards = flatten_cards(rows)

    if max_cards:
        cards = cards[:max_cards]

    detail_jsonl = os.path.join(LOG_DIR, f"172_ai_kalite_hakemi_detay_{run_tag}.jsonl")
    raw_dir = os.path.join(LOG_DIR, f"172_ai_judge_raw_{run_tag}")
    os.makedirs(raw_dir, exist_ok=True)

    state_path = os.path.join(STATE_DIR, f"172_ai_kalite_hakemi_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"172_ai_kalite_hakemi_raporu_{run_tag}.txt")

    print(f"\nKontrol edilen dosya : {input_path}")
    print(f"Model                : {MODEL}")
    print(f"Kart sayısı          : {len(cards)}")
    print("-" * 80)

    pass_count = 0
    warning_count = 0
    fail_count = 0
    total_score = 0
    total_tokens = 0
    errors = 0

    worst = []

    for i, card in enumerate(cards, start=1):
        print(f"[{i}/{len(cards)}] Hakem kontrolü: {card.get('karar_no')} | Kart {card.get('card_index')}")

        try:
            raw, judgement, usage = call_judge(client, card)

            raw_path = os.path.join(raw_dir, f"{i:04d}_{card.get('karar_no','').replace('/','_')}_kart_{card.get('card_index')}.txt")
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(raw or "")

            decision = judgement["decision"]
            if decision == "PASS":
                pass_count += 1
            elif decision == "WARNING":
                warning_count += 1
            else:
                fail_count += 1

            total_score += judgement["overall_score"]

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
                "card": card,
                "judgement": judgement,
                "usage": usage,
                "raw_response_path": raw_path,
            }
            append_jsonl(detail_jsonl, row)

            worst.append({
                "karar_no": card.get("karar_no"),
                "card_index": card.get("card_index"),
                "baslik": card.get("baslik"),
                "score": judgement["overall_score"],
                "decision": decision,
                "issues": judgement.get("issues", []),
                "reason": judgement.get("reason", ""),
            })

            print(f"{decision} | Puan: {judgement['overall_score']} | Token: {usage.get('total_tokens')}")

        except Exception as e:
            errors += 1
            append_jsonl(detail_jsonl, {
                "run_id": run_tag,
                "time": now(),
                "status": "ERROR",
                "input_path": input_path,
                "card": card,
                "error": str(e),
                "traceback": traceback.format_exc(),
            })
            print(f"HATA | {str(e)}")

        time.sleep(SLEEP_SECONDS)

    total = len(cards)
    avg_score = round(total_score / total, 2) if total else 0
    pass_rate = round((pass_count / total) * 100, 2) if total else 0
    fail_rate = round((fail_count / total) * 100, 2) if total else 0

    # Büyük üretim kabul eşiği:
    # FAIL yoksa, ortalama >=85 ise ve PASS oranı >=80 ise geçilebilir.
    ready_for_master = total > 0 and errors == 0 and fail_count == 0 and avg_score >= 85 and pass_rate >= 80

    worst_sorted = sorted(worst, key=lambda x: x["score"])[:10]

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_path": input_path,
        "model": MODEL,
        "cards_checked": total,
        "pass_count": pass_count,
        "warning_count": warning_count,
        "fail_count": fail_count,
        "error_count": errors,
        "average_score": avg_score,
        "pass_rate": pass_rate,
        "fail_rate": fail_rate,
        "total_tokens": total_tokens,
        "detail_jsonl": detail_jsonl,
        "ready_for_173": ready_for_master,
        "next_step": "173_Master_Acceptance_Test.py",
        "worst_cards": worst_sorted,
    }

    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("172 - AI KALITE HAKEMI RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                  : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Kontrol edilen dosya   : {input_path}\n")
        f.write(f"Model                  : {MODEL}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Kontrol edilen kart     : {total}\n")
        f.write(f"PASS kart               : {pass_count}\n")
        f.write(f"WARNING kart            : {warning_count}\n")
        f.write(f"FAIL kart               : {fail_count}\n")
        f.write(f"Hata                    : {errors}\n")
        f.write(f"Ortalama puan           : {avg_score} / 100\n")
        f.write(f"PASS oranı              : %{pass_rate}\n")
        f.write(f"FAIL oranı              : %{fail_rate}\n")
        f.write(f"Toplam token            : {total_tokens}\n")
        f.write(f"173'e geçilebilir mi    : {'EVET' if ready_for_master else 'HAYIR'}\n\n")

        f.write("EN DUSUK PUANLI KARTLAR\n")
        f.write("-" * 80 + "\n")
        if worst_sorted:
            for w in worst_sorted:
                f.write(f"Karar: {w['karar_no']} | Kart: {w['card_index']} | Puan: {w['score']} | Karar: {w['decision']}\n")
                f.write(f"Başlık: {w['baslik']}\n")
                f.write(f"Issues: {w['issues']}\n")
                f.write(f"Gerekçe: {w['reason']}\n")
                f.write("-" * 40 + "\n")
        else:
            f.write("Yok\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Detay JSONL             : {detail_jsonl}\n")
        f.write(f"Raw klasör              : {raw_dir}\n")
        f.write(f"State JSON              : {state_path}\n")
        f.write(f"Rapor                   : {rapor_path}\n")

    print("\n172 AI KALITE HAKEMI TAMAMLANDI")
    print("-" * 80)
    print(f"Kontrol edilen kart     : {total}")
    print(f"PASS kart               : {pass_count}")
    print(f"WARNING kart            : {warning_count}")
    print(f"FAIL kart               : {fail_count}")
    print(f"Hata                    : {errors}")
    print(f"Ortalama puan           : {avg_score} / 100")
    print(f"PASS oranı              : %{pass_rate}")
    print(f"Toplam token            : {total_tokens}")
    print(f"173'e geçilebilir mi    : {'EVET' if ready_for_master else 'HAYIR'}")

    print("\nDosyalar:")
    print(detail_jsonl)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
