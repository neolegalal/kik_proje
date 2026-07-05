# -*- coding: utf-8 -*-
import os, json, glob
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

def latest_file(pattern):
    files = glob.glob(os.path.join(RAPOR_DIR, pattern))
    return max(files, key=os.path.getmtime) if files else None

def load_jsonl(path):
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out

def parse_content_to_json(content):
    if isinstance(content, dict):
        return content
    if not isinstance(content, str):
        return {}
    txt = content.strip()
    if txt.startswith("```"):
        txt = txt.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(txt)
    except Exception:
        return {}

def extract_from_batch_row(row):
    custom_id = row.get("custom_id", "")

    body = (
        row.get("response", {})
           .get("body", {})
    )

    content = ""

    try:
        content = body["choices"][0]["message"]["content"]
    except Exception:
        pass

    parsed = parse_content_to_json(content)

    karar_no = (
        parsed.get("karar_no")
        or parsed.get("kararNo")
        or row.get("karar_no")
        or custom_id
    )

    cards = (
        parsed.get("kartlar")
        or parsed.get("hukuki_kartlar")
        or parsed.get("cards")
        or []
    )

    return karar_no, cards

def extract_from_normal_row(row):
    karar_no = (
        row.get("karar_no")
        or row.get("kararNo")
        or row.get("custom_id")
        or row.get("id")
        or ""
    )

    cards = (
        row.get("kartlar")
        or row.get("hukuki_kartlar")
        or row.get("batch_kartlar")
        or row.get("sade_kartlar")
        or row.get("cards")
        or []
    )

    return karar_no, cards

def card_get(card, *keys):
    for k in keys:
        if k in card:
            return card.get(k)
    return ""

def norm(x):
    return str(x or "").strip().lower()

def sig(card):
    return "|".join([
        norm(card_get(card, "baslik", "başlık")),
        norm(card_get(card, "hukuki_soru")),
        norm(card_get(card, "sonuc_tipi")),
        norm(card_get(card, "sonuc")),
        norm(card_get(card, "emsal_ilke")),
        norm(card_get(card, "anahtar_kelime", "anahtar")),
    ])

def write_card(f, title, idx, card):
    f.write(f"\n[{title} {idx}]\n")
    f.write(f"İddia No    : {card_get(card, 'iddia_no', 'iddiaNo')}\n")
    f.write(f"Başlık      : {card_get(card, 'baslik', 'başlık')}\n")
    f.write(f"Hukuki Soru : {card_get(card, 'hukuki_soru')}\n")
    f.write(f"Sonuç Tipi  : {card_get(card, 'sonuc_tipi')}\n")
    f.write(f"Sonuç       : {card_get(card, 'sonuc')}\n")
    f.write(f"Emsal İlke  : {card_get(card, 'emsal_ilke')}\n")
    f.write(f"Anahtar     : {card_get(card, 'anahtar_kelime', 'anahtar')}\n")
    f.write(f"Mevzuat     : {card_get(card, 'mevzuat')}\n")
    f.write(f"Güven       : {card_get(card, 'guven')}\n")

def main():
    print("="*80)
    print("136D - BATCH SADELEME KONTROL RAPORU")
    print("="*80)

    raw_path = latest_file("133A_batch_sonuc_*.jsonl")
    sade_path = latest_file("136C_batch_akilli_sadelesmis_*.jsonl")

    if not raw_path:
        print("HATA: 133A_batch_sonuc_*.jsonl bulunamadı.")
        return
    if not sade_path:
        print("HATA: 136C_batch_akilli_sadelesmis_*.jsonl bulunamadı.")
        return

    raw_rows = load_jsonl(raw_path)
    sade_rows = load_jsonl(sade_path)

    raw_by = {}
    for row in raw_rows:
        karar_no, cards = extract_from_batch_row(row)
        raw_by[karar_no] = cards

    sade_by = {}
    for row in sade_rows:
        karar_no, cards = extract_from_normal_row(row)
        sade_by[karar_no] = cards

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rapor = os.path.join(RAPOR_DIR, f"136D_batch_sadeleme_kontrol_raporu_{ts}.txt")
    csv = os.path.join(RAPOR_DIR, f"136D_batch_sadeleme_kontrol_ozet_{ts}.csv")

    kararlar = sorted(set(raw_by.keys()) | set(sade_by.keys()))

    toplam_raw = toplam_sade = toplam_cikarilan = riskli = 0

    with open(rapor, "w", encoding="utf-8") as f, open(csv, "w", encoding="utf-8-sig") as c:
        c.write("karar_no,ham_kart,sade_kart,cikarilan_kart,risk\n")

        f.write("136D - BATCH SADELEME KONTROL RAPORU\n")
        f.write("="*100 + "\n")
        f.write(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Ham Batch JSONL : {raw_path}\n")
        f.write(f"Sade JSONL      : {sade_path}\n\n")

        for karar_no in kararlar:
            raw_cards = raw_by.get(karar_no, [])
            sade_cards = sade_by.get(karar_no, [])

            raw_sigs = [sig(x) for x in raw_cards]
            sade_sigs = [sig(x) for x in sade_cards]

            removed = []
            for i, card in enumerate(raw_cards, 1):
                if sig(card) not in sade_sigs:
                    removed.append((i, card))

            ham = len(raw_cards)
            sade = len(sade_cards)
            cik = len(removed)

            toplam_raw += ham
            toplam_sade += sade
            toplam_cikarilan += cik

            risk = "NORMAL"
            if ham > 0 and sade == 0:
                risk = "YÜKSEK RİSK: Tüm kartlar silinmiş"
                riskli += 1
            elif ham >= 4 and sade <= 1:
                risk = "YÜKSEK RİSK: Aşırı sadeleşmiş"
                riskli += 1
            elif cik >= 3:
                risk = "KONTROL: Çok kart çıkarılmış"
                riskli += 1

            c.write(f'"{karar_no}",{ham},{sade},{cik},"{risk}"\n')

            f.write("\n" + "="*100 + "\n")
            f.write(f"KARAR NO: {karar_no}\n")
            f.write(f"HAM BATCH KART SAYISI : {ham}\n")
            f.write(f"SADE KART SAYISI      : {sade}\n")
            f.write(f"ÇIKARILAN KART        : {cik}\n")
            f.write(f"RİSK                  : {risk}\n")
            f.write("="*100 + "\n")

            f.write("\n### SADE KALAN KARTLAR\n")
            f.write("-"*100 + "\n")
            for i, card in enumerate(sade_cards, 1):
                write_card(f, "SADE KART", i, card)

            f.write("\n### ÇIKARILAN HAM KARTLAR\n")
            f.write("-"*100 + "\n")
            if not removed:
                f.write("Çıkarılan kart yok.\n")
            for i, card in removed:
                write_card(f, "ÇIKARILAN HAM KART", i, card)

        f.write("\n\n" + "="*100 + "\n")
        f.write("GENEL ÖZET\n")
        f.write("="*100 + "\n")
        f.write(f"Karar sayısı     : {len(kararlar)}\n")
        f.write(f"Ham Batch kart   : {toplam_raw}\n")
        f.write(f"Sade kart        : {toplam_sade}\n")
        f.write(f"Çıkarılan kart   : {toplam_cikarilan}\n")
        f.write(f"Riskli karar     : {riskli}\n")
        if toplam_raw:
            f.write(f"Azalma oranı     : %{round((toplam_raw-toplam_sade)*100/toplam_raw, 2)}\n")

    print()
    print("KONTROL RAPORU OLUŞTURULDU")
    print("-"*80)
    print(f"Karar sayısı    : {len(kararlar)}")
    print(f"Ham kart        : {toplam_raw}")
    print(f"Sade kart       : {toplam_sade}")
    print(f"Çıkarılan kart  : {toplam_cikarilan}")
    print(f"Riskli karar    : {riskli}")
    print()
    print("Dosyalar:")
    print(rapor)
    print(csv)
    print()
    print("NOT: DB'ye yazılmadı.")

if __name__ == "__main__":
    main()