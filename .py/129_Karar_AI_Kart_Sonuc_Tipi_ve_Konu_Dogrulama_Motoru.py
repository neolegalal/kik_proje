# -*- coding: utf-8 -*-

import os
import csv
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
DB_PATH = os.path.join(BASE_DIR, ".py", "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

os.makedirs(RAPOR_DIR, exist_ok=True)


KONU_TERIMLERI = {
    "aşırı düşük teklif": [
        "aşırı düşük", "sınır değer", "kanun 38", "4734 38",
        "tebliğ 45", "45.1", "analiz", "açıklama"
    ],
    "yaklaşık maliyet": [
        "yaklaşık maliyet", "maliyet hesabı", "maliyet hesap",
        "güncellen", "birim fiyat", "rayiç"
    ],
    "iş deneyim belgesi": [
        "iş deneyim", "benzer iş", "tek sözleşme", "teklif edilen bedelin"
    ],
    "benzer iş": [
        "benzer iş", "ihale konusu işe benzer", "benzerlik"
    ],
    "geçici teminat": [
        "geçici teminat"
    ],
    "kesin teminat": [
        "kesin teminat"
    ],
    "yeterlik kriteri": [
        "yeterlik", "yeterlilik", "idari şartname", "7. madde", "belge"
    ],
    "teknik şartname": [
        "teknik şartname", "teknik kriter", "teknik özellik"
    ],
    "iş ortaklığı": [
        "iş ortaklığı", "ortak girişim", "pilot ortak", "özel ortak"
    ],
    "birden fazla teklif verme": [
        "birden fazla teklif", "17/d", "birlikte hareket"
    ],
    "yasaklama": [
        "yasaklama", "yasaklı", "ihalelere katılmaktan yasak"
    ],
}


def norm(x):
    return (x or "").lower().replace("ı", "ı").strip()


def add_column_if_missing(cur, table, column, col_type="TEXT"):
    cols = [r[1] for r in cur.execute(f"PRAGMA table_info({table})").fetchall()]
    if column not in cols:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        return True
    return False


def sonuc_tipi_belirle(sonuc, kurul_degerlendirmesi, emsal_ilke):
    text = norm(" ".join([sonuc or "", kurul_degerlendirmesi or "", emsal_ilke or ""]))

    if any(k in text for k in [
        "başvurusunun reddine",
        "itirazen şikayet başvurusunun reddine",
        "itirazen şikâyet başvurusunun reddine",
        "iddiası reddedilmiştir",
        "iddia reddedilmiştir",
        "iddiası yerinde görülmemiştir",
        "uygun bulunmadığına",
        "uygun bulunmamıştır",
        "mevzuata uygundur",
        "hukuka uygundur",
        "yerinde olmadığı"
    ]):
        return "RET"

    if any(k in text for k in [
        "düzeltici işlem belirlenmesine",
        "düzeltici işlem",
        "yeniden gerçekleştirilmesi gerekmektedir",
        "yeniden hesaplanması",
        "tekliflerin yeniden değerlendirilmesi"
    ]):
        return "DÜZELTİCİ İŞLEM"

    if any(k in text for k in [
        "ihalenin iptaline",
        "ihale işlemlerinin iptaline",
        "iptaline karar",
        "iptal sonucu"
    ]):
        return "İPTAL"

    if any(k in text for k in [
        "iddiası yerinde bulunmuştur",
        "iddiasının yerinde olduğu",
        "haklı bulunduğu",
        "başvuru sahibinin iddiasının tamamında haklı"
    ]):
        return "KABUL"

    return "BELİRSİZ"


def konu_dogrula(anahtar_kelime, hukuki_soru, baslik, sonuc, emsal_ilke, kurul_degerlendirmesi):
    konu = norm(anahtar_kelime)
    text = norm(" ".join([
        hukuki_soru or "",
        baslik or "",
        sonuc or "",
        emsal_ilke or "",
        kurul_degerlendirmesi or ""
    ]))

    if not konu:
        return "KONU YOK", 0, "Anahtar kelime boş"

    # Birden fazla anahtar varsa ilk güçlü etiketi yakala
    aday_konular = []
    for k in KONU_TERIMLERI:
        if k in konu:
            aday_konular.append(k)

    if not aday_konular:
        return "KONTROL GEREKİR", 40, "Tanımlı konu listesinde yok"

    en_iyi_konu = aday_konular[0]
    terimler = KONU_TERIMLERI[en_iyi_konu]
    eslesen = [t for t in terimler if t in text]

    if len(eslesen) >= 2:
        return "DOĞRULANDI", 100, " / ".join(eslesen[:5])

    if len(eslesen) == 1:
        return "ZAYIF DOĞRULANDI", 65, eslesen[0]

    return "ŞÜPHELİ", 20, f"'{en_iyi_konu}' konusu metinle desteklenmiyor"


def eski_test_supheli_mi(karar_no, guven, konu_dogrulama, kalite_puani):
    karar_no = karar_no or ""

    # 2006 eski test kartlarında yüksek güven ama konu doğrulama düşükse özellikle şüpheli
    if karar_no.startswith("2006/") and konu_dogrulama in ("ŞÜPHELİ", "KONU YOK"):
        return "EVET"

    if karar_no.startswith("2006/") and (guven or "").lower() == "yüksek" and kalite_puani < 70:
        return "EVET"

    return "HAYIR"


def main():
    print("=" * 80)
    print("129 - KİK KARAR AI KART SONUÇ TİPİ VE KONU DOĞRULAMA MOTORU")
    print("=" * 80)

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    added = []
    for col in [
        ("sonuc_tipi", "TEXT"),
        ("konu_dogrulama", "TEXT"),
        ("konu_kalite_puani", "INTEGER"),
        ("konu_dogrulama_notu", "TEXT"),
        ("supheli_kart", "TEXT"),
        ("duzeltme_tarihi", "TEXT"),
    ]:
        if add_column_if_missing(cur, "hukuki_kartlar", col[0], col[1]):
            added.append(col[0])

    if added:
        print("Eklenen sütunlar:", ", ".join(added))
    else:
        print("Yeni sütun eklenmedi; alanlar zaten var.")

    rows = cur.execute("""
        SELECT
            id,
            karar_no,
            iddia_no,
            baslik,
            hukuki_soru,
            kurul_degerlendirmesi,
            sonuc,
            emsal_ilke,
            anahtar_kelime,
            guven
        FROM hukuki_kartlar
        ORDER BY id
    """).fetchall()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rapor_rows = []
    toplam = len(rows)
    supheli = 0
    zayif = 0
    belirsiz_sonuc = 0

    for r in rows:
        (
            kart_id,
            karar_no,
            iddia_no,
            baslik,
            hukuki_soru,
            kurul_degerlendirmesi,
            sonuc,
            emsal_ilke,
            anahtar_kelime,
            guven,
        ) = r

        st = sonuc_tipi_belirle(sonuc, kurul_degerlendirmesi, emsal_ilke)
        kd, puan, notu = konu_dogrula(
            anahtar_kelime,
            hukuki_soru,
            baslik,
            sonuc,
            emsal_ilke,
            kurul_degerlendirmesi
        )
        sup = eski_test_supheli_mi(karar_no, guven, kd, puan)

        if sup == "EVET":
            supheli += 1
        if puan < 70:
            zayif += 1
        if st == "BELİRSİZ":
            belirsiz_sonuc += 1

        cur.execute("""
            UPDATE hukuki_kartlar
            SET
                sonuc_tipi=?,
                konu_dogrulama=?,
                konu_kalite_puani=?,
                konu_dogrulama_notu=?,
                supheli_kart=?,
                duzeltme_tarihi=?
            WHERE id=?
        """, (st, kd, puan, notu, sup, now, kart_id))

        if sup == "EVET" or puan < 70 or st == "BELİRSİZ":
            rapor_rows.append({
                "id": kart_id,
                "karar_no": karar_no,
                "iddia_no": iddia_no,
                "anahtar_kelime": anahtar_kelime,
                "guven": guven,
                "sonuc_tipi": st,
                "konu_dogrulama": kd,
                "konu_kalite_puani": puan,
                "supheli_kart": sup,
                "baslik": baslik,
                "hukuki_soru": hukuki_soru,
                "sonuc": sonuc,
                "emsal_ilke": emsal_ilke,
                "not": notu,
            })

    con.commit()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path = os.path.join(RAPOR_DIR, f"129_kart_sonuc_konu_dogrulama_raporu_{ts}.csv")
    txt_path = os.path.join(RAPOR_DIR, f"129_kart_sonuc_konu_dogrulama_ozet_{ts}.txt")

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = [
            "id", "karar_no", "iddia_no", "anahtar_kelime", "guven",
            "sonuc_tipi", "konu_dogrulama", "konu_kalite_puani",
            "supheli_kart", "baslik", "hukuki_soru", "sonuc",
            "emsal_ilke", "not"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rapor_rows)

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("129 - KİK KARAR AI KART SONUÇ TİPİ VE KONU DOĞRULAMA ÖZETİ\n")
        f.write("=" * 80 + "\n")
        f.write(f"Tarih                     : {now}\n")
        f.write(f"Toplam kart               : {toplam}\n")
        f.write(f"Şüpheli kart              : {supheli}\n")
        f.write(f"Konu kalite puanı < 70    : {zayif}\n")
        f.write(f"Sonuç tipi BELİRSİZ       : {belirsiz_sonuc}\n")
        f.write("\n")
        f.write(f"CSV rapor                 : {csv_path}\n")

    print("\n" + "-" * 80)
    print("İŞLEM ÖZETİ")
    print("-" * 80)
    print(f"Toplam kart             : {toplam}")
    print(f"Şüpheli kart            : {supheli}")
    print(f"Konu kalite puanı < 70  : {zayif}")
    print(f"Sonuç tipi BELİRSİZ     : {belirsiz_sonuc}")
    print("\nRaporlar oluşturuldu:")
    print(csv_path)
    print(txt_path)

    con.close()


if __name__ == "__main__":
    main()