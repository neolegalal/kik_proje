# -*- coding: utf-8 -*-
"""
136E - BATCH GÜVENLİ SADELEME MOTORU

Amaç:
- Batch sonucundaki kartları agresif şekilde azaltmadan sadelemek.
- Sadece açık yan/usul kartlarını elemek.
- Gerçek hukuki iddiaları korumak.
- Riskli kararları otomatik olarak HAM kartlarla korumak.
- DB'ye yazmaz.

Girdi:
    raporlar/133A_batch_sonuc_*.jsonl

Çıktı:
    raporlar/136E_batch_guvenli_sadelesmis_*.jsonl
    raporlar/136E_batch_guvenli_sadeleme_raporu_*.txt
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
RAPOR_DIR = BASE_DIR / "raporlar"


YAN_KART_KELIMELERI = [
    "başvuru bedeli",
    "başvuru ücret",
    "şikayet gelirleri",
    "haklılık oranı",
    "bedelin iadesi",
    "bedeli iade",
    "dava yolu",
    "ankara idare mahkemesi",
    "4734 sayılı kanun'un 65",
    "4734 sayılı kanunun 65",
    "tebliğ edildiği tarihi izleyen otuz gün",
]

USUL_YAN_KART_KELIMELERI = [
    "yönetmelik’in 18",
    "yönetmeliğin 18",
    "eşit muamele yönünden yapılan inceleme",
    "herhangi bir aykırılık tespit edilmemiştir",
    "başvurular hakkında yönetmelik’in 18",
]

ASIL_KONU_KELIMELERI = [
    "aşırı düşük",
    "yaklaşık maliyet",
    "iş deneyim",
    "benzer iş",
    "teknik şartname",
    "idari şartname",
    "yeterlik",
    "ön yeterlik",
    "geçici teminat",
    "yasaklılık",
    "vergi borcu",
    "sgk",
    "kapasite raporu",
    "rekabet",
    "ihale iptali",
    "iptal yetkisi",
    "düzeltici işlem",
    "değerlendirme dışı",
    "fiyat dışı unsur",
    "fiyat farkı",
    "gramaj",
    "üts",
    "katalog",
    "yetki belgesi",
    "sözleşme tasarısı",
    "cezai işlem",
    "fesih",
    "bilgi eksikliği",
    "belge tamamlatma",
]


def latest_file(pattern: str) -> Path:
    files = list(RAPOR_DIR.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Dosya bulunamadı: {pattern}")
    return max(files, key=lambda p: p.stat().st_mtime)


def norm_text(x) -> str:
    if x is None:
        return ""
    return str(x).replace("\n", " ").replace("\r", " ").strip()


def lower_blob(kart: dict) -> str:
    parts = [
        kart.get("baslik"),
        kart.get("hukuki_soru"),
        kart.get("sonuc"),
        kart.get("emsal_ilke"),
        kart.get("anahtar_kelime"),
        kart.get("anahtar"),
        kart.get("mevzuat"),
        kart.get("sonuc_tipi"),
    ]
    return " ".join(norm_text(x) for x in parts).lower()


def is_yan_kart(kart: dict) -> bool:
    blob = lower_blob(kart)

    if any(k in blob for k in YAN_KART_KELIMELERI):
        return True

    if any(k in blob for k in USUL_YAN_KART_KELIMELERI):
        return True

    return False


def has_asil_konu(kart: dict) -> bool:
    blob = lower_blob(kart)
    return any(k in blob for k in ASIL_KONU_KELIMELERI)


def normalize_key(s: str) -> str:
    s = norm_text(s).lower()
    s = re.sub(r"[^\wğüşıöçİĞÜŞÖÇ]+", " ", s, flags=re.UNICODE)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def kart_signature(kart: dict) -> str:
    baslik = normalize_key(kart.get("baslik", ""))
    soru = normalize_key(kart.get("hukuki_soru", ""))
    anahtar = normalize_key(kart.get("anahtar_kelime") or kart.get("anahtar") or "")
    return f"{baslik[:80]}|{soru[:120]}|{anahtar[:80]}"


def extract_karar_no_from_custom_id(custom_id: str) -> str:
    """
    pilot_1_2026_UD_I_1056 -> 2026/UD.I-1056
    """
    m = re.search(r"(\d{4})_([A-Z]+)_([IVX]+)_(\d+)", custom_id or "")
    if not m:
        return custom_id or "BILINMEYEN"
    return f"{m.group(1)}/{m.group(2)}.{m.group(3)}-{m.group(4)}"


def parse_batch_line(line: str):
    obj = json.loads(line)

    custom_id = obj.get("custom_id") or obj.get("id") or ""
    karar_no = extract_karar_no_from_custom_id(custom_id)

    body = (
        obj.get("response", {})
        .get("body", {})
    )

    content = None

    try:
        content = body["choices"][0]["message"]["content"]
    except Exception:
        content = None

    if not content:
        return karar_no, custom_id, []

    if isinstance(content, str):
        content = content.strip()
        try:
            parsed = json.loads(content)
        except Exception:
            parsed = None
    elif isinstance(content, dict):
        parsed = content
    else:
        parsed = None

    if parsed is None:
        return karar_no, custom_id, []

    if isinstance(parsed, dict):
        if "kartlar" in parsed and isinstance(parsed["kartlar"], list):
            kartlar = parsed["kartlar"]
        elif "hukuki_kartlar" in parsed and isinstance(parsed["hukuki_kartlar"], list):
            kartlar = parsed["hukuki_kartlar"]
        elif "claims" in parsed and isinstance(parsed["claims"], list):
            kartlar = parsed["claims"]
        else:
            kartlar = []
    elif isinstance(parsed, list):
        kartlar = parsed
    else:
        kartlar = []

    clean = []
    for i, k in enumerate(kartlar, start=1):
        if not isinstance(k, dict):
            continue
        kk = dict(k)
        kk.setdefault("iddia_no", i)
        clean.append(kk)

    return karar_no, custom_id, clean


def dedupe_kartlar(kartlar):
    seen = set()
    out = []
    for k in kartlar:
        sig = kart_signature(k)
        if sig in seen:
            continue
        seen.add(sig)
        out.append(k)
    return out


def guvenli_sadele(karar_no: str, kartlar: list):
    ham = dedupe_kartlar(kartlar)

    asillar = []
    cikarilan = []

    for k in ham:
        if is_yan_kart(k) and not has_asil_konu(k):
            cikarilan.append((k, "yan/usul kart"))
            continue

        if is_yan_kart(k) and has_asil_konu(k):
            # Hem usul hem asıl konu varsa koru.
            asillar.append(k)
            continue

        asillar.append(k)

    # Güvenlik kuralı:
    # Ham kart 3+ iken sade kart 1'e düşerse fazla agresif say, ham kartları koru.
    riskli = False
    risk_nedeni = ""

    if len(ham) >= 3 and len(asillar) <= 1:
        riskli = True
        risk_nedeni = "Ham kart 3 veya üzeri iken sade kart 1'e düştü; ham kartlar korundu."
        asillar = ham
        cikarilan = []

    # Güvenlik kuralı:
    # Asıl konu içeren kart çıkarılmışsa riskli say ve geri al.
    geri_alinan = []
    kalan_cikarilan = []
    for k, neden in cikarilan:
        if has_asil_konu(k):
            geri_alinan.append(k)
        else:
            kalan_cikarilan.append((k, neden))

    if geri_alinan:
        riskli = True
        risk_nedeni = "Asıl konu içerdiği halde çıkarılacak kart tespit edildi; geri alındı."
        asillar.extend(geri_alinan)
        cikarilan = kalan_cikarilan

    asillar = dedupe_kartlar(asillar)

    for idx, k in enumerate(asillar, start=1):
        k["iddia_no"] = idx
        k["sadeleme_kaynagi"] = "136E_GUVENLI_BATCH"
        k["karar_no"] = karar_no

    return {
        "karar_no": karar_no,
        "ham_kart_sayisi": len(ham),
        "sade_kart_sayisi": len(asillar),
        "cikarilan_kart_sayisi": len(cikarilan),
        "riskli": riskli,
        "risk_nedeni": risk_nedeni,
        "kartlar": asillar,
        "cikarilanlar": [
            {
                "baslik": norm_text(k.get("baslik")),
                "hukuki_soru": norm_text(k.get("hukuki_soru")),
                "sonuc_tipi": norm_text(k.get("sonuc_tipi")),
                "neden": neden,
            }
            for k, neden in cikarilan
        ],
    }


def main():
    print("=" * 80)
    print("136E - BATCH GÜVENLİ SADELEME MOTORU")
    print("=" * 80)

    RAPOR_DIR.mkdir(parents=True, exist_ok=True)

    batch_file = latest_file("133A_batch_sonuc_*.jsonl")

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_jsonl = RAPOR_DIR / f"136E_batch_guvenli_sadelesmis_{now}.jsonl"
    out_report = RAPOR_DIR / f"136E_batch_guvenli_sadeleme_raporu_{now}.txt"

    karar_sonuclari = []

    with open(batch_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            karar_no, custom_id, kartlar = parse_batch_line(line)

            sonuc = guvenli_sadele(karar_no, kartlar)
            sonuc["custom_id"] = custom_id
            karar_sonuclari.append(sonuc)

    with open(out_jsonl, "w", encoding="utf-8") as f:
        for r in karar_sonuclari:
            f.write(json.dumps({
                "custom_id": r.get("custom_id"),
                "karar_no": r["karar_no"],
                "kartlar": r["kartlar"],
                "meta": {
                    "ham_kart_sayisi": r["ham_kart_sayisi"],
                    "sade_kart_sayisi": r["sade_kart_sayisi"],
                    "cikarilan_kart_sayisi": r["cikarilan_kart_sayisi"],
                    "riskli": r["riskli"],
                    "risk_nedeni": r["risk_nedeni"],
                    "motor": "136E_Batch_Guvenli_Sadeleme_Motoru",
                    "tarih": now,
                }
            }, ensure_ascii=False) + "\n")

    toplam_ham = sum(r["ham_kart_sayisi"] for r in karar_sonuclari)
    toplam_sade = sum(r["sade_kart_sayisi"] for r in karar_sonuclari)
    toplam_cikarilan = sum(r["cikarilan_kart_sayisi"] for r in karar_sonuclari)
    riskli_sayi = sum(1 for r in karar_sonuclari if r["riskli"])

    with open(out_report, "w", encoding="utf-8") as f:
        f.write("136E - BATCH GÜVENLİ SADELEME RAPORU\n")
        f.write("=" * 100 + "\n")
        f.write(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Batch JSONL: {batch_file}\n\n")

        f.write("GENEL ÖZET\n")
        f.write("-" * 100 + "\n")
        f.write(f"Karar sayısı       : {len(karar_sonuclari)}\n")
        f.write(f"Ham Batch kart     : {toplam_ham}\n")
        f.write(f"Güvenli sade kart  : {toplam_sade}\n")
        f.write(f"Çıkarılan yan kart : {toplam_cikarilan}\n")
        f.write(f"Riskli karar       : {riskli_sayi}\n\n")

        f.write("KARAR BAZLI ÖZET\n")
        f.write("-" * 100 + "\n")
        for r in karar_sonuclari:
            f.write(
                f"{r['karar_no']} | ham: {r['ham_kart_sayisi']} | "
                f"sade: {r['sade_kart_sayisi']} | çıkarılan: {r['cikarilan_kart_sayisi']} | "
                f"riskli: {'EVET' if r['riskli'] else 'HAYIR'}"
            )
            if r["risk_nedeni"]:
                f.write(f" | not: {r['risk_nedeni']}")
            f.write("\n")

        f.write("\nÇIKARILAN KARTLAR\n")
        f.write("-" * 100 + "\n")
        for r in karar_sonuclari:
            if not r["cikarilanlar"]:
                continue
            f.write(f"\n{r['karar_no']}\n")
            for c in r["cikarilanlar"]:
                f.write(f"  - Başlık: {c['baslik']}\n")
                f.write(f"    Soru  : {c['hukuki_soru']}\n")
                f.write(f"    Tip   : {c['sonuc_tipi']}\n")
                f.write(f"    Neden : {c['neden']}\n")

    print()
    print("GÜVENLİ SADELEME TAMAMLANDI")
    print("-" * 80)
    print(f"Karar sayısı       : {len(karar_sonuclari)}")
    print(f"Ham Batch kart     : {toplam_ham}")
    print(f"Güvenli sade kart  : {toplam_sade}")
    print(f"Çıkarılan yan kart : {toplam_cikarilan}")
    print(f"Riskli karar       : {riskli_sayi}")
    print()
    print("Dosyalar:")
    print(out_jsonl)
    print(out_report)
    print()
    print("NOT: DB'ye yazılmadı. Önce raporu kontrol edeceğiz.")


if __name__ == "__main__":
    main()