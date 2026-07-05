# -*- coding: utf-8 -*-
import os
import json
import glob
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
BATCH_DIR = os.path.join(BASE_DIR, "batch_planlari")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

MASTER_PATTERN = os.path.join(BATCH_DIR, "152_master_is_plani_*.jsonl")
NO_KARAR_PATTERN = os.path.join(BATCH_DIR, "152_karar_no_bulunamayan_*.jsonl")
DBDE_PATTERN = os.path.join(BATCH_DIR, "152_dbde_olan_atlanan_*.jsonl")

os.makedirs(RAPOR_DIR, exist_ok=True)


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
                    "_raw": line[:300]
                })
    return rows


def main():
    print("=" * 80)
    print("153 - BATCH PLAN KONTROL RAPORU")
    print("=" * 80)

    t = tag()

    master_path = latest_file(MASTER_PATTERN)
    no_karar_path = latest_file(NO_KARAR_PATTERN)
    dbde_path = latest_file(DBDE_PATTERN)

    if not master_path:
        raise FileNotFoundError("152 master iş planı bulunamadı.")

    master_rows = read_jsonl(master_path)
    no_karar_rows = read_jsonl(no_karar_path)
    dbde_rows = read_jsonl(dbde_path)

    toplam_batch = len(master_rows)
    toplam_kayit = 0
    eksik_batch = []
    hatali_json = []
    batch_detay = []
    karar_set = set()
    mukerrer_karar = []

    for m in master_rows:
        batch_no = m.get("batch_no")
        batch_path = m.get("batch_dosyasi")
        beklenen = int(m.get("kayit_sayisi") or 0)

        if not batch_path or not os.path.exists(batch_path):
            eksik_batch.append({
                "batch_no": batch_no,
                "batch_dosyasi": batch_path,
                "neden": "Batch dosyası bulunamadı"
            })
            continue

        rows = read_jsonl(batch_path)
        json_error_count = sum(1 for r in rows if "_json_error" in r)
        if json_error_count:
            hatali_json.append({
                "batch_no": batch_no,
                "batch_dosyasi": batch_path,
                "json_hata": json_error_count
            })

        temiz_rows = [r for r in rows if "_json_error" not in r]
        fiili = len(temiz_rows)
        toplam_kayit += fiili

        durum = "OK"
        if beklenen != fiili:
            durum = "SAYI_UYUSMAZLIGI"

        for r in temiz_rows:
            k = str(r.get("karar_no", "")).strip().upper()
            if not k:
                continue
            if k in karar_set:
                mukerrer_karar.append({
                    "karar_no": k,
                    "batch_no": batch_no,
                    "batch_dosyasi": batch_path
                })
            karar_set.add(k)

        batch_detay.append({
            "batch_no": batch_no,
            "beklenen": beklenen,
            "fiili": fiili,
            "durum": durum,
            "batch_dosyasi": batch_path
        })

    risk_var = bool(eksik_batch or hatali_json or mukerrer_karar)
    uretime_baslanabilir = not risk_var and toplam_kayit > 0

    rapor_path = os.path.join(RAPOR_DIR, f"153_batch_plan_kontrol_raporu_{t}.txt")
    ozet_jsonl = os.path.join(RAPOR_DIR, f"153_batch_plan_kontrol_ozet_{t}.jsonl")

    with open(ozet_jsonl, "w", encoding="utf-8") as f:
        for d in batch_detay:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("153 - BATCH PLAN KONTROL RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                  : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Master plan             : {master_path}\n")
        f.write(f"Karar no bulunamayan    : {no_karar_path}\n")
        f.write(f"DB'de olan atlanan      : {dbde_path}\n\n")

        f.write("ÖZET\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam batch            : {toplam_batch}\n")
        f.write(f"Toplam işlenecek kayıt  : {toplam_kayit}\n")
        f.write(f"Tekil karar no          : {len(karar_set)}\n")
        f.write(f"Karar no bulunamayan    : {len(no_karar_rows)}\n")
        f.write(f"DB'de olan atlanan      : {len(dbde_rows)}\n")
        f.write(f"Eksik batch             : {len(eksik_batch)}\n")
        f.write(f"JSON hatalı batch       : {len(hatali_json)}\n")
        f.write(f"Plan içi mükerrer karar : {len(mukerrer_karar)}\n")
        f.write(f"Üretime başlanabilir    : {'EVET' if uretime_baslanabilir else 'HAYIR'}\n\n")

        f.write("BATCH DETAYLARI\n")
        f.write("-" * 80 + "\n")
        for d in batch_detay:
            f.write(
                f"Batch {d['batch_no']:>4} | "
                f"Beklenen: {d['beklenen']:>4} | "
                f"Fiili: {d['fiili']:>4} | "
                f"{d['durum']} | {d['batch_dosyasi']}\n"
            )

        if eksik_batch:
            f.write("\nEKSİK BATCH DOSYALARI\n")
            f.write("-" * 80 + "\n")
            for x in eksik_batch[:100]:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")

        if hatali_json:
            f.write("\nJSON HATALARI\n")
            f.write("-" * 80 + "\n")
            for x in hatali_json[:100]:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")

        if mukerrer_karar:
            f.write("\nPLAN İÇİ MÜKERRER KARARLAR İLK 100\n")
            f.write("-" * 80 + "\n")
            for x in mukerrer_karar[:100]:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")

        if no_karar_rows:
            f.write("\nKARAR NO BULUNAMAYAN DOSYALAR\n")
            f.write("-" * 80 + "\n")
            for x in no_karar_rows[:200]:
                f.write(f"{x.get('dosya_adi','')} | {x.get('dosya_yolu','')}\n")

    print("\nBATCH PLAN KONTROLÜ TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam batch            : {toplam_batch}")
    print(f"Toplam işlenecek kayıt  : {toplam_kayit}")
    print(f"Tekil karar no          : {len(karar_set)}")
    print(f"Karar no bulunamayan    : {len(no_karar_rows)}")
    print(f"Eksik batch             : {len(eksik_batch)}")
    print(f"JSON hatalı batch       : {len(hatali_json)}")
    print(f"Plan içi mükerrer karar : {len(mukerrer_karar)}")
    print(f"Üretime başlanabilir    : {'EVET' if uretime_baslanabilir else 'HAYIR'}")

    print("\nDosyalar:")
    print(rapor_path)
    print(ozet_jsonl)


if __name__ == "__main__":
    main()