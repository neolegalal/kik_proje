# -*- coding: utf-8 -*-
"""
171 v2 - MINI URETIM KALITE KONTROL MOTORU
==========================================

Amaç:
- En güncel 168 production output JSONL dosyasını bulur.
- Üretilen kartlarda Hedef 1 WEB ve Hedef 2 RAG/Danışmanlık kalite kontrollerini yapar.
- DB'ye yazmadan önce 169 Importer'a geçilip geçilemeyeceğini söyler.

v2 Revizyonu:
- KONU_SONUC_AYRIMI kontrolü daha adil hale getirildi.
- Kurul/başvuru/mevzuat gibi doğal ortak kelimeler ayrım zayıflığı sayılmaz.
- Sadece konu_ozeti ile sonuc_ozeti neredeyse aynıysa BLOCK verir.
- Örneklerde görülen doğru konu/sonuç ayrımı artık BLOCK'a düşmemelidir.

Kullanım:
  python ".py\\171_v2_Mini_Uretim_Kalite_Kontrol_Motoru.py"

Belirli dosya ile:
  python ".py\\171_v2_Mini_Uretim_Kalite_Kontrol_Motoru.py" "C:\\...\\168_production_output_....jsonl"
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

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

READY_SCORE = 90
BLOCK_SCORE = 70
MAX_BLOCK_RATE_FOR_169 = 0.00
MIN_READY_RATE_FOR_169 = 0.80
MIN_AVG_SCORE_FOR_169 = 85

VALID_SONUC_TIPLERI = {
    "KABUL",
    "RET",
    "DÜZELTİCİ İŞLEM",
    "IPTAL",
    "İPTAL",
    "KARAR VERİLMESİNE YER OLMADIĞI",
    "DİĞER",
}

KURUM_SIRKET_IPUCLARI = [
    " ltd", " ltd.", " limited", " a.ş", " a.ş.", " anonim", " şirket",
    " belediye", " belediyesi", " bakanlık", " bakanlığı", " müdürlük", " müdürlüğü",
    " üniversite", " üniversitesi", " il özel idaresi", " genel müdürlüğü",
]

STOPWORDS = {
    "ve", "veya", "ile", "bir", "bu", "şu", "o", "da", "de", "ki", "mi", "mı", "mu", "mü",
    "için", "olan", "olarak", "gibi", "daha", "çok", "az", "ise", "ancak", "fakat", "çünkü",
    "kurul", "karar", "başvuru", "sahibi", "iddia", "ihale", "idare", "şartname", "mevzuat",
    "uyarınca", "kapsamında", "hükümleri", "hükmü", "madde", "maddesi", "göre", "tespit",
    "etmiştir", "edilmiştir", "olduğu", "olmadığı", "bulunduğu", "sonucuna", "ulaşmıştır",
}


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
    json_errors = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception as e:
                json_errors.append({"line_no": line_no, "error": str(e), "raw": line[:500]})
    return rows, json_errors


def append_jsonl(path, row):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def as_text(x):
    if x is None:
        return ""
    if isinstance(x, list):
        return " ".join(str(i) for i in x)
    return str(x)


def as_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return [str(i).strip() for i in x if str(i).strip()]
    if isinstance(x, str):
        s = x.strip()
        if not s:
            return []
        # JSON list string ise çözmeyi dene
        if s.startswith("[") and s.endswith("]"):
            try:
                obj = json.loads(s)
                if isinstance(obj, list):
                    return [str(i).strip() for i in obj if str(i).strip()]
            except Exception:
                pass
        # virgül/noktalı virgül ayrımı
        parts = re.split(r"[,;\n]+", s)
        return [p.strip(" -•\t") for p in parts if p.strip(" -•\t")]
    return [str(x).strip()] if str(x).strip() else []


def word_count(text):
    return len(re.findall(r"\b[\wçğıöşüÇĞİÖŞÜ]+\b", as_text(text), flags=re.I))


def token_set(text):
    words = re.findall(r"[a-zçğıöşü0-9]{3,}", as_text(text).lower())
    return {w for w in words if w not in STOPWORDS}


def jaccard(a, b):
    sa = token_set(a)
    sb = token_set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def contains_institution_or_company(text):
    t = " " + as_text(text).lower() + " "
    return any(ipucu in t for ipucu in KURUM_SIRKET_IPUCLARI)


def starts_like_question(text):
    t = as_text(text).strip()
    if not t:
        return False
    if t.endswith("?"):
        return True
    question_words = ["hangi", "nasıl", "ne", "neden", "kim", "ihalede", "istekli", "idare", "kurul"]
    return any(t.lower().startswith(q + " ") for q in question_words)


def has_result_language(text):
    t = as_text(text).lower()
    patterns = [
        "kabul", "ret", "redd", "düzeltici işlem", "iptal", "aykırı", "uygun olmadığı",
        "uygun olduğu", "yerinde", "yerinde olmadığı", "sonucuna", "karar verilmesine yer olmadığı",
        "değerlendirme dışı", "geçerli", "geçersiz", "tespit etmiştir",
    ]
    return any(p in t for p in patterns)


def has_topic_language(text):
    t = as_text(text).lower()
    patterns = [
        "başvuru sahibi", "ileri sür", "iddia", "ihale dokümanı", "şartname", "itirazen şikayet",
        "itirazen şikâyet", "konu", "incele", "istenmiş", "düzenlenmiş", "belirtilmiş",
    ]
    return any(p in t for p in patterns)


def konu_sonuc_ayrimi_issue(konu, sonuc):
    """
    v2: Sadece çok güçlü benzerlikte BLOCK verir.
    Normal olarak aynı mevzuat/kurul/ihale kelimelerinin geçmesi sorun değildir.
    """
    konu = as_text(konu).strip()
    sonuc = as_text(sonuc).strip()

    if not konu or not sonuc:
        return "KONU_SONUC_AYRIMI_KONTROL"

    sim = jaccard(konu, sonuc)
    konu_wc = word_count(konu)
    sonuc_wc = word_count(sonuc)

    # Neredeyse aynı metinse ağır sorun.
    norm_k = re.sub(r"\s+", " ", konu.lower()).strip()
    norm_s = re.sub(r"\s+", " ", sonuc.lower()).strip()
    if norm_k == norm_s:
        return "KONU_SONUC_AYRIMI_ZAYIF"

    # Çok yüksek kelime örtüşmesi varsa ve ikisi de kısa/benzerse sorun.
    if sim >= 0.72:
        return "KONU_SONUC_AYRIMI_ZAYIF"

    # Konu özeti tamamen sonuç diliyle yazılmışsa uyarı; BLOCK değil.
    if has_result_language(konu) and not has_topic_language(konu) and konu_wc < 45:
        return "KONU_OZETI_SONUCA_KAYMIS_OLABILIR"

    # Orta benzerlikte sadece manuel kontrol uyarısı.
    if sim >= 0.48:
        return "KONU_SONUC_AYRIMI_KONTROL"

    return None


def score_card(card):
    issues = []
    warnings = []
    score = 100

    baslik = as_text(card.get("baslik")).strip()
    hukuki_soru = as_text(card.get("hukuki_soru")).strip()
    konu_ozeti = as_text(card.get("konu_ozeti")).strip()
    sonuc_ozeti = as_text(card.get("sonuc_ozeti")).strip()
    sonuc = as_text(card.get("sonuc")).strip()
    sonuc_tipi = as_text(card.get("sonuc_tipi")).strip()
    emsal_ilke = as_text(card.get("emsal_ilke")).strip()
    anahtar = as_list(card.get("anahtar"))
    mevzuat = as_list(card.get("mevzuat"))
    guven = as_text(card.get("guven")).strip()

    # Zorunlu alanlar
    required = {
        "BASLIK_YOK": baslik,
        "HUKUKI_SORU_YOK": hukuki_soru,
        "KONU_OZETI_YOK": konu_ozeti,
        "SONUC_OZETI_YOK": sonuc_ozeti,
        "SONUC_TIPI_YOK": sonuc_tipi,
        "EMSAL_ILKE_YOK": emsal_ilke,
    }
    for code, value in required.items():
        if not value:
            issues.append(code)
            score -= 25

    # Uzunluk kontrolleri
    if konu_ozeti and word_count(konu_ozeti) < 25:
        issues.append("KONU_OZETI_COK_KISA")
        score -= 15
    if sonuc_ozeti and word_count(sonuc_ozeti) < 20:
        issues.append("SONUC_OZETI_COK_KISA")
        score -= 15
    if baslik and word_count(baslik) > 18:
        warnings.append("BASLIK_COK_UZUN")
        score -= 3

    # Liste kontrolleri
    if not isinstance(card.get("anahtar"), list):
        issues.append("ANAHTAR_LISTE_DEGIL")
        score -= 20
    if len(anahtar) < 5:
        issues.append("ANAHTAR_YETERSIZ")
        score -= 15
    if len(anahtar) > 12:
        warnings.append("ANAHTAR_COK_FAZLA")
        score -= 3

    if not isinstance(card.get("mevzuat"), list):
        warnings.append("MEVZUAT_LISTE_DEGIL")
        score -= 5
    if len(mevzuat) == 0:
        warnings.append("MEVZUAT_YOK")
        score -= 4

    # Sonuç tipi
    if sonuc_tipi and sonuc_tipi.upper() not in VALID_SONUC_TIPLERI:
        warnings.append("SONUC_TIPI_STANDART_DISI")
        score -= 5

    # Sonuc uyumu
    if sonuc_ozeti and sonuc:
        sim_sonuc = jaccard(sonuc_ozeti, sonuc)
        if sim_sonuc < 0.35:
            warnings.append("SONUC_ALANI_SONUC_OZETIYLE_ZAYIF_UYUMLU")
            score -= 5
    elif sonuc_ozeti and not sonuc:
        warnings.append("SONUC_ALANI_BOS")
        score -= 3

    # Konu/Sonuç ayrımı
    ayrim = konu_sonuc_ayrimi_issue(konu_ozeti, sonuc_ozeti)
    if ayrim == "KONU_SONUC_AYRIMI_ZAYIF":
        issues.append(ayrim)
        score -= 20
    elif ayrim:
        warnings.append(ayrim)
        score -= 3

    # Hukuki soru
    if hukuki_soru and not starts_like_question(hukuki_soru):
        warnings.append("HUKUKI_SORU_SORU_CUMLESI_DEGIL")
        score -= 5
    if hukuki_soru and contains_institution_or_company(hukuki_soru):
        warnings.append("HUKUKI_SORUDA_KURUM_SIRKET_ADI_OLABILIR")
        score -= 3

    # Başlıkta özel isim riski
    if baslik and contains_institution_or_company(baslik):
        warnings.append("BASLIKTA_KURUM_SIRKET_ADI_OLABILIR")
        score -= 3

    # Emsal ilke kontrolü
    if emsal_ilke and sonuc_ozeti and jaccard(emsal_ilke, sonuc_ozeti) >= 0.65:
        warnings.append("EMSAL_ILKE_SONUC_TEKRARI_OLABILIR")
        score -= 5

    score = max(0, min(100, score))

    if issues or score < BLOCK_SCORE:
        status = "BLOCK"
    elif warnings or score < READY_SCORE:
        status = "WARNING"
    else:
        status = "READY"

    normalized = {
        "baslik": baslik,
        "hukuki_soru": hukuki_soru,
        "konu_ozeti": konu_ozeti,
        "sonuc_ozeti": sonuc_ozeti,
        "sonuc": sonuc,
        "sonuc_tipi": sonuc_tipi,
        "emsal_ilke": emsal_ilke,
        "anahtar": anahtar,
        "mevzuat": mevzuat,
        "guven": guven,
    }

    return {
        "status": status,
        "score": score,
        "issues": issues,
        "warnings": warnings,
        "normalized": normalized,
    }


def main():
    print("=" * 80)
    print("171 v2 - MINI URETIM KALITE KONTROL MOTORU")
    print("=" * 80)

    run_tag = tag()

    if len(sys.argv) >= 2:
        input_path = sys.argv[1]
    else:
        input_path = latest_file(INPUT_PATTERN)

    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError("168 production output JSONL bulunamadı.")

    print(f"\nKontrol edilen dosya : {input_path}")
    print("-" * 80)

    rows, json_errors = read_jsonl(input_path)

    detail_path = os.path.join(LOG_DIR, f"171_v2_mini_kalite_detay_{run_tag}.jsonl")
    state_path = os.path.join(STATE_DIR, f"171_v2_mini_kalite_state_{run_tag}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"171_v2_mini_uretim_kalite_kontrol_raporu_{run_tag}.txt")

    total_cards = 0
    ready_cards = 0
    warning_cards = 0
    block_cards = 0
    scores = []
    issue_counter = Counter()
    warning_counter = Counter()
    karar_summary = defaultdict(lambda: {"kart": 0, "ready": 0, "warning": 0, "block": 0})
    block_examples = []
    warning_examples = []

    for row_idx, row in enumerate(rows, start=1):
        karar_no = as_text(row.get("karar_no") or row.get("orijinal_karar_no")).strip()
        kartlar = row.get("kartlar", [])
        if not isinstance(kartlar, list):
            kartlar = []

        for card_idx, card in enumerate(kartlar, start=1):
            total_cards += 1
            karar_summary[karar_no]["kart"] += 1

            if not isinstance(card, dict):
                card = {}

            result = score_card(card)
            status = result["status"]
            score = result["score"]
            scores.append(score)

            if status == "READY":
                ready_cards += 1
                karar_summary[karar_no]["ready"] += 1
            elif status == "WARNING":
                warning_cards += 1
                karar_summary[karar_no]["warning"] += 1
            else:
                block_cards += 1
                karar_summary[karar_no]["block"] += 1

            for issue in result["issues"]:
                issue_counter[issue] += 1
            for warning in result["warnings"]:
                warning_counter[warning] += 1

            detail = {
                "run_id": run_tag,
                "created_at": now(),
                "row_index": row_idx,
                "card_index": card_idx,
                "karar_no": karar_no,
                "status": status,
                "score": score,
                "issues": result["issues"],
                "warnings": result["warnings"],
                "card": result["normalized"],
            }
            append_jsonl(detail_path, detail)

            if status == "BLOCK" and len(block_examples) < 10:
                block_examples.append(detail)
            if status == "WARNING" and len(warning_examples) < 10:
                warning_examples.append(detail)

    avg_score = round(sum(scores) / len(scores), 2) if scores else 0
    ready_rate = round((ready_cards / total_cards) * 100, 2) if total_cards else 0
    block_rate = round((block_cards / total_cards) * 100, 2) if total_cards else 0

    can_go_169 = (
        total_cards > 0
        and len(json_errors) == 0
        and block_rate <= MAX_BLOCK_RATE_FOR_169 * 100
        and ready_rate >= MIN_READY_RATE_FOR_169 * 100
        and avg_score >= MIN_AVG_SCORE_FOR_169
    )

    state = {
        "run_id": run_tag,
        "created_at": now(),
        "input_path": input_path,
        "jsonl_rows": len(rows),
        "json_errors": len(json_errors),
        "total_cards": total_cards,
        "ready_cards": ready_cards,
        "warning_cards": warning_cards,
        "block_cards": block_cards,
        "avg_score": avg_score,
        "ready_rate": ready_rate,
        "block_rate": block_rate,
        "can_go_169": can_go_169,
        "issue_counter": dict(issue_counter),
        "warning_counter": dict(warning_counter),
        "detail_path": detail_path,
        "report_path": rapor_path,
    }
    write_json(state_path, state)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("171 v2 - MINI URETIM KALITE KONTROL RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                  : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Kontrol edilen dosya   : {input_path}\n\n")

        f.write("GENEL SONUC\n")
        f.write("-" * 80 + "\n")
        f.write(f"JSONL satır            : {len(rows)}\n")
        f.write(f"JSON hata              : {len(json_errors)}\n")
        f.write(f"Toplam kart            : {total_cards}\n")
        f.write(f"READY kart             : {ready_cards}\n")
        f.write(f"WARNING kart           : {warning_cards}\n")
        f.write(f"BLOCK kart             : {block_cards}\n")
        f.write(f"Ortalama puan          : {avg_score} / 100\n")
        f.write(f"READY oranı            : %{ready_rate}\n")
        f.write(f"BLOCK oranı            : %{block_rate}\n")
        f.write(f"169'a geçilebilir mi   : {'EVET' if can_go_169 else 'HAYIR'}\n\n")

        f.write("ANA KONTROLLER\n")
        f.write("-" * 80 + "\n")
        checks = [
            "konu_ozeti dolu mu ve yeterli uzunlukta mı?",
            "sonuc_ozeti dolu mu ve Kurul sonucunu anlatıyor mu?",
            "anahtar liste mi, yeterli ve anlamlı mı?",
            "mevzuat liste mi ve en az bir mevzuat ilişkisi var mı?",
            "sonuc alanı sonuc_ozeti ile uyumlu mu?",
            "konu_ozeti ile sonuc_ozeti gerçekten aynı metin mi, yoksa ayrılmış mı?",
            "hukuki_soru soru cümlesi mi ve danışmanlıkta kullanılabilir mi?",
            "emsal_ilke sonuç tekrarından ibaret mi?",
        ]
        for c in checks:
            f.write(f"- {c}\n")

        f.write("\nBLOCK SEBEPLERI\n")
        f.write("-" * 80 + "\n")
        if issue_counter:
            for k, v in issue_counter.most_common():
                f.write(f"{k:<45} : {v}\n")
        else:
            f.write("BLOCK sebebi yok.\n")

        f.write("\nWARNING SEBEPLERI\n")
        f.write("-" * 80 + "\n")
        if warning_counter:
            for k, v in warning_counter.most_common():
                f.write(f"{k:<45} : {v}\n")
        else:
            f.write("WARNING sebebi yok.\n")

        f.write("\nKARAR BAZLI OZET\n")
        f.write("-" * 80 + "\n")
        for karar_no, s in karar_summary.items():
            f.write(f"{karar_no:<25} kart={s['kart']} ready={s['ready']} warning={s['warning']} block={s['block']}\n")

        if block_examples:
            f.write("\nORNEK BLOCK KARTLAR\n")
            f.write("-" * 80 + "\n")
            for ex in block_examples:
                c = ex["card"]
                f.write(f"Karar: {ex['karar_no']} | Kart: {ex['card_index']} | Puan: {ex['score']}\n")
                f.write(f"Issues: {ex['issues']}\n")
                f.write(f"Warnings: {ex['warnings']}\n")
                f.write(f"Başlık: {c.get('baslik')}\n")
                f.write(f"Hukuki Soru: {c.get('hukuki_soru')}\n")
                f.write(f"Konu Özeti: {c.get('konu_ozeti')[:350]}\n")
                f.write(f"Sonuç Özeti: {c.get('sonuc_ozeti')[:350]}\n")
                f.write(f"Anahtar: {c.get('anahtar')}\n")
                f.write(f"Mevzuat: {c.get('mevzuat')}\n")
                f.write("-" * 40 + "\n")

        if warning_examples:
            f.write("\nORNEK WARNING KARTLAR\n")
            f.write("-" * 80 + "\n")
            for ex in warning_examples[:5]:
                c = ex["card"]
                f.write(f"Karar: {ex['karar_no']} | Kart: {ex['card_index']} | Puan: {ex['score']}\n")
                f.write(f"Warnings: {ex['warnings']}\n")
                f.write(f"Başlık: {c.get('baslik')}\n")
                f.write(f"Hukuki Soru: {c.get('hukuki_soru')}\n")
                f.write("-" * 40 + "\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"Detay JSONL            : {detail_path}\n")
        f.write(f"State JSON             : {state_path}\n")
        f.write(f"Rapor                  : {rapor_path}\n")

    print("\n171 v2 MINI KALITE KONTROL TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam kart            : {total_cards}")
    print(f"READY kart             : {ready_cards}")
    print(f"WARNING kart           : {warning_cards}")
    print(f"BLOCK kart             : {block_cards}")
    print(f"Ortalama puan          : {avg_score} / 100")
    print(f"169'a geçilebilir mi   : {'EVET' if can_go_169 else 'HAYIR'}")

    print("\nBLOCK sebepleri:")
    if issue_counter:
        for k, v in issue_counter.most_common():
            print(f"- {k}: {v}")
    else:
        print("- Yok")

    print("\nWARNING sebepleri:")
    if warning_counter:
        for k, v in warning_counter.most_common():
            print(f"- {k}: {v}")
    else:
        print("- Yok")

    print("\nDosyalar:")
    print(detail_path)
    print(state_path)
    print(rapor_path)


if __name__ == "__main__":
    main()
