# -*- coding: utf-8 -*-
import os, re, json, glob
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
EXPORT_DIR = os.path.join(BASE_DIR, "export")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

WEB_PATTERN = os.path.join(EXPORT_DIR, "151_web_aktif_kartlar_*.jsonl")

def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest_file(pattern):
    files = glob.glob(pattern)
    return max(files, key=os.path.getmtime) if files else None

def read_jsonl(path):
    rows, errors = [], []
    with open(path, "r", encoding="utf-8") as f:
        for no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                errors.append({"line": no, "error": str(e), "raw": line[:300]})
    return rows, errors

def txt(x):
    return str(x or "").strip()

def norm(x):
    return re.sub(r"\s+", " ", txt(x).lower())

def first_existing(row, names):
    for n in names:
        if n in row and txt(row.get(n)):
            return txt(row.get(n))
    return ""

def score_len(value, min_len, good_len):
    l = len(txt(value))
    if l >= good_len:
        return 100
    if l >= min_len:
        return 70
    if l > 0:
        return 35
    return 0

def web_card_score(row):
    karar_no = first_existing(row, ["karar_no", "karar"])
    baslik = first_existing(row, ["baslik", "başlık", "hukuki_baslik"])
    hukuki_soru = first_existing(row, ["hukuki_soru", "soru", "karar_sorusu"])
    konu_ozeti = first_existing(row, ["konu_ozeti", "konu_özeti", "karar_ozeti", "karar_özeti", "ozet", "özet"])
    sonuc_ozeti = first_existing(row, ["sonuc_ozeti", "sonuç_özeti", "sonuc", "sonuç"])
    sonuc_tipi = first_existing(row, ["sonuc_tipi", "sonuç_tipi"])
    emsal = first_existing(row, ["emsal_ilke", "emsal", "ilke"])
    mevzuat = first_existing(row, ["mevzuat", "dayanak", "yasal_dayanak"])
    anahtar = first_existing(row, ["anahtar", "anahtar_kelimeler", "etiketler", "keywords"])

    warnings = []
    block = []

    if not karar_no: block.append("KARAR_NO_YOK")
    if not baslik: block.append("BASLIK_YOK")
    if not hukuki_soru: block.append("HUKUKI_SORU_YOK")
    if not konu_ozeti: block.append("KONU_OZETI_YOK")
    if not sonuc_ozeti: block.append("SONUC_OZETI_YOK")

    if baslik and len(baslik) < 12: warnings.append("BASLIK_KISA")
    if hukuki_soru and "?" not in hukuki_soru: warnings.append("HUKUKI_SORU_SORU_ISARETI_YOK")
    if konu_ozeti and len(konu_ozeti) < 40: warnings.append("KONU_OZETI_KISA")
    if sonuc_ozeti and len(sonuc_ozeti) < 35: warnings.append("SONUC_OZETI_KISA")
    if not sonuc_tipi: warnings.append("SONUC_TIPI_YOK")
    if not emsal: warnings.append("EMSAL_ILKE_YOK")
    if not mevzuat: warnings.append("MEVZUAT_YOK")
    if not anahtar: warnings.append("ANAHTAR_YOK")

    if konu_ozeti and sonuc_ozeti and norm(konu_ozeti) == norm(sonuc_ozeti):
        warnings.append("KONU_SONUC_OZETI_AYNI")

    field_scores = {
        "karar_no": 100 if karar_no else 0,
        "baslik": score_len(baslik, 12, 35),
        "hukuki_soru": score_len(hukuki_soru, 25, 70),
        "konu_ozeti": score_len(konu_ozeti, 40, 120),
        "sonuc_ozeti": score_len(sonuc_ozeti, 35, 100),
        "sonuc_tipi": 100 if sonuc_tipi else 40,
        "emsal": score_len(emsal, 30, 120),
        "mevzuat": 100 if mevzuat else 60,
        "anahtar": 100 if anahtar else 60,
    }

    score = round(sum(field_scores.values()) / len(field_scores), 2)

    if block:
        level = "BLOCK"
        web_ready = False
    elif score >= 85:
        level = "WEB_READY"
        web_ready = True
    elif score >= 70:
        level = "WEB_WARNING"
        web_ready = True
    else:
        level = "WEB_WEAK"
        web_ready = False

    return {
        "karar_no": karar_no,
        "baslik": baslik,
        "score": score,
        "level": level,
        "web_ready": web_ready,
        "block": block,
        "warnings": warnings,
        "field_scores": field_scores,
    }

def main():
    print("=" * 80)
    print("165 - HEDEF 1 WEB KALİTE TEST MOTORU")
    print("=" * 80)

    t = tag()
    web_path = latest_file(WEB_PATTERN)
    if not web_path:
        raise FileNotFoundError("Web export JSONL bulunamadı.")

    rows, errors = read_jsonl(web_path)

    results = []
    counts = {}
    warning_counts = {}
    block_counts = {}

    for r in rows:
        res = web_card_score(r)
        results.append(res)
        counts[res["level"]] = counts.get(res["level"], 0) + 1
        for w in res["warnings"]:
            warning_counts[w] = warning_counts.get(w, 0) + 1
        for b in res["block"]:
            block_counts[b] = block_counts.get(b, 0) + 1

    total = len(results)
    ready = sum(1 for r in results if r["web_ready"])
    blocked = sum(1 for r in results if r["level"] == "BLOCK")
    weak = sum(1 for r in results if r["level"] == "WEB_WEAK")
    avg_score = round(sum(r["score"] for r in results) / total, 2) if total else 0

    certificate = total > 0 and blocked == 0 and avg_score >= 75 and ready / total >= 0.90

    state = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "web_path": web_path,
        "total_cards": total,
        "json_errors": len(errors),
        "web_ready": ready,
        "blocked": blocked,
        "weak": weak,
        "avg_score": avg_score,
        "certificate": certificate,
        "counts": counts,
        "warning_counts": warning_counts,
        "block_counts": block_counts,
    }

    state_path = os.path.join(STATE_DIR, f"165_hedef1_web_kalite_state_{t}.json")
    detay_path = os.path.join(RAPOR_DIR, f"165_hedef1_web_kalite_detay_{t}.jsonl")
    rapor_path = os.path.join(RAPOR_DIR, f"165_hedef1_web_kalite_raporu_{t}.txt")

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(detay_path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("165 - HEDEF 1 WEB KALİTE TEST RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Web JSONL           : {web_path}\n\n")

        f.write("ÖZET\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam kart         : {total}\n")
        f.write(f"JSON hatası         : {len(errors)}\n")
        f.write(f"WEB Ready           : {ready}\n")
        f.write(f"BLOCK               : {blocked}\n")
        f.write(f"WEB Weak            : {weak}\n")
        f.write(f"Ortalama WEB puanı  : {avg_score} / 100\n")
        f.write(f"Sertifika           : {'GEÇTİ' if certificate else 'KALDI'}\n\n")

        f.write("SEVİYE DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        for k, v in sorted(counts.items()):
            f.write(f"{k:25}: {v}\n")

        f.write("\nBLOCK DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        if block_counts:
            for k, v in sorted(block_counts.items()):
                f.write(f"{k:35}: {v}\n")
        else:
            f.write("BLOCK yok.\n")

        f.write("\nWARNING DAĞILIMI\n")
        f.write("-" * 80 + "\n")
        if warning_counts:
            for k, v in sorted(warning_counts.items(), key=lambda x: -x[1]):
                f.write(f"{k:35}: {v}\n")
        else:
            f.write("Warning yok.\n")

        f.write("\nEN ZAYIF 50 KART\n")
        f.write("-" * 80 + "\n")
        for r in sorted(results, key=lambda x: x["score"])[:50]:
            f.write(f"{r['score']:6} | {r['level']:12} | {r['karar_no']} | {r['baslik']}\n")

        f.write("\nHEDEF 1 SONUÇ\n")
        f.write("-" * 80 + "\n")
        if certificate:
            f.write("✓ Hedef 1 WEB için veri seti teknik ve içerik alanları bakımından kullanılabilir görünmektedir.\n")
        else:
            f.write("✗ Hedef 1 WEB için iyileştirme gerektiren alanlar bulunmaktadır.\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"State JSON          : {state_path}\n")
        f.write(f"Detay JSONL         : {detay_path}\n")
        f.write(f"Rapor               : {rapor_path}\n")

    print("\n165 HEDEF 1 WEB KALİTE TESTİ TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam kart        : {total}")
    print(f"WEB Ready          : {ready}")
    print(f"BLOCK              : {blocked}")
    print(f"WEB Weak           : {weak}")
    print(f"Ortalama puan      : {avg_score} / 100")
    print(f"Sertifika          : {'GEÇTİ' if certificate else 'KALDI'}")
    print("\nDosya:")
    print(rapor_path)

if __name__ == "__main__":
    main()