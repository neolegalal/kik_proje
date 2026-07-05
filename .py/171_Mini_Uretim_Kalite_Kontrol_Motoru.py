# -*- coding: utf-8 -*-
"""
171 - MINI URETIM KALITE KONTROL MOTORU

Amaç:
- 168 Production Format Revision Runner çıktısını kontrol eder.
- konu_ozeti, sonuc_ozeti, anahtar, mevzuat ve sonuc alanlarının teknik ve kalite kontrolünü yapar.
- DB'ye yazmadan önce mini üretimin WEB/RAG için uygun olup olmadığını raporlar.

Kullanım:
  python ".py\\171_Mini_Uretim_Kalite_Kontrol_Motoru.py"

Belirli dosya ile:
  python ".py\\171_Mini_Uretim_Kalite_Kontrol_Motoru.py" "C:\\Users\\MSI\\Desktop\\kik_proje\\uretim_output\\168_production_output_YYYYMMDD_HHMMSS.jsonl"

Not:
- Bu script API çağrısı yapmaz.
- DB'ye yazmaz.
- En güncel 168_production_output_*.jsonl dosyasını otomatik bulur.
"""

import os
import re
import sys
import glob
import json
from datetime import datetime
from collections import Counter, defaultdict

# =============================================================================
# AYARLAR
# =============================================================================

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
URETIM_OUTPUT_DIR = os.path.join(BASE_DIR, "uretim_output")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
LOG_DIR = os.path.join(BASE_DIR, "production_logs")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

INPUT_PATTERN = os.path.join(URETIM_OUTPUT_DIR, "168_production_output_*.jsonl")

MIN_KONU_KELIME = 25
MIN_SONUC_KELIME = 15
MIN_ANAHTAR = 5
MAX_ANAHTAR = 12
MIN_MEVZUAT = 1

GECERLI_SONUC_TIPLERI = {
    "KABUL",
    "RET",
    "DÜZELTİCİ İŞLEM",
    "DUZELTICI ISLEM",
    "İPTAL",
    "IPTAL",
    "KARAR VERİLMESİNE YER OLMADIĞI",
    "KARAR VERILMESINE YER OLMADIGI",
    "DİĞER",
    "DIGER",
}

KURUMSAL_AD_IPUCLARI = [
    " ltd", " ltd.", " a.ş", " a.s", " anonim", " limited", " belediyesi",
    " müdürlüğü", " bakanlığı", " valiliği", " üniversitesi", " hastanesi",
    " inşaat", " temizlik", " güvenlik", " yemek", " turizm"
]

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


def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                obj["_line_no"] = line_no
                rows.append(obj)
            except Exception as e:
                rows.append({
                    "_line_no": line_no,
                    "_json_error": str(e),
                    "_raw": line[:500]
                })
    return rows


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def append_jsonl(path, obj):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def as_text(v):
    if v is None:
        return ""
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, list):
        return ", ".join([str(x).strip() for x in v if str(x).strip()])
    return str(v).strip()


def as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return []
        # JSON liste string olarak gelmişse çözmeyi dene
        if s.startswith("[") and s.endswith("]"):
            try:
                arr = json.loads(s)
                if isinstance(arr, list):
                    return [str(x).strip() for x in arr if str(x).strip()]
            except Exception:
                pass
        # Virgül/noktalı virgül ayrımlı metni listeye çevir
        return [x.strip() for x in re.split(r"[,;\n]+", s) if x.strip()]
    return [str(v).strip()] if str(v).strip() else []


def word_count(text):
    text = as_text(text)
    return len(re.findall(r"\b\w+\b", text, flags=re.UNICODE))


def contains_result_language(text):
    t = as_text(text).lower()
    patterns = [
        "karar veril", "düzeltici işlem", "iptal", "redd", "red", "ret",
        "kabul", "yerinde bulun", "yerinde görül", "aykırı", "uygun bulun"
    ]
    return any(p in t for p in patterns)


def konu_sonuc_ayrimi_puani(konu_ozeti, sonuc_ozeti):
    konu = as_text(konu_ozeti)
    sonuc = as_text(sonuc_ozeti)
    if not konu or not sonuc:
        return 0

    puan = 100
    # Konu özetinde sonuç dili varsa ayrım zayıflar.
    if contains_result_language(konu):
        puan -= 25
    # Sonuç özetinde sonuç dili hiç yoksa sonuç zayıf olabilir.
    if not contains_result_language(sonuc):
        puan -= 20

    # Çok benzer metinler ayrım yapılmadığını gösterir.
    konu_words = set(re.findall(r"\w+", konu.lower(), flags=re.UNICODE))
    sonuc_words = set(re.findall(r"\w+", sonuc.lower(), flags=re.UNICODE))
    if konu_words and sonuc_words:
        overlap = len(konu_words & sonuc_words) / max(1, min(len(konu_words), len(sonuc_words)))
        if overlap > 0.75:
            puan -= 25

    return max(0, min(100, puan))


def has_private_names(text):
    t = as_text(text).lower()
    return any(x in t for x in KURUMSAL_AD_IPUCLARI)


def sonuc_tipi_normalize(s):
    s = as_text(s).upper()
    s = s.replace("I", "I").strip()
    return s


def score_card(card):
    issues = []
    warnings = []
    puan = 100

    baslik = as_text(card.get("baslik"))
    hukuki_soru = as_text(card.get("hukuki_soru"))
    konu_ozeti = as_text(card.get("konu_ozeti"))
    sonuc_ozeti = as_text(card.get("sonuc_ozeti"))
    sonuc = as_text(card.get("sonuc"))
    sonuc_tipi = as_text(card.get("sonuc_tipi"))
    emsal_ilke = as_text(card.get("emsal_ilke"))
    anahtar = as_list(card.get("anahtar"))
    mevzuat = as_list(card.get("mevzuat"))
    guven = as_text(card.get("guven"))

    # Zorunlu alanlar
    required_texts = {
        "baslik": baslik,
        "hukuki_soru": hukuki_soru,
        "konu_ozeti": konu_ozeti,
        "sonuc_ozeti": sonuc_ozeti,
        "sonuc": sonuc,
        "sonuc_tipi": sonuc_tipi,
        "emsal_ilke": emsal_ilke,
        "guven": guven,
    }
    for field, value in required_texts.items():
        if not value:
            issues.append(f"{field.upper()}_YOK")
            puan -= 12

    if not anahtar:
        issues.append("ANAHTAR_YOK")
        puan -= 15
    if not mevzuat:
        warnings.append("MEVZUAT_YOK")
        puan -= 5

    # Tip kontrolleri
    if not isinstance(card.get("anahtar"), list):
        issues.append("ANAHTAR_LISTE_DEGIL")
        puan -= 15
    if not isinstance(card.get("mevzuat"), list):
        issues.append("MEVZUAT_LISTE_DEGIL")
        puan -= 10

    # Uzunluk / kalite kontrolleri
    if konu_ozeti and word_count(konu_ozeti) < MIN_KONU_KELIME:
        issues.append("KONU_OZETI_COK_KISA")
        puan -= 10
    if sonuc_ozeti and word_count(sonuc_ozeti) < MIN_SONUC_KELIME:
        issues.append("SONUC_OZETI_COK_KISA")
        puan -= 10

    if hukuki_soru and not hukuki_soru.endswith("?"):
        warnings.append("HUKUKI_SORU_SORU_CUMLESI_DEGIL")
        puan -= 4

    if sonuc_tipi and sonuc_tipi_normalize(sonuc_tipi) not in GECERLI_SONUC_TIPLERI:
        issues.append("SONUC_TIPI_GECERSIZ")
        puan -= 15

    if anahtar:
        if len(anahtar) < MIN_ANAHTAR:
            issues.append("ANAHTAR_AZ")
            puan -= 8
        if len(anahtar) > MAX_ANAHTAR:
            warnings.append("ANAHTAR_COK")
            puan -= 3
        if len(set([a.lower() for a in anahtar])) != len(anahtar):
            warnings.append("ANAHTAR_TEKRAR")
            puan -= 3
        short_keys = [a for a in anahtar if len(a) < 3]
        if short_keys:
            warnings.append("ANAHTAR_ANLAMSIZ_KISA")
            puan -= 3

    # Konu ve sonuç ayrımı
    ayrim_puani = konu_sonuc_ayrimi_puani(konu_ozeti, sonuc_ozeti)
    if ayrim_puani < 60:
        issues.append("KONU_SONUC_AYRIMI_ZAYIF")
        puan -= 12
    elif ayrim_puani < 80:
        warnings.append("KONU_SONUC_AYRIMI_KONTROL")
        puan -= 4

    # Sonuç uyumu
    if sonuc and sonuc_ozeti:
        if sonuc != sonuc_ozeti:
            # Birebir aynı olmak zorunda değil; ama çok kopuksa uyarı.
            s1 = set(re.findall(r"\w+", sonuc.lower(), flags=re.UNICODE))
            s2 = set(re.findall(r"\w+", sonuc_ozeti.lower(), flags=re.UNICODE))
            overlap = len(s1 & s2) / max(1, min(len(s1), len(s2)))
            if overlap < 0.35:
                warnings.append("SONUC_ALANI_SONUC_OZETIYLE_ZAYIF_UYUMLU")
                puan -= 5

    # İsim/sansür kontrolü - özellikle hukuki soru ve başlıkta kurum/şirket adı olmamalı
    if has_private_names(hukuki_soru):
        warnings.append("HUKUKI_SORUDA_KURUM_SIRKET_ADI_OLABILIR")
        puan -= 4
    if has_private_names(baslik):
        warnings.append("BASLIKTA_KURUM_SIRKET_ADI_OLABILIR")
        puan -= 4

    # Emsal ilke sonuç özetiyle aynı olmamalı
    if emsal_ilke and sonuc_ozeti:
        if emsal_ilke.strip().lower() == sonuc_ozeti.strip().lower():
            issues.append("EMSAL_ILKE_SONUC_TEKRARI")
            puan -= 10

    puan = max(0, min(100, puan))

    if issues:
        kalite = "BLOCK"
    elif puan >= 85:
        kalite = "READY"
    elif puan >= 70:
        kalite = "WARNING"
    else:
        kalite = "BLOCK"

    return {
        "puan": puan,
        "kalite": kalite,
        "issues": issues,
        "warnings": warnings,
        "alan_ozet": {
            "baslik_len": len(baslik),
            "hukuki_soru_len": len(hukuki_soru),
            "konu_ozeti_kelime": word_count(konu_ozeti),
            "sonuc_ozeti_kelime": word_count(sonuc_ozeti),
            "anahtar_sayisi": len(anahtar),
            "mevzuat_sayisi": len(mevzuat),
            "konu_sonuc_ayrim_puani": ayrim_puani,
        },
        "normalized_preview": {
            "baslik": baslik,
            "hukuki_soru": hukuki_soru,
            "konu_ozeti": konu_ozeti[:300],
            "sonuc_ozeti": sonuc_ozeti[:300],
            "sonuc_tipi": sonuc_tipi,
            "anahtar": anahtar,
            "mevzuat": mevzuat,
        }
    }


def main():
    print("=" * 80)
    print("171 - MINI URETIM KALITE KONTROL MOTORU")
    print("=" * 80)

    run_tag = tag()

    if len(sys.argv) >= 2:
        input_path = sys.argv[1].strip().strip('"')
    else:
        input_path = latest_file(INPUT_PATTERN)

    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError("168 production output JSONL bulunamadı. Dosya yolunu argüman olarak ver.")

    rows = read_jsonl(input_path)

    detail_jsonl = os.path.join(LOG_DIR, f"171_mini_kalite_detay_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"171_mini_kalite_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"171_mini_uretim_kalite_kontrol_raporu_{run_tag}.txt")

    total_rows = len(rows)
    json_errors = 0
    total_cards = 0
    ready_cards = 0
    warning_cards = 0
    block_cards = 0
    score_sum = 0

    issue_counter = Counter()
    warning_counter = Counter()
    karar_stats = defaultdict(lambda: {"kart": 0, "ready": 0, "warning": 0, "block": 0})
    sample_blocks = []
    sample_warnings = []

    print(f"\nKontrol edilen dosya : {input_path}")
    print("-" * 80)

    for row in rows:
        if "_json_error" in row:
            json_errors += 1
            continue

        karar_no = str(row.get("karar_no") or row.get("orijinal_karar_no") or "").strip()
        kartlar = row.get("kartlar", [])
        if not isinstance(kartlar, list):
            kartlar = []
            issue_counter["KARTLAR_LISTE_DEGIL"] += 1

        for i, card in enumerate(kartlar, start=1):
            total_cards += 1
            result = score_card(card if isinstance(card, dict) else {})
            score_sum += result["puan"]

            kalite = result["kalite"]
            karar_stats[karar_no]["kart"] += 1
            if kalite == "READY":
                ready_cards += 1
                karar_stats[karar_no]["ready"] += 1
            elif kalite == "WARNING":
                warning_cards += 1
                karar_stats[karar_no]["warning"] += 1
            else:
                block_cards += 1
                karar_stats[karar_no]["block"] += 1

            for issue in result["issues"]:
                issue_counter[issue] += 1
            for warning in result["warnings"]:
                warning_counter[warning] += 1

            detail = {
                "run_id": run_tag,
                "created_at": now(),
                "input_path": input_path,
                "karar_no": karar_no,
                "kart_index": i,
                **result
            }
            append_jsonl(detail_jsonl, detail)

            if kalite == "BLOCK" and len(sample_blocks) < 10:
                sample_blocks.append(detail)
            if kalite == "WARNING" and len(sample_warnings) < 10:
                sample_warnings.append(detail)

    avg_score = round(score_sum / total_cards, 2) if total_cards else 0
    ready_ratio = round((ready_cards / total_cards) * 100, 2) if total_cards else 0
    block_ratio = round((block_cards / total_cards) * 100, 2) if total_cards else 0

    production_ready = (
        json_errors == 0
        and total_cards > 0
        and block_cards == 0
        and ready_ratio >= 80
        and avg_score >= 85
    )

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_path": input_path,
        "total_rows": total_rows,
        "json_errors": json_errors,
        "total_cards": total_cards,
        "ready_cards": ready_cards,
        "warning_cards": warning_cards,
        "block_cards": block_cards,
        "average_score": avg_score,
        "ready_ratio": ready_ratio,
        "block_ratio": block_ratio,
        "production_ready": production_ready,
        "issue_counts": dict(issue_counter),
        "warning_counts": dict(warning_counter),
        "detail_jsonl": detail_jsonl,
        "rapor_path": rapor_path,
        "next_step": "169_Production_DB_Importer_Revizyonu.py" if production_ready else "168 prompt/output kalitesi iyilestirilmeli veya bloklar manuel incelenmeli",
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("171 - MINI URETIM KALITE KONTROL RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                  : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Kontrol edilen dosya   : {input_path}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"JSONL satır            : {total_rows}\n")
        f.write(f"JSON hata              : {json_errors}\n")
        f.write(f"Toplam kart            : {total_cards}\n")
        f.write(f"READY kart             : {ready_cards}\n")
        f.write(f"WARNING kart           : {warning_cards}\n")
        f.write(f"BLOCK kart             : {block_cards}\n")
        f.write(f"Ortalama puan          : {avg_score} / 100\n")
        f.write(f"READY oranı            : %{ready_ratio}\n")
        f.write(f"BLOCK oranı            : %{block_ratio}\n")
        f.write(f"169'a geçilebilir mi   : {'EVET' if production_ready else 'HAYIR'}\n\n")

        f.write("ANA KONTROLLER\n")
        f.write("-" * 80 + "\n")
        f.write("- konu_ozeti dolu mu ve yeterli uzunlukta mı?\n")
        f.write("- sonuc_ozeti dolu mu ve Kurul sonucunu anlatıyor mu?\n")
        f.write("- anahtar liste mi, yeterli ve anlamlı mı?\n")
        f.write("- mevzuat liste mi ve en az bir mevzuat ilişkisi var mı?\n")
        f.write("- sonuc alanı sonuc_ozeti ile uyumlu mu?\n")
        f.write("- konu_ozeti ile sonuc_ozeti birbirinden ayrılmış mı?\n")
        f.write("- hukuki_soru soru cümlesi mi ve danışmanlıkta kullanılabilir mi?\n")
        f.write("- emsal_ilke sonuç tekrarından ibaret mi?\n\n")

        f.write("BLOCK SEBEPLERI\n")
        f.write("-" * 80 + "\n")
        if issue_counter:
            for k, v in issue_counter.most_common():
                f.write(f"{k:<45}: {v}\n")
        else:
            f.write("BLOCK sebebi yok.\n")
        f.write("\n")

        f.write("WARNING SEBEPLERI\n")
        f.write("-" * 80 + "\n")
        if warning_counter:
            for k, v in warning_counter.most_common():
                f.write(f"{k:<45}: {v}\n")
        else:
            f.write("Warning yok.\n")
        f.write("\n")

        f.write("KARAR BAZLI OZET\n")
        f.write("-" * 80 + "\n")
        for karar_no, st in sorted(karar_stats.items()):
            f.write(f"{karar_no:<25} kart={st['kart']} ready={st['ready']} warning={st['warning']} block={st['block']}\n")
        f.write("\n")

        f.write("ORNEK BLOCK KARTLAR\n")
        f.write("-" * 80 + "\n")
        if sample_blocks:
            for b in sample_blocks:
                p = b["normalized_preview"]
                f.write(f"Karar: {b['karar_no']} | Kart: {b['kart_index']} | Puan: {b['puan']}\n")
                f.write(f"Issues: {', '.join(b['issues'])}\n")
                f.write(f"Başlık: {p['baslik']}\n")
                f.write(f"Hukuki Soru: {p['hukuki_soru']}\n")
                f.write(f"Konu Özeti: {p['konu_ozeti']}\n")
                f.write(f"Sonuç Özeti: {p['sonuc_ozeti']}\n")
                f.write(f"Anahtar: {p['anahtar']}\n")
                f.write(f"Mevzuat: {p['mevzuat']}\n")
                f.write("-" * 40 + "\n")
        else:
            f.write("Örnek BLOCK kart yok.\n")
        f.write("\n")

        f.write("DOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Detay JSONL            : {detail_jsonl}\n")
        f.write(f"State JSON             : {state_path}\n")
        f.write(f"Rapor                  : {rapor_path}\n")

    print("\n171 MINI KALITE KONTROL TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam kart            : {total_cards}")
    print(f"READY kart             : {ready_cards}")
    print(f"WARNING kart           : {warning_cards}")
    print(f"BLOCK kart             : {block_cards}")
    print(f"Ortalama puan          : {avg_score} / 100")
    print(f"169'a geçilebilir mi   : {'EVET' if production_ready else 'HAYIR'}")

    if issue_counter:
        print("\nBLOCK sebepleri:")
        for k, v in issue_counter.most_common():
            print(f"- {k}: {v}")

    if warning_counter:
        print("\nWARNING sebepleri:")
        for k, v in warning_counter.most_common():
            print(f"- {k}: {v}")

    print("\nDosyalar:")
    print(detail_jsonl)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
