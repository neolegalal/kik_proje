# -*- coding: utf-8 -*-
"""
158 - 128 PRODUCTION JSONL RUNNER

Amaç:
- En güncel 155C1 input JSONL dosyasını okur.
- İlk etapta varsayılan 5 PDF/TXT işler.
- PDF metnini çıkarır.
- OpenAI ile hukuki kart üretir.
- Sonuçları JSONL olarak kaydeder.
- DB'ye yazmaz.

Kullanım:
  python ".py\\158_128_Production_JSONL_Runner.py"

Limit ile:
  python ".py\\158_128_Production_JSONL_Runner.py" 5
  python ".py\\158_128_Production_JSONL_Runner.py" 20

Not:
- OPENAI_API_KEY .env içinde veya ortam değişkeninde olmalı.
- DB_YAZ = False; bu dosya DB'ye yazmaz.
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


# =============================================================================
# AYARLAR
# =============================================================================

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
URETIM_INPUT_DIR = os.path.join(BASE_DIR, "uretim_input")
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

INPUT_PATTERN = os.path.join(URETIM_INPUT_DIR, "155C1_136E_pilot_input_*.jsonl")

DEFAULT_LIMIT = 5
DB_YAZ = False

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
MAX_TEXT_CHARS = 45000
SLEEP_SECONDS = 0.5

os.makedirs(URETIM_OUTPUT_DIR, exist_ok=True)
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


def get_limit():
    if len(sys.argv) >= 2:
        try:
            n = int(sys.argv[1])
            return n if n > 0 else DEFAULT_LIMIT
        except Exception:
            return DEFAULT_LIMIT
    return DEFAULT_LIMIT


def read_jsonl(path):
    rows = []
    if not path or not os.path.exists(path):
        return rows

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


def load_api_key():
    if load_dotenv:
        env_path = os.path.join(BASE_DIR, ".env")
        env_path2 = os.path.join(PY_DIR, ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)
        if os.path.exists(env_path2):
            load_dotenv(env_path2)

    return os.getenv("OPENAI_API_KEY", "").strip()


def extract_text_from_pdf(pdf_path):
    if PdfReader is None:
        raise RuntimeError("pypdf/PyPDF2 yüklü değil. Komut: pip install pypdf")

    reader = PdfReader(pdf_path)
    parts = []

    for i, page in enumerate(reader.pages, start=1):
        try:
            txt = page.extract_text() or ""
        except Exception:
            txt = ""

        if txt.strip():
            parts.append(f"\n\n--- SAYFA {i} ---\n{txt}")

    return "\n".join(parts).strip()


def extract_text_from_txt(txt_path):
    for enc in ["utf-8", "utf-8-sig", "cp1254", "latin-1"]:
        try:
            with open(txt_path, "r", encoding=enc, errors="ignore") as f:
                return f.read()
        except Exception:
            continue
    return ""


def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    if ext == ".txt":
        return extract_text_from_txt(file_path)

    raise RuntimeError(f"Desteklenmeyen dosya uzantısı: {ext}")


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

    head = text[:int(max_chars * 0.75)]
    tail = text[-int(max_chars * 0.25):]
    return head + "\n\n...[METİN ORTADAN KISALTILDI]...\n\n" + tail


def build_prompt(karar_no, dosya_adi, karar_metni):
    system_msg = """
Sen kamu ihale hukuku alanında çalışan uzman bir karar analiz motorusun.
Görevin Kamu İhale Kurulu kararından hukuki kartlar üretmektir.

Çıktı yalnızca geçerli JSON olmalıdır.
Markdown, açıklama, kod bloğu, yorum yazma.

JSON şeması:
{
  "karar_no": "...",
  "kartlar": [
    {
      "baslik": "...",
      "hukuki_soru": "...",
      "sonuc_tipi": "KABUL|RET|DÜZELTİCİ İŞLEM|İPTAL|KARAR VERİLMESİNE YER OLMADIĞI|DİĞER",
      "sonuc": "...",
      "emsal_ilke": "...",
      "anahtar": "...",
      "mevzuat": "...",
      "guven": "Yüksek|Orta|Düşük"
    }
  ]
}

Kurallar:
- Kararı gereksiz parçalara bölme.
- Aynı hukuki ilkeyi mükerrer kart yapma.
- Sonuç tipi ile sonuç metni çelişmesin.
- Başvuru sahibinin iddiası yerindeyse genelde KABUL veya DÜZELTİCİ İŞLEM olur.
- İddia yerinde değilse RET olur.
- Emsal ilke sonuç cümlesini tekrar etmesin; genellenebilir hukuk ilkesi olsun.
- Güven seviyesini abartma; tereddüt varsa Orta kullan.
- En fazla 6 kart üret.
- Karar gerçekten analiz edilemiyorsa kartlar boş liste olabilir.
""".strip()

    user_msg = f"""
KARAR NO:
{karar_no}

DOSYA:
{dosya_adi}

KARAR METNİ:
{karar_metni}
""".strip()

    return system_msg, user_msg


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

    raise ValueError("OpenAI yanıtı JSON olarak parse edilemedi.")


def normalize_result(obj, fallback_karar_no):
    if not isinstance(obj, dict):
        obj = {}

    karar_no = str(obj.get("karar_no") or fallback_karar_no).strip()
    kartlar = obj.get("kartlar", [])

    if not isinstance(kartlar, list):
        kartlar = []

    normalized_cards = []

    for k in kartlar:
        if not isinstance(k, dict):
            continue

        normalized_cards.append({
            "baslik": str(k.get("baslik", "")).strip(),
            "hukuki_soru": str(k.get("hukuki_soru", "")).strip(),
            "sonuc_tipi": str(k.get("sonuc_tipi", "")).strip(),
            "sonuc": str(k.get("sonuc", "")).strip(),
            "emsal_ilke": str(k.get("emsal_ilke", "")).strip(),
            "anahtar": str(k.get("anahtar", "")).strip(),
            "mevzuat": str(k.get("mevzuat", "")).strip(),
            "guven": str(k.get("guven", "")).strip(),
        })

    return {
        "karar_no": karar_no,
        "kartlar": normalized_cards
    }


def call_openai(client, karar_no, dosya_adi, karar_metni):
    system_msg, user_msg = build_prompt(karar_no, dosya_adi, karar_metni)

    # Chat Completions API, OpenAI Python SDK tarafından desteklenen standart kullanımdır.
    # Resmi API referansı Chat Completions oluşturma uç noktasını içerir. 
    # Kaynak: platform.openai.com docs.
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.1,
    )

    raw = resp.choices[0].message.content

    usage = {}
    try:
        usage = {
            "prompt_tokens": getattr(resp.usage, "prompt_tokens", None),
            "completion_tokens": getattr(resp.usage, "completion_tokens", None),
            "total_tokens": getattr(resp.usage, "total_tokens", None),
        }
    except Exception:
        usage = {}

    parsed = parse_json_response(raw)
    normalized = normalize_result(parsed, karar_no)

    return raw, normalized, usage


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 80)
    print("158 - 128 PRODUCTION JSONL RUNNER")
    print("=" * 80)

    run_tag = tag()
    limit = get_limit()

    input_path = latest_file(INPUT_PATTERN)
    if not input_path:
        raise FileNotFoundError("155C1 input JSONL bulunamadı.")

    api_key = load_api_key()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY bulunamadı. .env içine OPENAI_API_KEY=... ekle.")

    if OpenAI is None:
        raise RuntimeError("openai paketi yüklü değil. Komut: pip install openai")

    client = OpenAI(api_key=api_key)

    rows_all = read_jsonl(input_path)
    rows_clean = [r for r in rows_all if "_json_error" not in r]
    rows = rows_clean[:limit]

    output_jsonl = os.path.join(URETIM_OUTPUT_DIR, f"158_128_production_output_{run_tag}.jsonl")
    error_jsonl = os.path.join(URETIM_OUTPUT_DIR, f"158_128_production_errors_{run_tag}.jsonl")
    raw_dir = os.path.join(URETIM_OUTPUT_DIR, f"158_raw_{run_tag}")
    os.makedirs(raw_dir, exist_ok=True)

    log_path = os.path.join(LOG_DIR, f"158_128_production_runner_log_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"158_128_production_runner_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"158_128_production_jsonl_runner_raporu_{run_tag}.txt")

    started = time.time()
    ok_count = 0
    err_count = 0
    total_cards = 0
    total_tokens = 0

    print(f"\nInput JSONL : {input_path}")
    print(f"Limit       : {limit}")
    print(f"Model       : {MODEL}")
    print(f"DB yaz      : {DB_YAZ}")
    print("-" * 80)

    for idx, r in enumerate(rows, start=1):
        karar_no = str(r.get("karar_no", "")).strip()
        dosya_yolu = str(r.get("pdf_yolu") or r.get("dosya_yolu") or "").strip()
        dosya_adi = str(r.get("dosya_adi") or os.path.basename(dosya_yolu)).strip()

        log_base = {
            "run_id": run_tag,
            "time": now(),
            "index": idx,
            "karar_no": karar_no,
            "dosya_adi": dosya_adi,
            "dosya_yolu": dosya_yolu,
            "db_written": False,
        }

        print(f"[{idx}/{len(rows)}] İşleniyor: {karar_no} | {dosya_adi}")

        try:
            if not karar_no:
                raise RuntimeError("Karar no boş.")

            if not dosya_yolu or not os.path.exists(dosya_yolu):
                raise RuntimeError(f"Dosya bulunamadı: {dosya_yolu}")

            metin = extract_text(dosya_yolu)
            metin = clean_text(metin)

            if len(metin) < 200:
                raise RuntimeError(f"PDF/TXT metni çok kısa veya okunamadı. Uzunluk: {len(metin)}")

            metin_kisa = truncate_text(metin)

            raw, normalized, usage = call_openai(client, karar_no, dosya_adi, metin_kisa)

            raw_path = os.path.join(raw_dir, f"{idx:04d}_{re.sub(r'[^0-9A-Za-z_.-]+', '_', karar_no)}.txt")
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(raw or "")

            kart_sayisi = len(normalized.get("kartlar", []))
            total_cards += kart_sayisi

            try:
                if usage.get("total_tokens"):
                    total_tokens += int(usage["total_tokens"])
            except Exception:
                pass

            out_row = {
                "run_id": run_tag,
                "source": "158_128_PRODUCTION_JSONL_RUNNER",
                "status": "OK",
                "index": idx,
                "karar_no": normalized.get("karar_no", karar_no),
                "orijinal_karar_no": karar_no,
                "dosya_adi": dosya_adi,
                "dosya_yolu": dosya_yolu,
                "kart_sayisi": kart_sayisi,
                "kartlar": normalized.get("kartlar", []),
                "usage": usage,
                "raw_response_path": raw_path,
                "db_written": False,
                "created_at": now(),
            }

            append_jsonl(output_jsonl, out_row)
            append_jsonl(log_path, {**log_base, "status": "OK", "kart_sayisi": kart_sayisi, "usage": usage})

            ok_count += 1
            print(f"OK | Kart: {kart_sayisi} | Token: {usage.get('total_tokens')}")

        except Exception as e:
            err_count += 1
            err_row = {
                "run_id": run_tag,
                "source": "158_128_PRODUCTION_JSONL_RUNNER",
                "status": "ERROR",
                "index": idx,
                "karar_no": karar_no,
                "dosya_adi": dosya_adi,
                "dosya_yolu": dosya_yolu,
                "error": str(e),
                "traceback": traceback.format_exc(),
                "db_written": False,
                "created_at": now(),
            }

            append_jsonl(error_jsonl, err_row)
            append_jsonl(log_path, {**log_base, "status": "ERROR", "error": str(e)})

            print(f"HATA | {str(e)}")

        time.sleep(SLEEP_SECONDS)

    elapsed = round(time.time() - started, 2)

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_path": input_path,
        "limit": limit,
        "model": MODEL,
        "db_written": False,
        "processed": len(rows),
        "ok_count": ok_count,
        "error_count": err_count,
        "total_cards": total_cards,
        "total_tokens": total_tokens,
        "elapsed_seconds": elapsed,
        "output_jsonl": output_jsonl,
        "error_jsonl": error_jsonl,
        "log_path": log_path,
        "ready_for_next_step": ok_count > 0 and err_count == 0,
        "next_step": "159_Production_Output_Kalite_On_Kontrol.py",
    }

    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("158 - 128 PRODUCTION JSONL RUNNER RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input JSONL         : {input_path}\n")
        f.write(f"Model               : {MODEL}\n")
        f.write(f"Limit               : {limit}\n")
        f.write(f"DB yaz              : {DB_YAZ}\n\n")

        f.write("ÖZET\n")
        f.write("-" * 80 + "\n")
        f.write(f"İşlenen             : {len(rows)}\n")
        f.write(f"Başarılı            : {ok_count}\n")
        f.write(f"Hatalı              : {err_count}\n")
        f.write(f"Toplam kart         : {total_cards}\n")
        f.write(f"Toplam token        : {total_tokens}\n")
        f.write(f"Süre saniye         : {elapsed}\n")
        f.write(f"Sonraki adıma hazır : {'EVET' if state['ready_for_next_step'] else 'HAYIR'}\n\n")

        f.write("DOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Output JSONL        : {output_jsonl}\n")
        f.write(f"Error JSONL         : {error_jsonl}\n")
        f.write(f"Raw klasör          : {raw_dir}\n")
        f.write(f"Log JSONL           : {log_path}\n")
        f.write(f"State JSON          : {state_path}\n")
        f.write(f"Rapor               : {rapor_path}\n")

    print("\n158 RUNNER TAMAMLANDI")
    print("-" * 80)
    print(f"İşlenen             : {len(rows)}")
    print(f"Başarılı            : {ok_count}")
    print(f"Hatalı              : {err_count}")
    print(f"Toplam kart         : {total_cards}")
    print(f"Toplam token        : {total_tokens}")
    print(f"Sonraki adıma hazır : {'EVET' if state['ready_for_next_step'] else 'HAYIR'}")

    print("\nDosyalar:")
    print(output_jsonl)
    print(error_jsonl)
    print(log_path)
    print(state_path)
    print(rapor_path)

    print("\nNOT: DB'ye yazılmadı.")


if __name__ == "__main__":
    main()