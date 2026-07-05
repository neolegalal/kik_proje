# -*- coding: utf-8 -*-
import os, re, json, sqlite3
from datetime import datetime
from difflib import SequenceMatcher

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
DB_PATH = os.path.join(BASE_DIR, ".py", "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

PLAN_PREFIX = "140_batch_validator_duzeltme_plani_"
OUT_PREFIX = "141_batch_duzeltme_simulasyon_"

def stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def latest(prefix, ext):
    files = [os.path.join(RAPOR_DIR, f) for f in os.listdir(RAPOR_DIR)
             if f.startswith(prefix) and f.endswith(ext)]
    if not files:
        raise FileNotFoundError(f"{prefix}*{ext} bulunamadı.")
    return max(files, key=os.path.getmtime)

def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def flat(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            key = f"{prefix}.{k}" if prefix else k
            out[key] = v
            out.update(flat(v, key))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flat(v, f"{prefix}[{i}]"))
    return out

def norm(x):
    return "" if x is None else str(x).strip()

def sim(a, b):
    a, b = norm(a).lower(), norm(b).lower()
    if not a and not b:
        return 1
    if not a or not b:
        return 0
    return SequenceMatcher(None, a, b).ratio()

def pick(flatrow, names):
    for k, v in flatrow.items():
        lk = k.lower()
        for n in names:
            if lk.endswith(n.lower()) and norm(v):
                return v
    return None

def get_cards(cur, karar_no):
    cur.execute("SELECT * FROM hukuki_kartlar WHERE karar_no=?", (karar_no,))
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]

def best_match(cards, plan):
    p_baslik = plan.get("baslik")
    p_soru = plan.get("hukuki_soru")
    p_sonuc = plan.get("sonuc")
    p_emsal = plan.get("emsal_ilke")

    best, best_score = None, 0
    for c in cards:
        score = (
            sim(p_baslik, c.get("baslik")) * 0.40 +
            sim(p_soru, c.get("hukuki_soru")) * 0.30 +
            sim(p_sonuc, c.get("sonuc")) * 0.20 +
            sim(p_emsal, c.get("emsal_ilke")) * 0.10
        )
        if score > best_score:
            best, best_score = c, score

    return best, best_score

def extract_plan(row):
    fr = flat(row)

    karar_no = pick(fr, ["karar_no", "karar no", "kararNo"])
    baslik = pick(fr, ["baslik", "başlık", "mevcut_baslik", "mevcut_başlık"])
    hukuki_soru = pick(fr, ["hukuki_soru", "hukuki soru"])
    sonuc_tipi = pick(fr, ["sonuc_tipi", "sonuç_tipi", "sonuc tipi", "sonuç tipi"])
    sonuc = pick(fr, ["sonuc", "sonuç"])
    emsal_ilke = pick(fr, ["emsal_ilke", "emsal ilke"])
    guven = pick(fr, ["guven", "güven"])

    yeni_sonuc_tipi = pick(fr, [
        "onerilen_sonuc_tipi", "önerilen_sonuç_tipi",
        "yeni_sonuc_tipi", "yeni_sonuç_tipi",
        "duzeltilmis_sonuc_tipi", "düzeltilmiş_sonuç_tipi"
    ])
    yeni_sonuc = pick(fr, [
        "onerilen_sonuc", "önerilen_sonuç",
        "yeni_sonuc", "yeni_sonuç",
        "duzeltilmis_sonuc", "düzeltilmiş_sonuç"
    ])
    yeni_emsal = pick(fr, [
        "onerilen_emsal_ilke", "önerilen_emsal_ilke",
        "yeni_emsal_ilke", "duzeltilmis_emsal_ilke", "düzeltilmiş_emsal_ilke"
    ])
    yeni_guven = pick(fr, [
        "onerilen_guven", "önerilen_güven",
        "yeni_guven", "yeni_güven",
        "duzeltilmis_guven", "düzeltilmiş_güven"
    ])

    # 140 planı öneri üretmediyse basit otomatik düzeltme kuralları
    if not yeni_sonuc_tipi:
        s = norm(sonuc).lower()
        if sonuc_tipi and norm(sonuc_tipi).upper() == "RET" and any(x in s for x in ["yerindedir", "uygun bulunmamıştır", "mevzuata uyarlık bulunmadığı"]):
            yeni_sonuc_tipi = "KABUL"
        elif sonuc_tipi and norm(sonuc_tipi).upper() == "KABUL" and any(x in s for x in ["yerinde değildir", "reddedilmiştir", "uygun bulunmuştur"]):
            yeni_sonuc_tipi = "RET"

    if not yeni_guven:
        yeni_guven = "Orta"

    return {
        "ham": row,
        "karar_no": norm(karar_no),
        "baslik": baslik,
        "hukuki_soru": hukuki_soru,
        "sonuc_tipi": sonuc_tipi,
        "sonuc": sonuc,
        "emsal_ilke": emsal_ilke,
        "guven": guven,
        "oneriler": {
            "sonuc_tipi": yeni_sonuc_tipi,
            "sonuc": yeni_sonuc,
            "emsal_ilke": yeni_emsal,
            "guven": yeni_guven
        }
    }

def main():
    print("="*80)
    print("141 - BATCH VALIDATOR DÜZELTME SİMÜLASYON MOTORU")
    print("="*80)

    plan_path = latest(PLAN_PREFIX, ".jsonl")
    rows = read_jsonl(plan_path)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    ts = stamp()
    out_txt = os.path.join(RAPOR_DIR, f"{OUT_PREFIX}{ts}.txt")
    out_jsonl = os.path.join(RAPOR_DIR, f"{OUT_PREFIX}ozet_{ts}.jsonl")

    simulated, not_found, no_change = [], [], []

    for row in rows:
        p = extract_plan(row)

        if not p["karar_no"]:
            not_found.append({"sebep": "karar_no bulunamadı", "plan": row})
            continue

        cards = get_cards(cur, p["karar_no"])
        if not cards:
            not_found.append({"sebep": "DB karar_no bulunamadı", "karar_no": p["karar_no"], "plan": row})
            continue

        card, score = best_match(cards, p)
        if not card or score < 0.35:
            not_found.append({"sebep": "eşleşme skoru düşük", "karar_no": p["karar_no"], "score": score, "plan": row})
            continue

        changes = []
        for alan, yeni in p["oneriler"].items():
            if not norm(yeni):
                continue
            eski = card.get(alan)
            if norm(eski) != norm(yeni):
                changes.append({
                    "alan": alan,
                    "eski": eski,
                    "yeni": yeni,
                    "benzerlik": round(sim(eski, yeni), 4)
                })

        if changes:
            simulated.append({
                "karar_no": card.get("karar_no"),
                "kart_id": card.get("id"),
                "baslik": card.get("baslik"),
                "match_score": round(score, 4),
                "degisiklikler": changes
            })
        else:
            no_change.append({
                "karar_no": card.get("karar_no"),
                "kart_id": card.get("id"),
                "baslik": card.get("baslik")
            })

    con.close()

    with open(out_jsonl, "w", encoding="utf-8") as f:
        for r in simulated:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(out_txt, "w", encoding="utf-8") as f:
        f.write("141 - BATCH VALIDATOR DÜZELTME SİMÜLASYON RAPORU\n")
        f.write("="*100 + "\n")
        f.write(f"Tarih       : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Plan dosyası: {plan_path}\n")
        f.write(f"DB          : {DB_PATH}\n\n")
        f.write("GENEL ÖZET\n")
        f.write("-"*100 + "\n")
        f.write(f"Plan kayıt        : {len(rows)}\n")
        f.write(f"Simüle edilen kart: {len(simulated)}\n")
        f.write(f"Değişiklik toplamı: {sum(len(x['degisiklikler']) for x in simulated)}\n")
        f.write(f"Kart bulunamadı   : {len(not_found)}\n")
        f.write(f"Değişiklik yok    : {len(no_change)}\n\n")

        for i, r in enumerate(simulated, 1):
            f.write("="*100 + "\n")
            f.write(f"[{i}] {r['karar_no']} | Kart ID: {r['kart_id']} | Eşleşme: {r['match_score']}\n")
            f.write(f"Başlık: {r['baslik']}\n")
            for ch in r["degisiklikler"]:
                f.write(f"\nAlan : {ch['alan']}\n")
                f.write(f"Eski : {ch['eski']}\n")
                f.write(f"Yeni : {ch['yeni']}\n")

        if not_found:
            f.write("\n\nKART BULUNAMAYANLAR\n")
            f.write("="*100 + "\n")
            for x in not_found:
                f.write(json.dumps(x, ensure_ascii=False, indent=2) + "\n\n")

    print()
    print("SİMÜLASYON RAPORU OLUŞTURULDU")
    print("-"*80)
    print(f"Plan kayıt          : {len(rows)}")
    print(f"Simüle edilen kart  : {len(simulated)}")
    print(f"Değişiklik toplamı  : {sum(len(x['degisiklikler']) for x in simulated)}")
    print(f"Kart bulunamadı     : {len(not_found)}")
    print(f"Değişiklik yok      : {len(no_change)}")
    print()
    print("Dosyalar:")
    print(out_txt)
    print(out_jsonl)
    print()
    print("NOT: DB'ye yazılmadı.")

if __name__ == "__main__":
    main()