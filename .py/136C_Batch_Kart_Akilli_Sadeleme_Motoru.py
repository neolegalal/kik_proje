import os, re, json, glob, datetime
from difflib import SequenceMatcher

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

DROP_KONULAR = [
    "başvuru bedeli", "başvuru bedelinin iadesi", "iade",
    "yönetmelik’in 18", "yönetmelik'in 18",
    "eşit muamele", "dava yolu", "65'inci madde"
]

ANA_KONU_GRUPLARI = {
    "iş deneyim belgesi": ["iş deneyim", "benzer iş", "ön yeterlik", "bilgi eksikliği", "tamamlatma", "tek sözleşme"],
    "aşırı düşük teklif": ["aşırı düşük", "önemli teklif bileşeni", "teklif açıklaması", "tebliğ 79", "tebliğ 45"],
    "ihale iptali": ["ihale iptali", "iptal", "takdir yetkisi", "tek geçerli teklif", "kamu yararı"],
    "teknik şartname": ["teknik şartname", "rekabet", "belirsizlik", "gramaj", "araç", "model yılı", "kilometre"],
    "yaklaşık maliyet": ["yaklaşık maliyet", "güncelleme", "birim fiyat", "rayiç", "sınır değer"],
    "yasaklılık": ["yasaklılık", "kamu davası", "ihaleye katılamayacak", "sözleşme imzalanmaması"],
    "süre": ["şikayet süresi", "süre yönünden", "süresinde", "başvuru süresi"],
    "kapasite raporu": ["kapasite raporu", "mücbir sebep", "mutfak", "yemek"],
    "üts teknik belge": ["üts", "kapsam dışı", "yetki belgesi", "katalog", "tıbbi cihaz"],
    "ekonomik mali yeterlik": ["bilanço", "gelir tablosu", "ekonomik ve mali yeterlik"],
    "sözleşme ceza fesih": ["cezai işlem", "fesih", "ağır aykırılık", "sözleşme tasarısı"]
}

SONUC_ONCELIK = ["DÜZELTİCİ İŞLEM", "İPTAL", "KABUL", "RET", "KARAR VERİLMESİNE YER OLMADIĞI", "BELİRSİZ"]

def ts():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def norm(s):
    s = str(s or "").lower()
    s = s.translate(str.maketrans("ıİğĞüÜşŞöÖçÇ", "iigguussoocc"))
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def latest(pattern):
    files = glob.glob(os.path.join(RAPOR_DIR, pattern))
    return max(files, key=os.path.getmtime) if files else None

def parse_content(content):
    if isinstance(content, dict):
        return content
    content = str(content or "").strip()
    content = re.sub(r"^```json|^```|```$", "", content, flags=re.I).strip()
    try:
        return json.loads(content)
    except:
        m = re.search(r"\{.*\}", content, re.S)
        return json.loads(m.group(0)) if m else None

def read_batch_row(row):
    body = row.get("response", {}).get("body", {})
    choices = body.get("choices", [])
    if choices:
        return parse_content(choices[0].get("message", {}).get("content", ""))
    return parse_content(row)

def text_of(k):
    return " ".join([
        str(k.get("baslik", "")),
        str(k.get("hukuki_soru", "")),
        str(k.get("sonuc", "")),
        str(k.get("emsal_ilke", "")),
        str(k.get("anahtar_kelime", "")),
        str(k.get("anahtar", "")),
    ])

def is_drop(k):
    t = norm(text_of(k))
    return any(norm(x) in t for x in DROP_KONULAR)

def konu_bul(k):
    t = norm(text_of(k))
    for ana, words in ANA_KONU_GRUPLARI.items():
        if any(norm(w) in t for w in words):
            return ana
    return "diğer"

def longest(items):
    items = [str(x).strip() for x in items if str(x or "").strip()]
    return max(items, key=len) if items else ""

def uniq_join(values, sep=", "):
    out = []
    for v in values:
        for p in re.split(r"[,;]", str(v or "")):
            p = p.strip()
            if p and norm(p) not in [norm(x) for x in out]:
                out.append(p)
    return sep.join(out)

def sonuc_sec(cards):
    vals = [str(k.get("sonuc_tipi", "")).upper().strip() for k in cards]
    for s in SONUC_ONCELIK:
        if s in vals:
            return s
    return "BELİRSİZ"

def merge_cards(cards, konu):
    return {
        "iddia_no": 0,
        "baslik": longest([k.get("baslik") for k in cards]),
        "hukuki_soru": longest([k.get("hukuki_soru") for k in cards]),
        "sonuc_tipi": sonuc_sec(cards),
        "sonuc": longest([k.get("sonuc") for k in cards]),
        "emsal_ilke": longest([k.get("emsal_ilke") for k in cards]),
        "anahtar_kelime": uniq_join([k.get("anahtar_kelime") or k.get("anahtar") for k in cards]),
        "mevzuat": uniq_join([k.get("mevzuat") for k in cards], sep="; "),
        "guven": "Yüksek",
        "ana_konu": konu,
        "birlesen_kart_sayisi": len(cards),
        "sadeleme_notu": "Aynı ana hukuki uyuşmazlığa ait alt argümanlar tek emsal kartta toplandı."
    }

print("="*80)
print("136C - BATCH KART AKILLI SADELEME MOTORU")
print("="*80)

src = latest("133A_batch_sonuc_*.jsonl")
if not src:
    raise SystemExit("133A batch sonuç JSONL bulunamadı.")

out_jsonl = os.path.join(RAPOR_DIR, f"136C_batch_akilli_sadelesmis_{ts()}.jsonl")
out_txt = os.path.join(RAPOR_DIR, f"136C_batch_akilli_sadeleme_raporu_{ts()}.txt")

kararlar = []

with open(src, "r", encoding="utf-8") as f:
    for line in f:
        if not line.strip():
            continue
        row = json.loads(line)
        parsed = read_batch_row(row)
        if not parsed:
            continue
        karar_no = parsed.get("karar_no") or row.get("custom_id", "")
        cards = parsed.get("kartlar", [])
        kararlar.append((karar_no, row.get("custom_id", ""), cards))

before_total = 0
after_total = 0
dropped_total = 0

with open(out_jsonl, "w", encoding="utf-8") as jout, open(out_txt, "w", encoding="utf-8") as txt:
    txt.write("136C - BATCH KART AKILLI SADELEME RAPORU\n")
    txt.write("="*100 + "\n")
    txt.write(f"Kaynak: {src}\n\n")

    for karar_no, custom_id, cards in kararlar:
        before_total += len(cards)

        kept = [k for k in cards if not is_drop(k)]
        dropped = len(cards) - len(kept)
        dropped_total += dropped

        groups = {}
        for k in kept:
            konu = konu_bul(k)
            groups.setdefault(konu, []).append(k)

        merged = []
        for konu, ks in groups.items():
            merged.append(merge_cards(ks, konu))

        for i, k in enumerate(merged, 1):
            k["iddia_no"] = i

        after_total += len(merged)

        obj = {
            "karar_no": karar_no,
            "custom_id": custom_id,
            "batch_ham_kart_sayisi": len(cards),
            "usuli_yan_kart_cikarilan": dropped,
            "sadelesmis_kart_sayisi": len(merged),
            "kartlar": merged
        }
        jout.write(json.dumps(obj, ensure_ascii=False) + "\n")

        txt.write("\n" + "="*100 + "\n")
        txt.write(f"KARAR NO: {karar_no}\n")
        txt.write(f"Ham kart       : {len(cards)}\n")
        txt.write(f"Çıkarılan yan  : {dropped}\n")
        txt.write(f"Sade kart      : {len(merged)}\n")
        txt.write("-"*100 + "\n")

        for k in merged:
            txt.write(f"\n[KART {k['iddia_no']}]\n")
            txt.write(f"Ana konu   : {k.get('ana_konu')}\n")
            txt.write(f"Başlık     : {k.get('baslik')}\n")
            txt.write(f"Soru       : {k.get('hukuki_soru')}\n")
            txt.write(f"Sonuç Tipi : {k.get('sonuc_tipi')}\n")
            txt.write(f"Sonuç      : {k.get('sonuc')}\n")
            txt.write(f"İlke       : {k.get('emsal_ilke')}\n")
            txt.write(f"Birleşen   : {k.get('birlesen_kart_sayisi')}\n")

    txt.write("\n\nGENEL ÖZET\n")
    txt.write("="*100 + "\n")
    txt.write(f"Karar sayısı        : {len(kararlar)}\n")
    txt.write(f"Ham Batch kart      : {before_total}\n")
    txt.write(f"Çıkarılan yan kart  : {dropped_total}\n")
    txt.write(f"Sade kart           : {after_total}\n")
    txt.write(f"Azalma              : {before_total - after_total}\n")

print("\nAKILLI SADELEME TAMAMLANDI")
print("-"*80)
print(f"Karar sayısı       : {len(kararlar)}")
print(f"Ham Batch kart     : {before_total}")
print(f"Çıkarılan yan kart : {dropped_total}")
print(f"Sade kart          : {after_total}")
print(f"Azalma             : {before_total - after_total}")
print("\nDosyalar:")
print(out_jsonl)
print(out_txt)
print("\nNOT: DB'ye yazılmadı.")