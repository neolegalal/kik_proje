# -*- coding: utf-8 -*-
"""
155C2 - 136E INPUT UYUM KONTROL MOTORU

Amaç:
- En güncel 155C1 136E pilot input JSONL dosyasını bulur.
- 136E motor dosyasının varlığını kontrol eder.
- Input kayıtlarında 136E için gerekli alanları kontrol eder.
- Dosya yolları, karar no, uzantı ve tekrarları denetler.
- OpenAI çağrısı yapmaz.
- DB'ye yazmaz.
"""

import os
import re
import glob
import json
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
URETIM_INPUT_DIR = os.path.join(BASE_DIR, "uretim_input")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

INPUT_PATTERN = os.path.join(URETIM_INPUT_DIR, "155C1_136E_pilot_input_*.jsonl")
SCRIPT_136E = os.path.join(PY_DIR, "136E_Batch_Guvenli_Sadeleme_Motoru.py")

REQUIRED_FIELDS = [
    "sira",
    "karar_no",
    "pdf_yolu",
    "dosya_yolu",
    "dosya_adi",
    "batch_no",
    "pilot_sira",
    "durum",
]

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def latest_file(pattern):
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getmtime)


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


def karar_no_format_ok(karar_no):
    k = str(karar_no or "").strip().upper()

    if not k:
        return False

    # Normal KİK formatı: 2026/UH.I-1234, 2008/UY.Z-382
    if re.match(r"^20\d{2}/[A-ZÇĞİÖŞÜ]{2,}(?:\.[A-ZÇĞİÖŞÜI]+)?-\d+$", k):
        return True

    # Manuel istisna formatları
    if re.match(r"^20\d{2}/ISTISNA-\d+$", k):
        return True

    if re.match(r"^20\d{2}/KIK-YOK-\d+$", k):
        return True

    return False


def main():
    print("=" * 80)
    print("155C2 - 136E INPUT UYUM KONTROL MOTORU")
    print("=" * 80)

    t = tag()

    input_path = latest_file(INPUT_PATTERN)
    if not input_path:
        raise FileNotFoundError("155C1 136E pilot input JSONL bulunamadı.")

    rows = read_jsonl(input_path)

    risks = []
    karar_seen = set()
    path_seen = set()

    script_exists = os.path.exists(SCRIPT_136E)
    if not script_exists:
        risks.append({
            "risk": "136E_SCRIPT_YOK",
            "detay": SCRIPT_136E,
        })

    for idx, r in enumerate(rows, start=1):
        if "_json_error" in r:
            risks.append({
                "sira": idx,
                "risk": "JSON_HATASI",
                "kayit": r,
            })
            continue

        for field in REQUIRED_FIELDS:
            if field not in r:
                risks.append({
                    "sira": idx,
                    "risk": "ALAN_EKSIK",
                    "alan": field,
                    "karar_no": r.get("karar_no"),
                })

        karar_no = str(r.get("karar_no", "")).strip().upper()
        pdf_yolu = str(r.get("pdf_yolu", "")).strip()
        dosya_yolu = str(r.get("dosya_yolu", "")).strip()
        durum = str(r.get("durum", "")).strip()

        if not karar_no_format_ok(karar_no):
            risks.append({
                "sira": idx,
                "risk": "KARAR_NO_FORMAT_RISK",
                "karar_no": karar_no,
            })

        if karar_no:
            if karar_no in karar_seen:
                risks.append({
                    "sira": idx,
                    "risk": "MUKERRER_KARAR_NO",
                    "karar_no": karar_no,
                })
            karar_seen.add(karar_no)

        if not pdf_yolu:
            risks.append({
                "sira": idx,
                "risk": "PDF_YOLU_BOS",
                "karar_no": karar_no,
            })
        elif not os.path.exists(pdf_yolu):
            risks.append({
                "sira": idx,
                "risk": "PDF_BULUNAMADI",
                "karar_no": karar_no,
                "pdf_yolu": pdf_yolu,
            })
        else:
            ext = os.path.splitext(pdf_yolu)[1].lower()
            if ext not in [".pdf", ".txt"]:
                risks.append({
                    "sira": idx,
                    "risk": "DESTEKLENMEYEN_UZANTI",
                    "karar_no": karar_no,
                    "uzanti": ext,
                })

        if dosya_yolu and pdf_yolu and os.path.normcase(dosya_yolu) != os.path.normcase(pdf_yolu):
            risks.append({
                "sira": idx,
                "risk": "PDF_YOLU_DOSYA_YOLU_FARKLI",
                "karar_no": karar_no,
                "pdf_yolu": pdf_yolu,
                "dosya_yolu": dosya_yolu,
            })

        if pdf_yolu:
            pkey = os.path.normcase(pdf_yolu)
            if pkey in path_seen:
                risks.append({
                    "sira": idx,
                    "risk": "MUKERRER_DOSYA_YOLU",
                    "karar_no": karar_no,
                    "pdf_yolu": pdf_yolu,
                })
            path_seen.add(pkey)

        if durum != "136E_HAZIR":
            risks.append({
                "sira": idx,
                "risk": "DURUM_UYUMSUZ",
                "karar_no": karar_no,
                "durum": durum,
            })

    ready = len(rows) > 0 and len(risks) == 0

    state = {
        "run_id": t,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_path": input_path,
        "script_136E": SCRIPT_136E,
        "script_136E_exists": script_exists,
        "record_count": len(rows),
        "risk_count": len(risks),
        "ready_for_136E": ready,
        "next_step": "155C3_136E_Pilot_Cagirma_Motoru.py" if ready else "RISKLERI_GIDER",
    }

    state_path = os.path.join(STATE_DIR, f"155C2_136E_input_uyum_state_{t}.json")
    risk_jsonl = os.path.join(RAPOR_DIR, f"155C2_136E_input_uyum_riskler_{t}.jsonl")
    rapor_path = os.path.join(RAPOR_DIR, f"155C2_136E_input_uyum_raporu_{t}.txt")

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(risk_jsonl, "w", encoding="utf-8") as f:
        for r in risks:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("155C2 - 136E INPUT UYUM KONTROL RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Input JSONL         : {input_path}\n")
        f.write(f"136E Script         : {SCRIPT_136E}\n")
        f.write(f"136E Script var     : {'EVET' if script_exists else 'HAYIR'}\n")
        f.write(f"Kayıt sayısı        : {len(rows)}\n")
        f.write(f"Risk sayısı         : {len(risks)}\n")
        f.write(f"136E hazır          : {'EVET' if ready else 'HAYIR'}\n\n")

        f.write("GEREKLİ ALANLAR\n")
        f.write("-" * 80 + "\n")
        for field in REQUIRED_FIELDS:
            f.write(f"- {field}\n")

        if risks:
            f.write("\nRİSKLER İLK 100\n")
            f.write("-" * 80 + "\n")
            for r in risks[:100]:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"State JSON          : {state_path}\n")
        f.write(f"Risk JSONL          : {risk_jsonl}\n")
        f.write(f"Rapor               : {rapor_path}\n")

    print("\n136E INPUT UYUM KONTROLÜ TAMAMLANDI")
    print("-" * 80)
    print(f"Kayıt sayısı    : {len(rows)}")
    print(f"136E script var : {'EVET' if script_exists else 'HAYIR'}")
    print(f"Risk sayısı     : {len(risks)}")
    print(f"136E hazır      : {'EVET' if ready else 'HAYIR'}")

    print("\nDosyalar:")
    print(rapor_path)
    print(risk_jsonl)
    print(state_path)

    print("\nNOT: OpenAI çağrısı yapılmadı. DB'ye yazılmadı.")


if __name__ == "__main__":
    main()