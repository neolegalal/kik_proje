# -*- coding: utf-8 -*-
"""
154 - PİLOT BATCH AI ÜRETİM HAZIRLIK MOTORU

Amaç:
- En güncel 152 master iş planını bulur.
- Seçilen batch'i pilot üretim için hazırlar.
- PDF/TXT dosya yollarını kontrol eder.
- Pilot üretim JSONL dosyası oluşturur.
- DB'ye yazmaz.
- OpenAI çağrısı yapmaz.

Kullanım:
1) Varsayılan olarak batch 1:
   python ".py\\154_Pilot_Batch_AI_Uretim_Hazirlik.py"

2) Belirli batch:
   python ".py\\154_Pilot_Batch_AI_Uretim_Hazirlik.py" 2
"""

import os
import sys
import glob
import json
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
BATCH_DIR = os.path.join(BASE_DIR, "batch_planlari")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
PILOT_DIR = os.path.join(BASE_DIR, "pilot_uretim")

MASTER_PATTERN = os.path.join(BATCH_DIR, "152_master_is_plani_*.jsonl")

DEFAULT_BATCH_NO = 1

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(PILOT_DIR, exist_ok=True)


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


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def get_target_batch_no():
    if len(sys.argv) >= 2:
        try:
            return int(sys.argv[1])
        except Exception:
            raise ValueError("Batch no sayı olmalıdır. Örnek: python ... 1")
    return DEFAULT_BATCH_NO


def main():
    print("=" * 80)
    print("154 - PİLOT BATCH AI ÜRETİM HAZIRLIK MOTORU")
    print("=" * 80)

    run_tag = tag()
    target_batch_no = get_target_batch_no()

    master_path = latest_file(MASTER_PATTERN)
    if not master_path:
        raise FileNotFoundError("152 master iş planı bulunamadı.")

    master_rows = read_jsonl(master_path)
    if not master_rows:
        raise RuntimeError("Master plan boş görünüyor.")

    master_errors = [r for r in master_rows if "_json_error" in r]
    if master_errors:
        raise RuntimeError(f"Master planda JSON hatası var. Hata sayısı: {len(master_errors)}")

    target = None
    for r in master_rows:
        if int(r.get("batch_no", -1)) == target_batch_no:
            target = r
            break

    if not target:
        raise RuntimeError(f"Master plan içinde batch bulunamadı: {target_batch_no}")

    batch_path = target.get("batch_dosyasi")
    if not batch_path or not os.path.exists(batch_path):
        raise FileNotFoundError(f"Batch dosyası bulunamadı: {batch_path}")

    batch_rows = read_jsonl(batch_path)
    batch_errors = [r for r in batch_rows if "_json_error" in r]
    temiz_rows = [r for r in batch_rows if "_json_error" not in r]

    pdf_var = []
    pdf_yok = []
    karar_no_yok = []
    karar_no_set = set()
    mukerrer_karar = []

    pilot_rows = []

    for idx, r in enumerate(temiz_rows, start=1):
        karar_no = str(r.get("karar_no", "")).strip()
        dosya_yolu = str(r.get("dosya_yolu", "")).strip()
        dosya_adi = str(r.get("dosya_adi", "")).strip()

        if not karar_no:
            karar_no_yok.append(r)

        if karar_no:
            k = karar_no.upper()
            if k in karar_no_set:
                mukerrer_karar.append(r)
            karar_no_set.add(k)

        if dosya_yolu and os.path.exists(dosya_yolu):
            pdf_var.append(r)
            dosya_durum = "DOSYA_VAR"
        else:
            pdf_yok.append(r)
            dosya_durum = "DOSYA_YOK"

        pilot_rows.append({
            "pilot_run_id": run_tag,
            "batch_no": target_batch_no,
            "pilot_sira": idx,
            "karar_no": karar_no,
            "dosya_adi": dosya_adi,
            "dosya_yolu": dosya_yolu,
            "dosya_durum": dosya_durum,
            "uzanti": r.get("uzanti", ""),
            "boyut": r.get("boyut", 0),
            "modified": r.get("modified", ""),
            "durum": "AI_URETIME_HAZIR" if dosya_durum == "DOSYA_VAR" and karar_no else "KONTROL_GEREKLI",
            "kaynak_batch_dosyasi": batch_path,
            "kaynak": "154_PILOT_BATCH_AI_URETIM_HAZIRLIK"
        })

    uretime_hazir = (
        len(batch_errors) == 0
        and len(pdf_yok) == 0
        and len(karar_no_yok) == 0
        and len(mukerrer_karar) == 0
        and len(pilot_rows) > 0
    )

    pilot_jsonl = os.path.join(PILOT_DIR, f"154_pilot_batch_{target_batch_no:04d}_{run_tag}.jsonl")
    kontrol_jsonl = os.path.join(PILOT_DIR, f"154_pilot_batch_{target_batch_no:04d}_kontrol_{run_tag}.jsonl")
    rapor_path = os.path.join(RAPOR_DIR, f"154_pilot_batch_ai_uretim_hazirlik_raporu_{run_tag}.txt")

    write_jsonl(pilot_jsonl, pilot_rows)

    kontrol_rows = []
    for r in batch_errors:
        kontrol_rows.append({"risk": "JSON_HATASI", "kayit": r})
    for r in pdf_yok:
        kontrol_rows.append({"risk": "DOSYA_YOK", "kayit": r})
    for r in karar_no_yok:
        kontrol_rows.append({"risk": "KARAR_NO_YOK", "kayit": r})
    for r in mukerrer_karar:
        kontrol_rows.append({"risk": "MUKERRER_KARAR_NO", "kayit": r})

    write_jsonl(kontrol_jsonl, kontrol_rows)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("154 - PİLOT BATCH AI ÜRETİM HAZIRLIK RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                 : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Master plan            : {master_path}\n")
        f.write(f"Batch no               : {target_batch_no}\n")
        f.write(f"Batch dosyası          : {batch_path}\n")
        f.write(f"Beklenen kayıt         : {target.get('kayit_sayisi')}\n")
        f.write(f"Fiili kayıt            : {len(temiz_rows)}\n\n")

        f.write("KONTROL ÖZETİ\n")
        f.write("-" * 80 + "\n")
        f.write(f"JSON hatası            : {len(batch_errors)}\n")
        f.write(f"Dosya var              : {len(pdf_var)}\n")
        f.write(f"Dosya yok              : {len(pdf_yok)}\n")
        f.write(f"Karar no yok           : {len(karar_no_yok)}\n")
        f.write(f"Mükerrer karar no      : {len(mukerrer_karar)}\n")
        f.write(f"Üretime hazır          : {'EVET' if uretime_hazir else 'HAYIR'}\n\n")

        f.write("DOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Pilot JSONL            : {pilot_jsonl}\n")
        f.write(f"Kontrol JSONL          : {kontrol_jsonl}\n")
        f.write(f"Rapor                  : {rapor_path}\n\n")

        if kontrol_rows:
            f.write("RİSK DETAYLARI İLK 100\n")
            f.write("-" * 80 + "\n")
            for x in kontrol_rows[:100]:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")

    print("\nPİLOT BATCH HAZIRLIK TAMAMLANDI")
    print("-" * 80)
    print(f"Batch no          : {target_batch_no}")
    print(f"Fiili kayıt       : {len(temiz_rows)}")
    print(f"JSON hatası       : {len(batch_errors)}")
    print(f"Dosya var         : {len(pdf_var)}")
    print(f"Dosya yok         : {len(pdf_yok)}")
    print(f"Karar no yok      : {len(karar_no_yok)}")
    print(f"Mükerrer karar no : {len(mukerrer_karar)}")
    print(f"Üretime hazır     : {'EVET' if uretime_hazir else 'HAYIR'}")

    print("\nDosyalar:")
    print(pilot_jsonl)
    print(kontrol_jsonl)
    print(rapor_path)

    print("\nNOT: DB'ye yazılmadı. OpenAI çağrısı yapılmadı.")


if __name__ == "__main__":
    main()