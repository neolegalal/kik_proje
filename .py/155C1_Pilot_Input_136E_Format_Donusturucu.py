# -*- coding: utf-8 -*-
import os
import glob
import json
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PILOT_DIR = os.path.join(BASE_DIR, "pilot_uretim")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
URETIM_INPUT_DIR = os.path.join(BASE_DIR, "uretim_input")

PILOT_PATTERN = os.path.join(PILOT_DIR, "154_pilot_batch_*.jsonl")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(URETIM_INPUT_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


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
                rows.append({
                    "_json_error": str(e),
                    "_line_no": line_no,
                    "_raw": line[:500],
                })
    return rows


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():
    print("=" * 80)
    print("155C1 - PILOT INPUT 136E FORMAT DÖNÜŞTÜRÜCÜ")
    print("=" * 80)

    t = tag()

    pilot_path = latest_file(PILOT_PATTERN)
    if not pilot_path:
        raise FileNotFoundError("154 pilot JSONL bulunamadı.")

    pilot_rows = read_jsonl(pilot_path)

    converted = []
    errors = []

    for idx, r in enumerate(pilot_rows, start=1):
        if "_json_error" in r:
            errors.append({
                "sira": idx,
                "risk": "JSON_HATASI",
                "kayit": r,
            })
            continue

        karar_no = str(r.get("karar_no", "")).strip()
        dosya_yolu = str(r.get("dosya_yolu", "")).strip()
        dosya_adi = str(r.get("dosya_adi", "")).strip()

        if not karar_no:
            errors.append({
                "sira": idx,
                "risk": "KARAR_NO_YOK",
                "kayit": r,
            })
            continue

        if not dosya_yolu or not os.path.exists(dosya_yolu):
            errors.append({
                "sira": idx,
                "risk": "DOSYA_YOK",
                "kayit": r,
            })
            continue

        converted.append({
            "sira": len(converted) + 1,
            "karar_no": karar_no,
            "pdf_yolu": dosya_yolu,
            "dosya_yolu": dosya_yolu,
            "dosya_adi": dosya_adi,
            "batch_no": r.get("batch_no"),
            "pilot_sira": r.get("pilot_sira"),
            "kaynak": "155C1_PILOT_TO_136E_INPUT",
            "durum": "136E_HAZIR"
        })

    out_jsonl = os.path.join(URETIM_INPUT_DIR, f"155C1_136E_pilot_input_{t}.jsonl")
    err_jsonl = os.path.join(URETIM_INPUT_DIR, f"155C1_136E_pilot_input_hatalar_{t}.jsonl")
    rapor_path = os.path.join(RAPOR_DIR, f"155C1_pilot_input_136E_format_raporu_{t}.txt")

    write_jsonl(out_jsonl, converted)
    write_jsonl(err_jsonl, errors)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("155C1 - PILOT INPUT 136E FORMAT DÖNÜŞTÜRÜCÜ RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih             : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Pilot JSONL        : {pilot_path}\n")
        f.write(f"Okunan kayıt       : {len(pilot_rows)}\n")
        f.write(f"Dönüştürülen       : {len(converted)}\n")
        f.write(f"Hatalı kayıt       : {len(errors)}\n")
        f.write(f"136E input JSONL   : {out_jsonl}\n")
        f.write(f"Hata JSONL         : {err_jsonl}\n")
        f.write(f"Üretime hazır      : {'EVET' if len(converted) > 0 and len(errors) == 0 else 'HAYIR'}\n\n")

        if errors:
            f.write("HATALAR İLK 50\n")
            f.write("-" * 80 + "\n")
            for e in errors[:50]:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")

    print("\nDÖNÜŞTÜRME TAMAMLANDI")
    print("-" * 80)
    print(f"Okunan kayıt     : {len(pilot_rows)}")
    print(f"Dönüştürülen     : {len(converted)}")
    print(f"Hatalı kayıt     : {len(errors)}")
    print(f"Üretime hazır    : {'EVET' if len(converted) > 0 and len(errors) == 0 else 'HAYIR'}")

    print("\nDosyalar:")
    print(out_jsonl)
    print(err_jsonl)
    print(rapor_path)

    print("\nNOT: OpenAI çağrısı yapılmadı. DB'ye yazılmadı.")


if __name__ == "__main__":
    main()