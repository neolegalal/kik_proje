import os
import sqlite3
from datetime import datetime

# =============================================================================
# 145 - MÜKERRER KART PASİFLEŞTİRME MOTORU
# =============================================================================

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

DB_YAZ = True

PASIFLESTIRILECEK_KARTLAR = [
    {
        "kart_id": 1832,
        "karar_no": "2026/UH.I-1044",
        "etiket": "YAN_KART_MUKERRER",
        "not": "1834 ile aynı hukuki eksende mükerrer. Kurul kararına itiraz niteliği ana ilkesi tekrar ediyor."
    },
    {
        "kart_id": 1834,
        "karar_no": "2026/UH.I-1044",
        "etiket": "YAN_KART_MUKERRER",
        "not": "1832 ile aynı hukuki eksende mükerrer. Aynı hukuki itiraz farklı istekli üzerinden tekrar kartlaştırılmış."
    },
]


def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def get_columns(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}


def ensure_column(cur, table, col_name, col_def):
    cols = get_columns(cur, table)
    if col_name not in cols:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
        return True
    return False


def find_card(cur, kart_id):
    cur.execute("""
        SELECT *
        FROM hukuki_kartlar
        WHERE id = ?
    """, (kart_id,))
    row = cur.fetchone()
    return row


def main():
    print("=" * 80)
    print("145 - MÜKERRER KART PASİFLEŞTİRME MOTORU")
    print("=" * 80)

    ensure_dir(RAPOR_DIR)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rapor_path = os.path.join(
        RAPOR_DIR,
        f"145_mukerrer_kart_pasiflestirme_raporu_{ts}.txt"
    )

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    eklenen_kolonlar = []

    for col_name, col_def in [
        ("aktif", "INTEGER DEFAULT 1"),
        ("kalite_etiketi", "TEXT"),
        ("kalite_notu", "TEXT"),
    ]:
        if ensure_column(cur, "hukuki_kartlar", col_name, col_def):
            eklenen_kolonlar.append(col_name)

    yedek_tablo = f"hukuki_kartlar_yedek_145_{ts}"

    if DB_YAZ:
        cur.execute(f"""
            CREATE TABLE {yedek_tablo} AS
            SELECT *
            FROM hukuki_kartlar
        """)

    uygulanan = 0
    bulunamayan = 0
    detaylar = []

    for item in PASIFLESTIRILECEK_KARTLAR:
        kart_id = item["kart_id"]
        beklenen_karar_no = item["karar_no"]

        card = find_card(cur, kart_id)

        if not card:
            bulunamayan += 1
            detaylar.append(
                f"[BULUNAMADI] kart_id={kart_id} karar={beklenen_karar_no}"
            )
            continue

        mevcut_karar_no = card["karar_no"] if "karar_no" in card.keys() else None
        baslik = card["baslik"] if "baslik" in card.keys() else ""

        if mevcut_karar_no and mevcut_karar_no != beklenen_karar_no:
            detaylar.append(
                f"[UYARI] kart_id={kart_id} beklenen karar={beklenen_karar_no}, "
                f"DB karar={mevcut_karar_no}. Yine de ID eşleşmesi esas alınarak işlem yapıldı."
            )

        if DB_YAZ:
            cur.execute("""
                UPDATE hukuki_kartlar
                SET aktif = 0,
                    kalite_etiketi = ?,
                    kalite_notu = ?
                WHERE id = ?
            """, (
                item["etiket"],
                item["not"],
                kart_id
            ))

        uygulanan += 1

        detaylar.append(
            f"[PASIFLESTIRILDI] karar={mevcut_karar_no} kart_id={kart_id} "
            f"aktif=0 etiket={item['etiket']} | {baslik}"
        )

    if DB_YAZ:
        con.commit()
    else:
        con.rollback()

    cur.execute("SELECT COUNT(*) FROM hukuki_kartlar")
    toplam_kart = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM hukuki_kartlar WHERE COALESCE(aktif, 1) = 1")
    aktif_kart = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM hukuki_kartlar WHERE aktif = 0")
    pasif_kart = cur.fetchone()[0]

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("145 - MÜKERRER KART PASİFLEŞTİRME RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                 : {DB_PATH}\n")
        f.write(f"DB yaz             : {DB_YAZ}\n")
        f.write(f"Yedek tablo        : {yedek_tablo if DB_YAZ else 'YOK'}\n")
        f.write(f"Eklenen kolonlar   : {', '.join(eklenen_kolonlar) if eklenen_kolonlar else 'YOK'}\n")
        f.write(f"Plan kart          : {len(PASIFLESTIRILECEK_KARTLAR)}\n")
        f.write(f"Pasifleştirilen    : {uygulanan}\n")
        f.write(f"Kart bulunamadı    : {bulunamayan}\n")
        f.write(f"DB kart toplam     : {toplam_kart}\n")
        f.write(f"Aktif kart         : {aktif_kart}\n")
        f.write(f"Pasif kart         : {pasif_kart}\n\n")
        f.write("DETAYLAR\n")
        f.write("-" * 80 + "\n")
        for d in detaylar:
            f.write(d + "\n")

    con.close()

    print()
    print("PASİFLEŞTİRME TAMAMLANDI")
    print("-" * 80)
    print(f"Plan kart       : {len(PASIFLESTIRILECEK_KARTLAR)}")
    print(f"Pasifleştirilen : {uygulanan}")
    print(f"Kart bulunamadı : {bulunamayan}")
    print(f"Aktif kart      : {aktif_kart}")
    print(f"Pasif kart      : {pasif_kart}")
    print(f"Yedek tablo     : {yedek_tablo if DB_YAZ else 'YOK'}")
    print()
    print("Dosya:")
    print(rapor_path)


if __name__ == "__main__":
    main()