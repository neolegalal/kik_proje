# -*- coding: utf-8 -*-
import os
import json
import glob
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

def latest_file(pattern):
    files = glob.glob(os.path.join(RAPOR_DIR, pattern))
    if not files:
        return None
    return max(files, key=os.path.getmtime)

def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def getv(d, *keys, default=""):
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] is not None:
            return d[k]
    return default

def normalize_text(x):
    return str(x or "").strip().lower()

def suggest_result_type(card):
    sonuc = normalize_text(getv(card, "sonuc", "Sonuç"))
    mevcut = getv(card, "sonuc_tipi", "Sonuç Tipi", default="")

    kabul_words = [
        "iddia yerindedir",
        "yerinde görülmüştür",
        "uygun olmadığı",
        "mevzuata aykırı",
        "hukuka aykırı",
        "düzeltici işlem",
        "iptaline",
        "yeterli görülmemesinde mevzuata uyarlık bulunmadığı",
    ]

    ret_words = [
        "yerinde değildir",
        "reddedilmiştir",
        "reddine",
        "süre yönünden redd",
        "görev yönünden redd",
        "uygun bulunmuştur",
        "mevzuata uygundur",
        "hukuka uygundur",
    ]

    if any(w in sonuc for w in kabul_words):
        return "KABUL"
    if any(w in sonuc for w in ret_words):
        return "RET"
    if "iptal" in sonuc:
        return "İPTAL"
    return mevcut

def improve_emsal(card):
    emsal = getv(card, "emsal_ilke", "Emsal İlke")
    sonuc = getv(card, "sonuc", "Sonuç")
    konu = normalize_text(getv(card, "baslik", "Başlık"))

    if normalize_text(emsal) == normalize_text(sonuc) or len(str(emsal)) < 40:
        if "süre" in konu:
            return "Şikâyet ve itirazen şikâyet başvurularında süre, işlemin farkına varıldığı veya farkına varılmış olması gereken tarihi izleyen günden itibaren başlar; süresinden sonra yapılan başvurular reddedilir."
        if "bilgi" in konu or "tamamlama" in konu:
            return "Belgelerde teklifin veya başvurunun esasını değiştirmeyen bilgi eksikliği bulunması halinde idare, doğrudan eleme yerine bilgi eksikliğinin tamamlatılması yoluna gitmelidir."
        if "iş deneyim" in konu or "benzer iş" in konu:
            return "İş deneyim belgeleri, ihale dokümanında belirlenen benzer iş tanımı ve belge kapsamı birlikte değerlendirilerek incelenmeli; ayrıştırılamayan bütünleşik hizmetler şekli gerekçelerle dışlanmamalıdır."
        if "aşırı düşük" in konu:
            return "Aşırı düşük teklif açıklaması istenirken önemli teklif bileşenleri açık, somut ve istekliler bakımından eşit uygulanabilir şekilde belirlenmelidir."
        return "Emsal ilke, kararın somut sonucunu tekrar etmek yerine benzer olaylarda uygulanabilecek genel hukuki kural şeklinde yazılmalıdır."

    return emsal

def confidence_suggestion(card, riskler):
    guven = normalize_text(getv(card, "guven", "Güven"))
    if riskler:
        return "Orta"
    if guven in ["yüksek", "high"]:
        return "Yüksek"
    return getv(card, "guven", "Güven", default="Orta")

def main():
    print("=" * 80)
    print("140 - BATCH VALIDATOR DÜZELTME PLANI")
    print("=" * 80)

    riskli_path = latest_file("139_batch_kart_validator_riskli_kartlar_*.jsonl")
    if not riskli_path:
        print("HATA: 139 riskli kart JSONL dosyası bulunamadı.")
        return

    rows = read_jsonl(riskli_path)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    txt_path = os.path.join(RAPOR_DIR, f"140_batch_validator_duzeltme_plani_{ts}.txt")
    jsonl_path = os.path.join(RAPOR_DIR, f"140_batch_validator_duzeltme_plani_{ts}.jsonl")

    out_rows = []

    with open(txt_path, "w", encoding="utf-8") as txt, open(jsonl_path, "w", encoding="utf-8") as js:
        txt.write("140 - BATCH VALIDATOR DÜZELTME PLANI\n")
        txt.write("=" * 100 + "\n")
        txt.write(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        txt.write(f"Kaynak dosya: {riskli_path}\n")
        txt.write(f"Riskli kart sayısı: {len(rows)}\n\n")

        for i, row in enumerate(rows, 1):
            karar_no = getv(row, "karar_no", "Karar No", default="BİLİNMİYOR")
            kart_no = getv(row, "kart_no", "Kart No", default=i)
            riskler = getv(row, "riskler", "Riskler", default=[])

            card = getv(row, "kart", "card", default=row)
            if not isinstance(card, dict):
                card = row

            baslik = getv(card, "baslik", "Başlık")
            soru = getv(card, "hukuki_soru", "Hukuki Soru")
            mevcut_tip = getv(card, "sonuc_tipi", "Sonuç Tipi")
            sonuc = getv(card, "sonuc", "Sonuç")
            emsal = getv(card, "emsal_ilke", "Emsal İlke")
            guven = getv(card, "guven", "Güven")

            onerilen_tip = suggest_result_type(card)
            onerilen_emsal = improve_emsal(card)
            onerilen_guven = confidence_suggestion(card, riskler)

            plan = {
                "karar_no": karar_no,
                "kart_no": kart_no,
                "riskler": riskler,
                "mevcut": {
                    "baslik": baslik,
                    "hukuki_soru": soru,
                    "sonuc_tipi": mevcut_tip,
                    "sonuc": sonuc,
                    "emsal_ilke": emsal,
                    "guven": guven,
                },
                "onerilen": {
                    "sonuc_tipi": onerilen_tip,
                    "emsal_ilke": onerilen_emsal,
                    "guven": onerilen_guven,
                },
                "db_yaz": False
            }

            out_rows.append(plan)
            js.write(json.dumps(plan, ensure_ascii=False) + "\n")

            txt.write("-" * 100 + "\n")
            txt.write(f"[{i}] KARAR NO : {karar_no} | KART: {kart_no}\n")
            txt.write(f"Riskler      : {riskler}\n")
            txt.write(f"Başlık       : {baslik}\n")
            txt.write(f"Hukuki Soru  : {soru}\n\n")
            txt.write(f"Mevcut Sonuç Tipi  : {mevcut_tip}\n")
            txt.write(f"Önerilen Sonuç Tipi: {onerilen_tip}\n\n")
            txt.write(f"Sonuç:\n{sonuc}\n\n")
            txt.write(f"Mevcut Emsal İlke:\n{emsal}\n\n")
            txt.write(f"Önerilen Emsal İlke:\n{onerilen_emsal}\n\n")
            txt.write(f"Mevcut Güven  : {guven}\n")
            txt.write(f"Önerilen Güven: {onerilen_guven}\n\n")

    print("\nDÜZELTME PLANI OLUŞTURULDU")
    print("-" * 80)
    print(f"Riskli kart : {len(rows)}")
    print("\nDosyalar:")
    print(txt_path)
    print(jsonl_path)
    print("\nNOT: DB'ye yazılmadı. Sadece düzeltme planı üretildi.")

if __name__ == "__main__":
    main()