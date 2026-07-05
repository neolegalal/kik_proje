# -*- coding: utf-8 -*-
"""
178 - AKILLI KART BIRLESTIRME HAKEMI

Amaç:
- 168 production output JSONL dosyasındaki kartları karar bazında inceler.
- Aynı karar içinde üretilen kartların gerçekten bağımsız hukuki meseleler olup olmadığını denetler.
- Kart tekrarlarını, birleşmesi gereken kartları ve korunması gereken kartları belirler.
- 179 Kart Optimizasyon Motoru için plan üretir.

Kullanım:
  python ".py\\178_Akilli_Kart_Birlestirme_Hakemi.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\uretim_output\\168_production_output_20260630_182904.jsonl"

Limitli:
  python ".py\\178_Akilli_Kart_Birlestirme_Hakemi.py" "C:\\...\\168_production_output_x.jsonl" 5

Not:
- API maliyeti oluşur.
- DB'ye yazmaz.
- Sadece optimizasyon planı üretir.
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


BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

INPUT_PATTERN = os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl")

MODEL = os.getenv("OPENAI_MERGE_JUDGE_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini"))
SLEEP_SECONDS = 0.4

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


def build_prompt(karar_no, cards):
    system = """
Sen Kamu İhale Hukuku karar kartları için akıllı kart birleştirme hakemisin.

Görevin:
- Aynı karardan üretilen kartları incelemek.
- Hangi kartların gerçekten bağımsız hukuki mesele olduğunu belirlemek.
- Hangi kartların aynı meseleyi farklı kelimelerle tekrar ettiğini tespit etmek.
- Hangi kartların birleştirilmesi gerektiğini önermek.
- Hangi kartların korunması gerektiğini söylemek.
- WEB ve AI/RAG açısından kart sayısının optimal olup olmadığını değerlendirmek.

Yalnızca geçerli JSON üret.
Markdown, açıklama veya kod bloğu yazma.

Birleştirme kriterleri:
- Hukuki soru aynı meseleye cevap veriyorsa,
- Emsal ilke aynı hukuki sonucu tekrar ediyorsa,
- Konu/sonuç özeti yalnızca aynı olayın farklı ifade edilmiş hali ise,
- Anahtarlar büyük ölçüde aynıysa,
bu kartlar birleşebilir.

Koruma kriterleri:
- Farklı mevzuat hükmüne dayanıyorsa,
- Farklı yeterlik kriteri/şikayet sebebi ise,
- Ayrı danışmanlık sorusuna cevap veriyorsa,
- Ayrı WEB içeriği olarak değer taşıyorsa,
kart ayrı kalmalıdır.

JSON şeması:
{
  "karar_no": "",
  "original_card_count": 0,
  "recommended_card_count": 0,
  "decision": "PASS|MERGE_RECOMMENDED|REVIEW",
  "overall_redundancy_score": 0,
  "cards_to_keep": [1,2],
  "merge_groups": [
    {
      "group_id": 1,
      "cards": [1,3],
      "reason": "",
      "recommended_new_title": "",
      "recommended_new_hukuki_soru": "",
      "recommended_new_emsal_ilke": "",
      "priority": "HIGH|MEDIUM|LOW"
    }
  ],
  "cards_to_drop": [
    {
      "card_index": 2,
      "reason": ""
    }
  ],
  "independent_cards": [
    {
      "card_index": 1,
      "reason": ""
    }
  ],
  "web_recommendation": "",
  "rag_recommendation": "",
  "notes": ["..."]
}

Puan:
- overall_redundancy_score 0 = tekrar yok
- 100 = yoğun tekrar var

Karar:
- PASS: Kartlar bağımsız, birleşme gerekmez.
- MERGE_RECOMMENDED: En az bir birleştirme önerilir.
- REVIEW: Belirsiz veya insan kontrolü gerekir.
""".strip()

    user = f"""
KARAR NO:
{karar_no}

URETILEN KARTLAR:
{json.dumps(cards, ensure_ascii=False, indent=2)}
""".strip()

    return system, user


def normalize_review(obj, karar_no, original_count):
    if not isinstance(obj, dict):
        obj = {}

    decision = str(obj.get("decision", "")).strip().upper()
    if decision not in {"PASS", "MERGE_RECOMMENDED", "REVIEW"}:
        decision = "REVIEW"

    def as_int(v, default=0):
        try:
            return int(float(v))
        except Exception:
            return default

    merge_groups = obj.get("merge_groups", [])
    if not isinstance(merge_groups, list):
        merge_groups = []

    cards_to_keep = obj.get("cards_to_keep", [])
    if not isinstance(cards_to_keep, list):
        cards_to_keep = []

    cards_to_drop = obj.get("cards_to_drop", [])
    if not isinstance(cards_to_drop, list):
        cards_to_drop = []

    independent_cards = obj.get("independent_cards", [])
    if not isinstance(independent_cards, list):
        independent_cards = []

    notes = obj.get("notes", [])
    if not isinstance(notes, list):
        notes = [str(notes)]

    return {
        "karar_no": str(obj.get("karar_no") or karar_no).strip(),
        "original_card_count": as_int(obj.get("original_card_count"), original_count),
        "recommended_card_count": as_int(obj.get("recommended_card_count"), original_count),
        "decision": decision,
        "overall_redundancy_score": max(0, min(100, as_int(obj.get("overall_redundancy_score"), 0))),
        "cards_to_keep": cards_to_keep,
        "merge_groups": merge_groups,
        "cards_to_drop": cards_to_drop,
        "independent_cards": independent_cards,
        "web_recommendation": str(obj.get("web_recommendation", "")).strip(),
        "rag_recommendation": str(obj.get("rag_recommendation", "")).strip(),
        "notes": [str(x).strip() for x in notes if str(x).strip()],
    }


def call_ai(client, karar_no, cards):
    system, user = build_prompt(karar_no, cards)

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
    print("178 - AKILLI KART BIRLESTIRME HAKEMI")
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
    items = rows_by_decision(rows)

    limit = get_limit()
    if limit:
        items = items[:limit]

    detail_path = os.path.join(LOG_DIR, f"178_birlestirme_hakemi_detay_{run_tag}.jsonl")
    raw_dir = os.path.join(LOG_DIR, f"178_birlestirme_raw_{run_tag}")
    os.makedirs(raw_dir, exist_ok=True)

    state_path = os.path.join(STATE_DIR, f"178_birlestirme_hakemi_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"178_akilli_kart_birlestirme_hakemi_raporu_{run_tag}.txt")

    print(f"\nInput       : {input_path}")
    print(f"Model       : {MODEL}")
    print(f"Karar sayısı : {len(items)}")
    print("-" * 80)

    pass_count = 0
    merge_count = 0
    review_count = 0
    error_count = 0
    total_original_cards = 0
    total_recommended_cards = 0
    total_redundancy = 0
    total_tokens = 0

    all_results = []

    for idx, item in enumerate(items, start=1):
        karar_no = item["karar_no"]
        cards = item["kartlar"]
        total_original_cards += len(cards)

        print(f"[{idx}/{len(items)}] Birleştirme analizi: {karar_no} | Kart: {len(cards)}")

        try:
            if len(cards) <= 1:
                review = {
                    "karar_no": karar_no,
                    "original_card_count": len(cards),
                    "recommended_card_count": len(cards),
                    "decision": "PASS",
                    "overall_redundancy_score": 0,
                    "cards_to_keep": [c["card_index"] for c in cards],
                    "merge_groups": [],
                    "cards_to_drop": [],
                    "independent_cards": [{"card_index": c["card_index"], "reason": "Tek kart bulundu."} for c in cards],
                    "web_recommendation": "Tek kartlı karar; birleştirme gerekmez.",
                    "rag_recommendation": "Tek kartlı karar; tekrar riski yok.",
                    "notes": ["AI çağrısı yapılmadı; tek kart otomatik PASS."],
                }
                raw = json.dumps(review, ensure_ascii=False, indent=2)
                usage = {}
            else:
                raw, review, usage = call_ai(client, karar_no, cards)

            raw_path = os.path.join(raw_dir, f"{idx:04d}_{re.sub(r'[^0-9A-Za-z_.-]+', '_', karar_no)}.txt")
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(raw or "")

            decision = review["decision"]
            if decision == "PASS":
                pass_count += 1
            elif decision == "MERGE_RECOMMENDED":
                merge_count += 1
            else:
                review_count += 1

            total_recommended_cards += review.get("recommended_card_count", len(cards))
            total_redundancy += review.get("overall_redundancy_score", 0)

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
                "original_cards": cards,
                "review": review,
                "usage": usage,
                "raw_response_path": raw_path,
            }
            append_jsonl(detail_path, row)
            all_results.append(row)

            print(f"{decision} | Orijinal: {review['original_card_count']} | Önerilen: {review['recommended_card_count']} | Tekrar: {review['overall_redundancy_score']} | Token: {usage.get('total_tokens')}")

        except Exception as e:
            error_count += 1
            row = {
                "run_id": run_tag,
                "time": now(),
                "status": "ERROR",
                "input_path": input_path,
                "karar_no": karar_no,
                "error": str(e),
                "traceback": traceback.format_exc(),
            }
            append_jsonl(detail_path, row)
            all_results.append(row)
            print(f"HATA | {str(e)}")

        time.sleep(SLEEP_SECONDS)

    decision_count = len(items)
    avg_redundancy = round(total_redundancy / decision_count, 2) if decision_count else 0
    reduction_count = max(0, total_original_cards - total_recommended_cards)
    reduction_rate = round((reduction_count / total_original_cards) * 100, 2) if total_original_cards else 0

    # 179'a geçiş: hata yoksa geçilebilir.
    ready_for_179 = decision_count > 0 and error_count == 0

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_path": input_path,
        "model": MODEL,
        "decision_count": decision_count,
        "pass_count": pass_count,
        "merge_recommended_count": merge_count,
        "review_count": review_count,
        "error_count": error_count,
        "total_original_cards": total_original_cards,
        "total_recommended_cards": total_recommended_cards,
        "reduction_count": reduction_count,
        "reduction_rate": reduction_rate,
        "avg_redundancy_score": avg_redundancy,
        "total_tokens": total_tokens,
        "detail_path": detail_path,
        "raw_dir": raw_dir,
        "ready_for_179": ready_for_179,
        "next_step": "179_Kart_Optimizasyon_Motoru.py",
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("178 - AKILLI KART BIRLESTIRME HAKEMI RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                         : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input                         : {input_path}\n")
        f.write(f"Model                         : {MODEL}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"Karar sayısı                   : {decision_count}\n")
        f.write(f"PASS                           : {pass_count}\n")
        f.write(f"Birleştirme önerilen           : {merge_count}\n")
        f.write(f"Review gereken                 : {review_count}\n")
        f.write(f"Hata                           : {error_count}\n")
        f.write(f"Orijinal kart                  : {total_original_cards}\n")
        f.write(f"Önerilen kart                  : {total_recommended_cards}\n")
        f.write(f"Azalma                         : {reduction_count} kart (%{reduction_rate})\n")
        f.write(f"Ortalama tekrar puanı          : {avg_redundancy} / 100\n")
        f.write(f"Toplam token                   : {total_tokens}\n")
        f.write(f"179'a geçilebilir mi           : {'EVET' if ready_for_179 else 'HAYIR'}\n\n")

        f.write("KARAR BAZLI BIRLESTIRME PLANI\n")
        f.write("-" * 80 + "\n")
        for r in all_results:
            if r["status"] != "OK":
                f.write(f"\nKarar: {r.get('karar_no')} | ERROR | {r.get('error')}\n")
                continue
            rev = r["review"]
            f.write(f"\nKarar: {r['karar_no']} | {rev['decision']} | Orijinal: {rev['original_card_count']} | Önerilen: {rev['recommended_card_count']} | Tekrar: {rev['overall_redundancy_score']}\n")
            f.write(f"WEB: {rev.get('web_recommendation','')}\n")
            f.write(f"RAG: {rev.get('rag_recommendation','')}\n")

            if rev.get("merge_groups"):
                f.write("Birleştirme grupları:\n")
                for g in rev["merge_groups"]:
                    f.write(f"  - Grup {g.get('group_id')} | Kartlar: {g.get('cards')} | Öncelik: {g.get('priority')}\n")
                    f.write(f"    Neden: {g.get('reason')}\n")
                    f.write(f"    Yeni başlık: {g.get('recommended_new_title')}\n")
                    f.write(f"    Yeni soru: {g.get('recommended_new_hukuki_soru')}\n")
                    f.write(f"    Yeni ilke: {g.get('recommended_new_emsal_ilke')}\n")

            if rev.get("cards_to_drop"):
                f.write("Silinmesi/atılması önerilen kartlar:\n")
                for d in rev["cards_to_drop"]:
                    f.write(f"  - Kart {d.get('card_index')}: {d.get('reason')}\n")

            if rev.get("independent_cards"):
                f.write("Bağımsız kartlar:\n")
                for ic in rev["independent_cards"]:
                    f.write(f"  - Kart {ic.get('card_index')}: {ic.get('reason')}\n")

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

    print("\n178 BIRLESTIRME HAKEMI TAMAMLANDI")
    print("-" * 80)
    print(f"Karar sayısı                   : {decision_count}")
    print(f"PASS                           : {pass_count}")
    print(f"Birleştirme önerilen           : {merge_count}")
    print(f"Review gereken                 : {review_count}")
    print(f"Hata                           : {error_count}")
    print(f"Orijinal kart                  : {total_original_cards}")
    print(f"Önerilen kart                  : {total_recommended_cards}")
    print(f"Azalma                         : {reduction_count} kart (%{reduction_rate})")
    print(f"Ortalama tekrar puanı          : {avg_redundancy} / 100")
    print(f"Toplam token                   : {total_tokens}")
    print(f"179'a geçilebilir mi           : {'EVET' if ready_for_179 else 'HAYIR'}")
    print("\nDosyalar:")
    print(detail_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
