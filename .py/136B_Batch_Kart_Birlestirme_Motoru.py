import os
import re
import json
import glob
import datetime
from difflib import SequenceMatcher
from collections import defaultdict

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
os.makedirs(RAPOR_DIR, exist_ok=True)

print("=" * 80)
print("136B - BATCH KART BİRLEŞTİRME MOTORU")
print("=" * 80)

# ------------------------------------------------------------
# AYARLAR
# ------------------------------------------------------------
BENZERLIK_ESIGI = 72

BIRLESTIRME_DISI_ANAHTARLAR = [
    "başvuru bedeli",
    "itirazen şikayet başvuru bedeli",
    "iade",
    "yönetmelik’in 18",
    "yönetmelik'in 18",
    "eşit muamele",
]

AYRI_TUTULACAK_KONULAR = [
    "başvuru bedeli",
    "süre",
    "yasaklılık",
    "geçici teminat",
    "aşırı düşük",
    "iş deneyim",
    "teknik şartname",
    "yaklaşık maliyet",
    "ihale iptali",
    "kapasite raporu",
    "bilanço",
    "gelir tablosu",
]


def now_ts():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def norm_text(s):
    if s is None:
        return ""
    s = str(s).lower()
    tr_map = str.maketrans("ıİğĞüÜşŞöÖçÇ", "iigguussoocc")
    s = s.translate(tr_map)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def sim(a, b):
    a = norm_text(a)
    b = norm_text(b)
    if not a or not b:
        return 0
    return int(SequenceMatcher(None, a, b).ratio() * 100)


def contains_any(text, words):
    t = norm_text(text)
    return any(norm_text(w) in t for w in words)


def latest_file(pattern):
    files = glob.glob(os.path.join(RAPOR_DIR, pattern))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def extract_json_from_response(obj):
    """
    OpenAI Batch response yapıları farklı gelebilir.
    Bu fonksiyon mümkün olduğunca esnek okur.
    """
    if isinstance(obj, dict):
        body = obj.get("response", {}).get("body")
        if body:
            choices = body.get("choices", [])
            if choices:
                content = choices[0].get("message", {}).get("content", "")
                return parse_json_content(content)

        if "kartlar" in obj:
            return obj

        if "content" in obj:
            return parse_json_content(obj.get("content", ""))

    return None


def parse_json_content(content):
    if not content:
        return None

    if isinstance(content, dict):
        return content

    content = str(content).strip()

    content = re.sub(r"^```json", "", content, flags=re.I).strip()
    content = re.sub(r"^```", "", content).strip()
    content = re.sub(r"```$", "", content).strip()

    try:
        return json.loads(content)
    except Exception:
        pass

    m = re.search(r"\{.*\}", content, flags=re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None

    return None


def get_custom_id(row):
    return row.get("custom_id") or row.get("id") or ""


def get_karar_no_from_custom_id(custom_id):
    m = re.search(r"(\d{4}_[A-Z]+_[A-Z]+_\d+)", custom_id)
    if m:
        return m.group(1).replace("_", "/").replace("/I/", ".I-").replace("/II/", ".II-").replace("/III/", ".III-")

    m = re.search(r"(\d{4}[-/][A-ZÇĞİÖŞÜ.]+[-/]\d+)", custom_id)
    if m:
        return m.group(1).replace("-", "/")

    return custom_id


def kart_text(k):
    return " ".join([
        str(k.get("baslik", "")),
        str(k.get("hukuki_soru", "")),
        str(k.get("sonuc", "")),
        str(k.get("emsal_ilke", "")),
        str(k.get("anahtar_kelime", k.get("anahtar", ""))),
    ])


def konu_etiketi(k):
    text = norm_text(kart_text(k))

    for konu in AYRI_TUTULACAK_KONULAR:
        if norm_text(konu) in text:
            return konu

    return "genel"


def should_force_separate(k):
    text = kart_text(k)
    return contains_any(text, BIRLESTIRME_DISI_ANAHTARLAR)


def kart_benzerlik(k1, k2):
    s1 = sim(k1.get("hukuki_soru", ""), k2.get("hukuki_soru", ""))
    s2 = sim(k1.get("baslik", ""), k2.get("baslik", ""))
    s3 = sim(k1.get("emsal_ilke", ""), k2.get("emsal_ilke", ""))
    s4 = sim(k1.get("anahtar_kelime", k1.get("anahtar", "")), k2.get("anahtar_kelime", k2.get("anahtar", "")))

    return int((s1 * 0.35) + (s2 * 0.25) + (s3 * 0.25) + (s4 * 0.15))


def merge_group(group):
    if len(group) == 1:
        k = dict(group[0])
        k["birlesen_kart_sayisi"] = 1
        k["birlesme_notu"] = "Tek kart, birleştirme yapılmadı."
        return k

    sonuc_tipleri = [str(k.get("sonuc_tipi", "")).upper() for k in group if k.get("sonuc_tipi")]
    sonuc_tipi = "BELİRSİZ"

    for tercih in ["DÜZELTİCİ İŞLEM", "İPTAL", "KABUL", "RET", "KARAR VERİLMESİNE YER OLMADIĞI"]:
        if tercih in sonuc_tipleri:
            sonuc_tipi = tercih
            break

    basliklar = [k.get("baslik", "") for k in group if k.get("baslik")]
    sorular = [k.get("hukuki_soru", "") for k in group if k.get("hukuki_soru")]
    sonuclar = [k.get("sonuc", "") for k in group if k.get("sonuc")]
    ilkeler = [k.get("emsal_ilke", "") for k in group if k.get("emsal_ilke")]
    anahtarlar = []
    mevzuatlar = []

    for k in group:
        ak = k.get("anahtar_kelime", k.get("anahtar", ""))
        if ak:
            anahtarlar.extend([x.strip() for x in str(ak).split(",") if x.strip()])
        mev = k.get("mevzuat", "")
        if mev:
            mevzuatlar.extend([x.strip() for x in str(mev).split(";") if x.strip()])

    def longest(items):
        items = [x.strip() for x in items if x and str(x).strip()]
        return max(items, key=len) if items else ""

    merged = {
        "iddia_no": min([int(k.get("iddia_no", 999)) for k in group if str(k.get("iddia_no", "")).isdigit()] or [1]),
        "baslik": longest(basliklar),
        "hukuki_soru": longest(sorular),
        "sonuc_tipi": sonuc_tipi,
        "sonuc": longest(sonuclar),
        "emsal_ilke": longest(ilkeler),
        "anahtar_kelime": ", ".join(sorted(set(anahtarlar), key=lambda x: x.lower())),
        "mevzuat": "; ".join(sorted(set(mevzuatlar), key=lambda x: x.lower())),
        "guven": "Yüksek",
        "birlesen_kart_sayisi": len(group),
        "birlesme_notu": "Aynı hukuki uyuşmazlık/aynı mevzuat ekseni görüldüğü için birleştirildi."
    }

    return merged


def cluster_cards(cards):
    groups = []

    for card in cards:
        if should_force_separate(card):
            groups.append([card])
            continue

        placed = False
        card_konu = konu_etiketi(card)

        for g in groups:
            if any(should_force_separate(x) for x in g):
                continue

            g_konu = konu_etiketi(g[0])

            if card_konu != g_konu:
                continue

            scores = [kart_benzerlik(card, x) for x in g]
            max_score = max(scores) if scores else 0

            same_result = norm_text(card.get("sonuc_tipi", "")) == norm_text(g[0].get("sonuc_tipi", ""))
            close_enough = max_score >= BENZERLIK_ESIGI

            if close_enough or same_result and max_score >= 62:
                g.append(card)
                placed = True
                break

        if not placed:
            groups.append([card])

    return groups


# ------------------------------------------------------------
# JSONL BUL
# ------------------------------------------------------------
jsonl_path = latest_file("133A_batch_sonuc_*.jsonl")

if not jsonl_path:
    print("133A batch sonuç JSONL bulunamadı.")
    raise SystemExit

print(f"\nOkunan Batch JSONL:\n{jsonl_path}")

# ------------------------------------------------------------
# OKU
# ------------------------------------------------------------
kararlar = {}

with open(jsonl_path, "r", encoding="utf-8") as f:
    for line_no, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue

        try:
            row = json.loads(line)
        except Exception as e:
            print(f"JSON satır okunamadı: {line_no} | {e}")
            continue

        custom_id = get_custom_id(row)
        parsed = extract_json_from_response(row)

        if not parsed:
            continue

        karar_no = parsed.get("karar_no") or get_karar_no_from_custom_id(custom_id)
        kartlar = parsed.get("kartlar", [])

        if not isinstance(kartlar, list):
            continue

        kararlar[karar_no] = {
            "custom_id": custom_id,
            "ham": parsed,
            "kartlar": kartlar
        }

# ------------------------------------------------------------
# BİRLEŞTİR
# ------------------------------------------------------------
sonuc_rows = []
jsonl_out = os.path.join(RAPOR_DIR, f"136B_batch_kart_birlestirilmis_{now_ts()}.jsonl")
txt_out = os.path.join(RAPOR_DIR, f"136B_batch_kart_birlestirme_raporu_{now_ts()}.txt")

total_before = 0
total_after = 0

with open(jsonl_out, "w", encoding="utf-8") as jout, open(txt_out, "w", encoding="utf-8") as rout:
    rout.write("136B - BATCH KART BİRLEŞTİRME RAPORU\n")
    rout.write("=" * 100 + "\n")
    rout.write(f"Tarih: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
    rout.write(f"Kaynak JSONL: {jsonl_path}\n")
    rout.write(f"Benzerlik eşiği: {BENZERLIK_ESIGI}\n\n")

    for karar_no, data in kararlar.items():
        cards = data["kartlar"]
        total_before += len(cards)

        groups = cluster_cards(cards)
        merged_cards = [merge_group(g) for g in groups]

        for idx, k in enumerate(merged_cards, 1):
            k["iddia_no"] = idx

        total_after += len(merged_cards)

        out_obj = {
            "karar_no": karar_no,
            "custom_id": data["custom_id"],
            "orijinal_kart_sayisi": len(cards),
            "birlestirilmis_kart_sayisi": len(merged_cards),
            "kartlar": merged_cards
        }

        jout.write(json.dumps(out_obj, ensure_ascii=False) + "\n")

        rout.write("\n" + "=" * 100 + "\n")
        rout.write(f"KARAR NO: {karar_no}\n")
        rout.write(f"Önceki Batch kart sayısı : {len(cards)}\n")
        rout.write(f"Birleşmiş kart sayısı    : {len(merged_cards)}\n")
        rout.write("-" * 100 + "\n")

        for i, k in enumerate(merged_cards, 1):
            rout.write(f"\n[BİRLEŞMİŞ KART {i}]\n")
            rout.write(f"Başlık     : {k.get('baslik','')}\n")
            rout.write(f"Soru       : {k.get('hukuki_soru','')}\n")
            rout.write(f"Sonuç Tipi : {k.get('sonuc_tipi','')}\n")
            rout.write(f"Sonuç      : {k.get('sonuc','')}\n")
            rout.write(f"İlke       : {k.get('emsal_ilke','')}\n")
            rout.write(f"Anahtar    : {k.get('anahtar_kelime','')}\n")
            rout.write(f"Birleşen   : {k.get('birlesen_kart_sayisi','')}\n")
            rout.write(f"Not        : {k.get('birlesme_notu','')}\n")

    rout.write("\n\n" + "=" * 100 + "\n")
    rout.write("GENEL ÖZET\n")
    rout.write("=" * 100 + "\n")
    rout.write(f"Karar sayısı              : {len(kararlar)}\n")
    rout.write(f"Batch ham kart sayısı      : {total_before}\n")
    rout.write(f"Birleşmiş kart sayısı      : {total_after}\n")
    rout.write(f"Azalma                    : {total_before - total_after}\n")

print("\nBİRLEŞTİRME TAMAMLANDI")
print("-" * 80)
print(f"Karar sayısı         : {len(kararlar)}")
print(f"Batch ham kart       : {total_before}")
print(f"Birleşmiş kart       : {total_after}")
print(f"Azalma               : {total_before - total_after}")
print("\nOluşturulan dosyalar:")
print(jsonl_out)
print(txt_out)
print("\nNOT: DB'ye yazılmadı. Sadece birleşmiş Batch kart çıktısı üretildi.")