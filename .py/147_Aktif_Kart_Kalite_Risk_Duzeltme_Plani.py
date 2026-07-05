# -*- coding: utf-8 -*-
import os
import re
import json
import sqlite3
from datetime import datetime
from collections import defaultdict

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
DB_PATH = os.path.join(BASE_DIR, ".py", "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

os.makedirs(RAPOR_DIR, exist_ok=True)

TABLE = "hukuki_kartlar"
DRY_RUN = True  # Bu motor DB'ye yazmaz, sadece plan üretir.

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def norm(s):
    return (s or "").strip()

def lower_tr(s):
    return norm(s).lower().replace("ı", "i")

def has_col(cur, table, col):
    cur.execute(f"PRAGMA table_info({table})")
    return col in [r[1] for r in cur.fetchall()]

def get_col(row, col, default=""):
    return row[col] if col in row.keys() and row[col] is not None else default

def is_active(row, has_aktif):
    if not has_aktif:
        return True
    return int(get_col(row, "aktif", 1) or 1) == 1

def contradiction(row):
    st = lower_tr(get_col(row, "sonuc_tipi"))
    sonuc = lower_tr(get_col(row, "sonuc"))

    if not st or not sonuc:
        return None

    kabul_kelimeleri = [
        "yerindedir", "hakli bulun", "mevzuata aykiridir",
        "hukuka aykiridir", "düzeltici işlem", "iptal edilmesi gerekir"
    ]
    ret_kelimeleri = [
        "yerinde değildir", "yerinde degildir", "reddedilmiştir",
        "reddine", "uygun bulunmuştur", "mevzuata uygundur",
        "hukuka uygundur"
    ]

    if "ret" in st:
        if any(k in sonuc for k in kabul_kelimeleri):
            return "RET yazılmış ancak sonuç metni iddianın yerinde/aykırılık bulunduğunu gösteriyor."

    if "kabul" in st:
        if any(k in sonuc for k in ret_kelimeleri):
            return "KABUL yazılmış ancak sonuç metni iddianın reddedildiğini/yerinde olmadığını gösteriyor."

    return None

def suggest_sonuc_tipi(row):
    st = norm(get_col(row, "sonuc_tipi"))
    sonuc = lower_tr(get_col(row, "sonuc"))

    if any(k in sonuc for k in ["yerindedir", "hakli bulun", "mevzuata aykiridir", "hukuka aykiridir"]):
        return "KABUL"

    if any(k in sonuc for k in ["reddedilmiştir", "reddine", "yerinde değildir", "yerinde degildir", "mevzuata uygundur", "hukuka uygundur"]):
        return "RET"

    if "düzeltici işlem" in sonuc or "duzeltici islem" in sonuc:
        return "DÜZELTİCİ İŞLEM"

    if "iptal" in sonuc:
        return "İPTAL"

    return st

def default_sonuc(row):
    st = lower_tr(get_col(row, "sonuc_tipi"))
    baslik = norm(get_col(row, "baslik"))

    if "ret" in st:
        return "Başvuru sahibinin bu iddiası Kurul tarafından yerinde görülmemiştir."
    if "kabul" in st:
        return "Başvuru sahibinin bu iddiası Kurul tarafından yerinde görülmüştür."
    if "düzeltici" in st or "duzeltici" in st:
        return "Tespit edilen aykırılığın düzeltici işlemle giderilebilecek nitelikte olduğu sonucuna varılmıştır."
    if "iptal" in st:
        return "Tespit edilen aykırılık nedeniyle ihalenin iptaline karar verilmiştir."

    return f"{baslik} yönünden Kurul değerlendirmesi yapılmıştır."

def default_emsal(row):
    text = lower_tr(" ".join([
        get_col(row, "baslik"),
        get_col(row, "hukuki_soru"),
        get_col(row, "anahtar"),
        get_col(row, "mevzuat")
    ]))

    if "şikayet" in text or "süre" in text or "basvuru" in text:
        return "İhalelere yönelik başvurularda süre kuralları hak düşürücü niteliktedir; süresinde yapılmayan başvurular reddedilir."
    if "aşırı düşük" in text or "asiri dusuk" in text:
        return "Aşırı düşük teklif açıklamaları, idarece belirlenen önemli teklif bileşenleri ve Kamu İhale Genel Tebliği hükümleri çerçevesinde değerlendirilir."
    if "iş deneyim" in text or "is deneyim" in text:
        return "İş deneyimini gösteren belgeler, ihale dokümanında belirlenen yeterlik kriterleri ve benzer iş tanımı çerçevesinde değerlendirilir."
    if "teminat" in text:
        return "Geçici teminatın tutarı, süresi ve sunuluş şekli ihale dokümanına ve mevzuata uygun olmalıdır."
    if "teknik şartname" in text or "teknik sartname" in text:
        return "Teknik şartname düzenlemeleri idarenin ihtiyacını karşılayacak, rekabeti engellemeyecek ve isteklilerin tekliflerini sağlıklı hazırlamasına imkan verecek şekilde yapılmalıdır."
    if "yaklaşık maliyet" in text or "yaklasik maliyet" in text:
        return "Yaklaşık maliyete ilişkin işlemler ihale mevzuatında öngörülen açıklık, gizlilik ve değerlendirme kuralları çerçevesinde yürütülmelidir."
    if "fiyat farkı" in text or "fiyat farki" in text:
        return "Fiyat farkı düzenlemeleri ihale dokümanı ve ilgili fiyat farkı esaslarına uygun, açık ve uygulanabilir şekilde belirlenmelidir."

    return "İhale işlemleri, ihale dokümanı hükümleri ile 4734 sayılı Kanun’un temel ilkelerine uygun yürütülmelidir."

def main():
    ts = now_stamp()
    txt_path = os.path.join(RAPOR_DIR, f"147_aktif_kart_kalite_risk_duzeltme_plani_{ts}.txt")
    jsonl_path = os.path.join(RAPOR_DIR, f"147_aktif_kart_kalite_risk_duzeltme_plani_{ts}.jsonl")

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    has_aktif = has_col(cur, TABLE, "aktif")
    has_kalite_etiketi = has_col(cur, TABLE, "kalite_etiketi")
    has_kalite_notu = has_col(cur, TABLE, "kalite_notu")

    cur.execute(f"SELECT * FROM {TABLE}")
    all_rows = cur.fetchall()
    rows = [r for r in all_rows if is_active(r, has_aktif)]

    plan = []
    risk_count = defaultdict(int)

    # 1) Boş alan ve çelişki planları
    for r in rows:
        kart_id = get_col(r, "id")
        karar_no = norm(get_col(r, "karar_no"))
        baslik = norm(get_col(r, "baslik"))
        sonuc = norm(get_col(r, "sonuc"))
        emsal = norm(get_col(r, "emsal_ilke"))

        c = contradiction(r)
        if c:
            yeni_tip = suggest_sonuc_tipi(r)
            plan.append({
                "islem": "DUZELT",
                "risk": "SONUC_TIPI_CELISKI",
                "karar_no": karar_no,
                "kart_id": kart_id,
                "baslik": baslik,
                "alan": "sonuc_tipi",
                "eski": norm(get_col(r, "sonuc_tipi")),
                "yeni": yeni_tip,
                "not": c
            })
            risk_count["SONUC_TIPI_CELISKI"] += 1

        if not sonuc:
            plan.append({
                "islem": "DUZELT",
                "risk": "BOS_SONUC",
                "karar_no": karar_no,
                "kart_id": kart_id,
                "baslik": baslik,
                "alan": "sonuc",
                "eski": "",
                "yeni": default_sonuc(r),
                "not": "Sonuç alanı boş olduğu için asgari güvenli sonuç cümlesi önerildi."
            })
            risk_count["BOS_SONUC"] += 1

        if not emsal:
            plan.append({
                "islem": "DUZELT",
                "risk": "BOS_EMSAL_ILKE",
                "karar_no": karar_no,
                "kart_id": kart_id,
                "baslik": baslik,
                "alan": "emsal_ilke",
                "eski": "",
                "yeni": default_emsal(r),
                "not": "Emsal ilke alanı boş olduğu için konuya göre genel ilke önerildi."
            })
            risk_count["BOS_EMSAL_ILKE"] += 1

        guven = norm(get_col(r, "guven"))
        if guven in ["yüksek", "orta", "düşük"]:
            plan.append({
                "islem": "DUZELT",
                "risk": "GUVEN_FORMAT",
                "karar_no": karar_no,
                "kart_id": kart_id,
                "baslik": baslik,
                "alan": "guven",
                "eski": guven,
                "yeni": guven.capitalize(),
                "not": "Güven seviyesi yazım standardı düzeltilecek."
            })
            risk_count["GUVEN_FORMAT"] += 1

    # 2) Aktif mükerrer başlık planı
    groups = defaultdict(list)
    for r in rows:
        key = (norm(get_col(r, "karar_no")), lower_tr(get_col(r, "baslik")))
        if key[0] and key[1]:
            groups[key].append(r)

    for (karar_no, baslik_key), items in groups.items():
        if len(items) > 1:
            items_sorted = sorted(items, key=lambda x: int(get_col(x, "id", 0)))
            keep = items_sorted[0]
            for dup in items_sorted[1:]:
                plan.append({
                    "islem": "PASIFLESTIR",
                    "risk": "AKTIF_MUKERRER_BASLIK",
                    "karar_no": karar_no,
                    "kart_id": get_col(dup, "id"),
                    "baslik": norm(get_col(dup, "baslik")),
                    "aktif_yeni": 0,
                    "kalite_etiketi": "YAN_KART_MUKERRER",
                    "kalite_notu": f"Aynı karar içinde aynı başlıkla mükerrer. Korunan kart_id={get_col(keep, 'id')}.",
                    "not": "Mükerrer aktif kart pasifleştirilecek."
                })
                risk_count["AKTIF_MUKERRER_BASLIK"] += 1

    with open(jsonl_path, "w", encoding="utf-8") as f:
        for item in plan:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    lines = []
    lines.append("147 - AKTİF KART KALİTE RİSK DÜZELTME PLANI")
    lines.append("=" * 80)
    lines.append(f"Tarih             : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    lines.append(f"DB                : {DB_PATH}")
    lines.append(f"DB yaz            : False")
    lines.append(f"Aktif kart        : {len(rows)}")
    lines.append(f"Plan işlem        : {len(plan)}")
    lines.append("")
    lines.append("RİSK DAĞILIMI")
    lines.append("-" * 80)
    for k, v in sorted(risk_count.items()):
        lines.append(f"{k:<28}: {v}")
    lines.append("")
    lines.append("DETAYLAR")
    lines.append("-" * 80)

    for item in plan:
        if item["islem"] == "DUZELT":
            lines.append(
                f"[DUZELT] risk={item['risk']} karar={item['karar_no']} "
                f"kart_id={item['kart_id']} alan={item['alan']}"
            )
            lines.append(f"Başlık : {item['baslik']}")
            lines.append(f"Eski   : {item['eski']}")
            lines.append(f"Yeni   : {item['yeni']}")
            lines.append(f"Not    : {item['not']}")
            lines.append("")
        else:
            lines.append(
                f"[PASIFLESTIR] risk={item['risk']} karar={item['karar_no']} "
                f"kart_id={item['kart_id']}"
            )
            lines.append(f"Başlık : {item['baslik']}")
            lines.append(f"Etiket : {item['kalite_etiketi']}")
            lines.append(f"Not    : {item['kalite_notu']}")
            lines.append("")

    lines.append("DOSYALAR")
    lines.append("-" * 80)
    lines.append(txt_path)
    lines.append(jsonl_path)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("=" * 80)
    print("147 - AKTİF KART KALİTE RİSK DÜZELTME PLANI")
    print("=" * 80)
    print()
    print("DÜZELTME PLANI OLUŞTURULDU")
    print("-" * 80)
    print(f"Aktif kart  : {len(rows)}")
    print(f"Plan işlem  : {len(plan)}")
    print(f"DB yaz      : False")
    print()
    print("Risk dağılımı:")
    for k, v in sorted(risk_count.items()):
        print(f"- {k}: {v}")
    print()
    print("Dosyalar:")
    print(txt_path)
    print(jsonl_path)
    print()
    print("NOT: DB'ye yazılmadı. Önce planı kontrol edeceğiz.")

    con.close()

if __name__ == "__main__":
    main()