# -*- coding: utf-8 -*-
import os
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
DB_PATH = os.path.join(BASE_DIR, ".py", "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

DB_YAZ = True

DUZELTMELER = [
    {
        "kart_id": 1800,
        "karar_no": "2026/UD.I-1283",
        "sonuc_tipi": "KABUL",
        "guven": "Orta",
        "not": "RET/sonuç çelişkisi giderildi."
    },
    {
        "kart_id": 1804,
        "karar_no": "2026/UD.I-1284",
        "sonuc_tipi": "KABUL",
        "guven": "Orta",
        "not": "RET/itiraz yerindedir çelişkisi giderildi."
    },
    {
        "kart_id": 1805,
        "karar_no": "2026/UD.I-1284",
        "sonuc_tipi": "KABUL",
        "guven": "Orta",
        "not": "RET/talep yerindedir çelişkisi giderildi."
    },
    {
        "kart_id": 1806,
        "karar_no": "2026/UD.I-1284",
        "sonuc_tipi": "KABUL",
        "guven": "Orta",
        "not": "RET/talep yerindedir çelişkisi giderildi."
    },
]

PASIFLESTIR = [
    {
        "kart_id": 1832,
        "karar_no": "2026/UH.I-1044",
        "guven": "Orta",
        "etiket": "YAN_KART_MUKERRER",
        "not": "1834 ile aynı hukuki eksende mükerrer."
    },
    {
        "kart_id": 1834,
        "karar_no": "2026/UH.I-1044",
        "guven": "Orta",
        "etiket": "YAN_KART_MUKERRER",
        "not": "1832 ile aynı hukuki eksende mükerrer."
    },
    {
        "kart_id": 1853,
        "karar_no": "2026/UH.I-1053",
        "guven": "Orta",
        "etiket": "YAN_KART_MUKERRER",
        "not": "1854/ana aşırı düşük sorgulama kartı ile ilişkilidir."
    },
    {
        "kart_id": 1854,
        "karar_no": "2026/UH.I-1053",
        "guven": "Orta",
        "etiket": "YAN_KART_MUKERRER",
        "not": "1853 ile aynı ana ilkenin tekrarı niteliğinde."
    },
]

EMSAL_DUZELT = {
    1832: "Kurul kararlarına itiraz niteliğindeki başvurular Kurum tarafından yeniden incelenemez; bu tür iddialar ancak dava yoluyla ileri sürülebilir.",
    1834: "Kurul kararlarına itiraz niteliğindeki başvurular Kurum tarafından yeniden incelenemez; aynı hukuki itiraz farklı istekli üzerinden tekrar kartlaştırılmamalıdır.",
    1853: "Aşırı düşük teklif açıklamasında Tebliğ’de sayılan yöntemler esas alınır; önceki işlere ait hakediş raporu tek başına geçerli açıklama yöntemi olarak kabul edilemez.",
    1854: "Aşırı düşük teklif sorgulamasında önemli teklif bileşenleri açık, somut ve tüm istekliler bakımından eşit şekilde belirlenmelidir.",
}

def kolonlar(cur, tablo):
    cur.execute(f"PRAGMA table_info({tablo})")
    return [r[1] for r in cur.fetchall()]

def tablo_var_mi(cur, tablo):
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (tablo,)
    )
    return cur.fetchone() is not None

def kart_getir(cur, kart_id):
    cur.execute("SELECT * FROM hukuki_kartlar WHERE id=?", (kart_id,))
    return cur.fetchone()

def main():
    os.makedirs(RAPOR_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rapor_path = os.path.join(RAPOR_DIR, f"144_final_kart_duzeltme_raporu_{ts}.txt")

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cols = kolonlar(cur, "hukuki_kartlar")

    gerekli = ["id", "karar_no", "sonuc_tipi", "guven", "emsal_ilke"]
    eksik = [c for c in gerekli if c not in cols]
    if eksik:
        raise RuntimeError(f"hukuki_kartlar tablosunda eksik kolon var: {eksik}")

    # Yan/mükerrer işaretleme için kolon varsa kullanır; yoksa sadece rapora yazar.
    etiket_kolon = None
    for aday in ["validator_etiket", "kart_etiket", "etiket", "durum_notu"]:
        if aday in cols:
            etiket_kolon = aday
            break

    yedek_tablo = None
    if DB_YAZ:
        yedek_tablo = f"hukuki_kartlar_yedek_144_{ts}"
        cur.execute(f"CREATE TABLE {yedek_tablo} AS SELECT * FROM hukuki_kartlar")

    rapor = []
    rapor.append("144 - FINAL KART DÜZELTME MOTORU")
    rapor.append("=" * 80)
    rapor.append(f"Tarih       : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    rapor.append(f"DB          : {DB_PATH}")
    rapor.append(f"DB yaz      : {DB_YAZ}")
    rapor.append(f"Yedek tablo : {yedek_tablo if yedek_tablo else 'YOK'}")
    rapor.append(f"Etiket kolon: {etiket_kolon if etiket_kolon else 'YOK'}")
    rapor.append("")
    rapor.append("DETAYLAR")
    rapor.append("-" * 80)

    uygulanan = 0
    bulunamayan = 0

    # 1) Sonuç tipi / güven düzeltmeleri
    for d in DUZELTMELER:
        kart = kart_getir(cur, d["kart_id"])
        if not kart:
            bulunamayan += 1
            rapor.append(f"[BULUNAMADI] kart_id={d['kart_id']} karar={d['karar_no']}")
            continue

        eski_sonuc_tipi = kart["sonuc_tipi"]
        eski_guven = kart["guven"]

        rapor.append(
            f"[DUZELTME] karar={d['karar_no']} kart_id={d['kart_id']} "
            f"sonuc_tipi: {eski_sonuc_tipi} -> {d['sonuc_tipi']} | "
            f"guven: {eski_guven} -> {d['guven']} | {d['not']}"
        )

        if DB_YAZ:
            cur.execute(
                """
                UPDATE hukuki_kartlar
                SET sonuc_tipi=?, guven=?
                WHERE id=?
                """,
                (d["sonuc_tipi"], d["guven"], d["kart_id"])
            )
        uygulanan += 1

    # 2) Emsal ilke düzeltmeleri
    for kart_id, yeni_emsal in EMSAL_DUZELT.items():
        kart = kart_getir(cur, kart_id)
        if not kart:
            bulunamayan += 1
            rapor.append(f"[BULUNAMADI] emsal kart_id={kart_id}")
            continue

        eski_emsal = kart["emsal_ilke"]
        rapor.append("")
        rapor.append(f"[EMSAL] kart_id={kart_id}")
        rapor.append(f"Eski: {eski_emsal}")
        rapor.append(f"Yeni: {yeni_emsal}")

        if DB_YAZ:
            cur.execute(
                """
                UPDATE hukuki_kartlar
                SET emsal_ilke=?
                WHERE id=?
                """,
                (yeni_emsal, kart_id)
            )
        uygulanan += 1

    # 3) Mükerrer / yan kart işaretleme
    for p in PASIFLESTIR:
        kart = kart_getir(cur, p["kart_id"])
        if not kart:
            bulunamayan += 1
            rapor.append(f"[BULUNAMADI] pasif kart_id={p['kart_id']} karar={p['karar_no']}")
            continue

        rapor.append("")
        rapor.append(
            f"[MUKERRER_ISARET] karar={p['karar_no']} kart_id={p['kart_id']} "
            f"etiket={p['etiket']} | {p['not']}"
        )

        if DB_YAZ:
            if etiket_kolon:
                cur.execute(
                    f"""
                    UPDATE hukuki_kartlar
                    SET guven=?, {etiket_kolon}=?
                    WHERE id=?
                    """,
                    (p["guven"], p["etiket"], p["kart_id"])
                )
            else:
                cur.execute(
                    """
                    UPDATE hukuki_kartlar
                    SET guven=?
                    WHERE id=?
                    """,
                    (p["guven"], p["kart_id"])
                )
        uygulanan += 1

    if DB_YAZ:
        con.commit()

    rapor.insert(8, f"Uygulanan işlem : {uygulanan}")
    rapor.insert(9, f"Kart bulunamadı : {bulunamayan}")

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("\n".join(rapor))

    print("=" * 80)
    print("144 - FINAL KART DÜZELTME MOTORU")
    print("=" * 80)
    print()
    print("FINAL DÜZELTME TAMAMLANDI")
    print("-" * 80)
    print(f"Uygulanan işlem : {uygulanan}")
    print(f"Kart bulunamadı : {bulunamayan}")
    print(f"DB yaz          : {DB_YAZ}")
    print(f"Yedek tablo     : {yedek_tablo if yedek_tablo else 'YOK'}")
    print()
    print("Dosya:")
    print(rapor_path)

    con.close()

if __name__ == "__main__":
    main()