# -*- coding: utf-8 -*-
"""
128_Karar_AI_OpenAI_Toplu_Isleme_Orkestratoru.py

Amaç:
- pdfs klasöründeki PDF kararları OpenAI API ile toplu işler.
- kararlar tablosuna karar bilgilerini yazar.
- karar_iddialari ve hukuki_kartlar üretir.
- Daha önce işlenen PDF'leri atlar.
- Hata logu tutar.
- İlk üretim testi için LIMIT=500.
"""

import os
import re
import json
import time
import sqlite3
import traceback
from pathlib import Path
from datetime import datetime

from openai import OpenAI
from pypdf import PdfReader


BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PDF_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje\.py\pdfler")
DB_PATH = BASE_DIR / ".py" / "kik.db"
RAPOR_DIR = BASE_DIR / "raporlar"
RAPOR_DIR.mkdir(exist_ok=True)

MODEL = "gpt-4.1-mini"
LIMIT = 500
SLEEP_SECONDS = 0.5
MAX_TEXT_CHARS = 45000

LOG_CSV = RAPOR_DIR / f"128_openai_toplu_isleme_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

client = OpenAI()


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def temizle(metin):
    if metin is None:
        return ""
    return re.sub(r"\s+", " ", str(metin)).strip()


def oku_pdf(pdf_path):
    reader = PdfReader(str(pdf_path))
    metinler = []

    for page in reader.pages:
        try:
            metinler.append(page.extract_text() or "")
        except Exception:
            pass

    return "\n".join(metinler).strip()


def json_temizle(text):
    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1).strip()

    if text.startswith("```"):
        text = text.replace("```", "", 1).strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


def tablo_kolonlari(cur, tablo):
    return [r[1] for r in cur.execute(f"PRAGMA table_info({tablo})").fetchall()]


def guvenli_insert(cur, tablo, veri):
    kolonlar = tablo_kolonlari(cur, tablo)
    temiz_veri = {k: v for k, v in veri.items() if k in kolonlar}

    if not temiz_veri:
        return None

    cols = list(temiz_veri.keys())
    vals = [temiz_veri[c] for c in cols]

    sql = f"""
        INSERT INTO {tablo} ({",".join(cols)})
        VALUES ({",".join(["?"] * len(cols))})
    """

    cur.execute(sql, vals)
    return cur.lastrowid


def guvenli_update(cur, tablo, veri, where_col, where_val):
    kolonlar = tablo_kolonlari(cur, tablo)
    temiz_veri = {k: v for k, v in veri.items() if k in kolonlar}

    if not temiz_veri:
        return

    set_sql = ", ".join([f"{k}=?" for k in temiz_veri.keys()])
    vals = list(temiz_veri.values()) + [where_val]

    cur.execute(
        f"UPDATE {tablo} SET {set_sql} WHERE {where_col}=?",
        vals
    )


def log_yaz(satir):
    ilk = not LOG_CSV.exists()

    with open(LOG_CSV, "a", encoding="utf-8-sig", newline="") as f:
        import csv
        writer = csv.writer(f)

        if ilk:
            writer.writerow([
                "tarih",
                "dosya",
                "durum",
                "karar_no",
                "iddia_sayisi",
                "kart_sayisi",
                "hata"
            ])

        writer.writerow(satir)


def dosya_islenmis_mi(cur, dosya_adi):
    row = cur.execute(
        "SELECT id FROM kararlar WHERE dosya_adi=? LIMIT 1",
        (dosya_adi,)
    ).fetchone()

    return row is not None


def karar_no_var_mi(cur, karar_no):
    if not karar_no:
        return None

    row = cur.execute(
        "SELECT id FROM kararlar WHERE karar_no=? LIMIT 1",
        (karar_no,)
    ).fetchone()

    return row[0] if row else None


def openai_analiz_et(tam_metin, dosya_adi):
    tam_metin = tam_metin[:MAX_TEXT_CHARS]

    system_prompt = """
Sen Kamu İhale Kurulu kararlarını analiz eden uzman bir kamu ihale hukuku asistanısın.
Görevin verilen karar metnini yapılandırılmış JSON olarak çıkarmaktır.
Sadece geçerli JSON döndür. Markdown kullanma.
"""

    user_prompt = f"""
Aşağıdaki KİK karar metnini analiz et.

Dosya adı: {dosya_adi}

JSON şeması:

{{
  "karar": {{
    "karar_no": "",
    "karar_tarihi": "",
    "karar_yili": "",
    "toplanti_no": "",
    "gundem_no": "",
    "basvuru_sahibi": "",
    "idare_adi": "",
    "ihale_kayit_no": "",
    "ihale_konusu": "",
    "ihale_turu": "",
    "ihale_usulu": "",
    "ihale_ili": "",
    "karar_sonucu": "",
    "oylama": "",
    "ilgili_mevzuat": "",
    "karar_soru_basligi": "",
    "karar_ozeti": "",
    "karar_sonuc_ozeti": "",
    "ana_kategori": "",
    "anahtar_kelimeler": "",
    "emsal_degeri": ""
  }},
  "iddialar": [
    {{
      "iddia_no": 1,
      "konu": "",
      "uzman_soru": "",
      "iddia_ozeti": "",
      "kurul_cevabi": "",
      "sonuc": "",
      "emsal_ilke": "",
      "mevzuat": "",
      "anahtar_kelime": "",
      "guven": "Yüksek/Orta/Düşük",
      "iddia_turu": ""
    }}
  ],
  "hukuki_kartlar": [
    {{
      "iddia_no": 1,
      "baslik": "",
      "hukuki_soru": "",
      "kurul_degerlendirmesi": "",
      "sonuc": "",
      "emsal_ilke": "",
      "anahtar_kelime": "",
      "iddia_ozeti": "",
      "mevzuat": "",
      "guven": "Yüksek/Orta/Düşük"
    }}
  ]
}}

Kurallar:
- Karar metninde birden fazla iddia varsa ayrı iddia üret.
- Hukuki kartlar, iddialarla iddia_no üzerinden uyumlu olsun.
- Kısa ama uzman seviyesinde yaz.
- "emsal_ilke" alanı kararın uygulanabilir hukuki ilkesini içersin.
- Bilgi yoksa boş string kullan.
- Sadece JSON döndür.

KARAR METNİ:
{tam_metin}
"""

    response = client.chat.completions.create(
        model=MODEL,
        temperature=0.1,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw = response.choices[0].message.content
    data = json.loads(json_temizle(raw))
    return data


def karar_kaydet(cur, dosya_adi, tam_metin, data):
    karar = data.get("karar", {}) or {}

    karar_no = temizle(karar.get("karar_no"))
    mevcut_id = karar_no_var_mi(cur, karar_no)

    karar_yili = temizle(karar.get("karar_yili"))
    if not karar_yili and karar_no:
        m = re.search(r"20\d{2}", karar_no)
        karar_yili = m.group(0) if m else ""

    veri = {
        "dosya_adi": dosya_adi,
        "karar_no": karar_no,
        "karar_tarihi": temizle(karar.get("karar_tarihi")),
        "karar_yili": int(karar_yili) if str(karar_yili).isdigit() else None,
        "toplanti_no": temizle(karar.get("toplanti_no")),
        "gundem_no": temizle(karar.get("gundem_no")),
        "basvuru_sahibi": temizle(karar.get("basvuru_sahibi")),
        "idare_adi": temizle(karar.get("idare_adi")),
        "ihale_kayit_no": temizle(karar.get("ihale_kayit_no")),
        "ihale_konusu": temizle(karar.get("ihale_konusu")),
        "ihale_turu": temizle(karar.get("ihale_turu")),
        "ihale_usulu": temizle(karar.get("ihale_usulu")),
        "ihale_ili": temizle(karar.get("ihale_ili")),
        "karar_sonucu": temizle(karar.get("karar_sonucu")),
        "oylama": temizle(karar.get("oylama")),
        "ilgili_mevzuat": temizle(karar.get("ilgili_mevzuat")),
        "karar_soru_basligi": temizle(karar.get("karar_soru_basligi")),
        "karar_ozeti": temizle(karar.get("karar_ozeti")),
        "karar_sonuc_ozeti": temizle(karar.get("karar_sonuc_ozeti")),
        "ana_kategori": temizle(karar.get("ana_kategori")),
        "anahtar_kelimeler": temizle(karar.get("anahtar_kelimeler")),
        "emsal_degeri": temizle(karar.get("emsal_degeri")),
        "tam_metin": tam_metin,
        "islenme_tarihi": now(),
    }

    if mevcut_id:
        guvenli_update(cur, "kararlar", veri, "id", mevcut_id)
        return mevcut_id, karar_no

    karar_id = guvenli_insert(cur, "kararlar", veri)
    return karar_id, karar_no


def iddia_var_mi(cur, karar_no, iddia_no):
    row = cur.execute("""
        SELECT id FROM karar_iddialari
        WHERE karar_no=? AND iddia_no=?
        LIMIT 1
    """, (karar_no, iddia_no)).fetchone()

    return row is not None


def kart_var_mi(cur, karar_no, iddia_no):
    row = cur.execute("""
        SELECT id FROM hukuki_kartlar
        WHERE karar_no=? AND iddia_no=?
        LIMIT 1
    """, (karar_no, iddia_no)).fetchone()

    return row is not None


def iddialari_kaydet(cur, karar_id, karar_no, data):
    sayi = 0

    for item in data.get("iddialar", []) or []:
        iddia_no = item.get("iddia_no") or 1

        try:
            iddia_no = int(iddia_no)
        except Exception:
            iddia_no = 1

        if iddia_var_mi(cur, karar_no, iddia_no):
            continue

        veri = {
            "karar_id": karar_id,
            "karar_no": karar_no,
            "iddia_no": iddia_no,
            "konu": temizle(item.get("konu")),
            "uzman_soru": temizle(item.get("uzman_soru")),
            "iddia_ozeti": temizle(item.get("iddia_ozeti")),
            "kurul_cevabi": temizle(item.get("kurul_cevabi")),
            "sonuc": temizle(item.get("sonuc")),
            "emsal_ilke": temizle(item.get("emsal_ilke")),
            "mevzuat": temizle(item.get("mevzuat")),
            "anahtar_kelime": temizle(item.get("anahtar_kelime")),
            "guven": temizle(item.get("guven")),
            "olusturma_tarihi": now(),
            "kurul_degerlendirmesi": temizle(item.get("kurul_cevabi")),
            "kaynak": "OpenAI",
            "iddia_turu": temizle(item.get("iddia_turu")),
            "tarih": now(),
        }

        guvenli_insert(cur, "karar_iddialari", veri)
        sayi += 1

    return sayi


def hukuki_kartlari_kaydet(cur, karar_no, data):
    sayi = 0

    for item in data.get("hukuki_kartlar", []) or []:
        iddia_no = item.get("iddia_no") or 1

        try:
            iddia_no = int(iddia_no)
        except Exception:
            iddia_no = 1

        if kart_var_mi(cur, karar_no, iddia_no):
            continue

        veri = {
            "karar_no": karar_no,
            "iddia_no": iddia_no,
            "baslik": temizle(item.get("baslik")),
            "hukuki_soru": temizle(item.get("hukuki_soru")),
            "kurul_degerlendirmesi": temizle(item.get("kurul_degerlendirmesi")),
            "sonuc": temizle(item.get("sonuc")),
            "emsal_ilke": temizle(item.get("emsal_ilke")),
            "anahtar_kelime": temizle(item.get("anahtar_kelime")),
            "kart_tarihi": datetime.now().strftime("%Y-%m-%d"),
            "iddia_ozeti": temizle(item.get("iddia_ozeti")),
            "mevzuat": temizle(item.get("mevzuat")),
            "guven": temizle(item.get("guven")),
            "olusturma_tarihi": now(),
        }

        guvenli_insert(cur, "hukuki_kartlar", veri)
        sayi += 1

    return sayi


def main():
    print("=" * 80)
    print("128 - KİK KARAR AI OPENAI TOPLU İŞLEME ORKESTRATÖRÜ")
    print("=" * 80)
    print(f"PDF klasörü : {PDF_DIR}")
    print(f"DB          : {DB_PATH}")
    print(f"Model       : {MODEL}")
    print(f"Limit       : {LIMIT}")

    if not os.getenv("OPENAI_API_KEY"):
        print("HATA: OPENAI_API_KEY bulunamadı.")
        return

    pdfler = sorted(PDF_DIR.rglob("*.pdf"))

    print(f"Toplam PDF bulundu: {len(pdfler)}")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    islenen = 0
    atlanan = 0
    hatali = 0

    for pdf in pdfler:
        if islenen >= LIMIT:
            break

        dosya_adi = pdf.name

        try:
            if dosya_islenmis_mi(cur, dosya_adi):
                atlanan += 1
                continue

            print("\n" + "-" * 80)
            print(f"İşleniyor: {dosya_adi}")

            tam_metin = oku_pdf(pdf)

            if len(tam_metin) < 500:
                raise Exception("PDF metni çok kısa veya okunamadı.")

            data = openai_analiz_et(tam_metin, dosya_adi)

            karar_id, karar_no = karar_kaydet(cur, dosya_adi, tam_metin, data)
            iddia_sayisi = iddialari_kaydet(cur, karar_id, karar_no, data)
            kart_sayisi = hukuki_kartlari_kaydet(cur, karar_no, data)

            con.commit()

            islenen += 1

            print(f"OK | Karar No: {karar_no} | İddia: {iddia_sayisi} | Kart: {kart_sayisi}")

            log_yaz([
                now(),
                dosya_adi,
                "OK",
                karar_no,
                iddia_sayisi,
                kart_sayisi,
                "",
            ])

            time.sleep(SLEEP_SECONDS)

        except Exception as e:
            con.rollback()
            hatali += 1

            hata = str(e)
            print(f"HATA: {dosya_adi} | {hata}")

            log_yaz([
                now(),
                dosya_adi,
                "HATA",
                "",
                0,
                0,
                hata + " | " + traceback.format_exc()[:1000],
            ])

    toplam_karar = cur.execute("SELECT COUNT(*) FROM kararlar").fetchone()[0]
    toplam_iddia = cur.execute("SELECT COUNT(*) FROM karar_iddialari").fetchone()[0]
    toplam_kart = cur.execute("SELECT COUNT(*) FROM hukuki_kartlar").fetchone()[0]

    con.close()

    print("\n" + "=" * 80)
    print("İŞLEM ÖZETİ")
    print("=" * 80)
    print(f"Yeni işlenen PDF : {islenen}")
    print(f"Atlanan PDF      : {atlanan}")
    print(f"Hatalı PDF       : {hatali}")
    print(f"Toplam karar     : {toplam_karar}")
    print(f"Toplam iddia     : {toplam_iddia}")
    print(f"Toplam kart      : {toplam_kart}")
    print(f"Log dosyası      : {LOG_CSV}")


if __name__ == "__main__":
    main()