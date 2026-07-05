# -*- coding: utf-8 -*-
import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY_DIR = BASE_DIR / ".py"
RAPOR_DIR = BASE_DIR / "raporlar"
DB_PATH = PY_DIR / "kik.db"

DB_WRITE = True  # Güvenli mod için False yapabilirsin

def latest_file(pattern: str) -> Path:
    files = list(RAPOR_DIR.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Dosya bulunamadı: {pattern}")
    return max(files, key=lambda p: p.stat().st_mtime)

def load_jsonl(path: Path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def table_columns(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]

def get_value(row, *names):
    for n in names:
        if n in row:
            return row[n]
    return None

def normalize_changes(item):
    """
    141 jsonl yapısı farklı isimlerle gelebilir diye esnek okur.
    Beklenen: karar_no + kart_no/id + degisiklikler veya alan bazlı eski/yeni.
    """
    karar_no = get_value(item, "karar_no", "Karar No", "karar")
    kart_no = get_value(item, "kart_no", "kart_sira", "sira", "kart_index", "Kart No")
    kart_id = get_value(item, "id", "kart_id", "db_id", "hukuki_kart_id")

    changes = get_value(item, "degisiklikler", "changes", "duzeltmeler")
    if isinstance(changes, dict):
        return karar_no, kart_no, kart_id, changes

    # Alternatif düz yapı
    possible_fields = [
        "sonuc_tipi", "sonuç_tipi",
        "sonuc", "sonuç",
        "emsal_ilke",
        "guven", "güven",
        "baslik", "başlık",
        "hukuki_soru",
        "anahtar",
        "mevzuat",
    ]

    out = {}
    for field in possible_fields:
        yeni = get_value(item, f"yeni_{field}", f"{field}_yeni")
        if yeni is not None:
            clean = field.replace("sonuç", "sonuc").replace("güven", "guven").replace("başlık", "baslik")
            out[clean] = yeni

    return karar_no, kart_no, kart_id, out

def find_card(cur, cols, karar_no, kart_no, kart_id):
    if kart_id and "id" in cols:
        cur.execute("SELECT * FROM hukuki_kartlar WHERE id=?", (kart_id,))
        return cur.fetchone()

    if karar_no and kart_no is not None:
        for sira_col in ["kart_no", "kart_sira", "sira", "iddia_no"]:
            if sira_col in cols and "karar_no" in cols:
                cur.execute(
                    f"SELECT * FROM hukuki_kartlar WHERE karar_no=? AND {sira_col}=?",
                    (karar_no, kart_no)
                )
                row = cur.fetchone()
                if row:
                    return row

    if karar_no and "karar_no" in cols:
        # Son çare: karar içindeki sıraya göre
        cur.execute("SELECT * FROM hukuki_kartlar WHERE karar_no=? ORDER BY rowid", (karar_no,))
        rows = cur.fetchall()
        try:
            idx = int(kart_no) - 1
            if 0 <= idx < len(rows):
                return rows[idx]
        except Exception:
            pass

    return None

def main():
    print("=" * 80)
    print("142 - BATCH VALIDATOR DÜZELTME DB UYGULAMA MOTORU")
    print("=" * 80)

    sim_path = latest_file("141_batch_duzeltme_simulasyon_ozet_*.jsonl")
    rows = load_jsonl(sim_path)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rapor_path = RAPOR_DIR / f"142_batch_validator_db_duzeltme_raporu_{ts}.txt"

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    cols = table_columns(cur, "hukuki_kartlar")
    backup_table = f"hukuki_kartlar_yedek_142_{ts}"

    uygulanacak = []
    bulunamadi = []
    degisiklik_sayisi = 0

    for item in rows:
        karar_no, kart_no, kart_id, changes = normalize_changes(item)
        if not changes:
            continue

        row = find_card(cur, cols, karar_no, kart_no, kart_id)
        if not row:
            bulunamadi.append(item)
            continue

        valid_changes = {}
        for k, v in changes.items():
            col = k.replace("sonuç", "sonuc").replace("güven", "guven").replace("başlık", "baslik")
            if col in cols:
                old = row[col]
                if str(old or "") != str(v or ""):
                    valid_changes[col] = v

        if valid_changes:
            uygulanacak.append({
                "rowid": row["id"] if "id" in cols else row["rowid"] if "rowid" in row.keys() else None,
                "karar_no": karar_no or row["karar_no"] if "karar_no" in cols else karar_no,
                "kart_no": kart_no,
                "changes": valid_changes
            })
            degisiklik_sayisi += len(valid_changes)

    if DB_WRITE and uygulanacak:
        cur.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM hukuki_kartlar")

        for u in uygulanacak:
            set_sql = ", ".join([f"{c}=?" for c in u["changes"].keys()])
            vals = list(u["changes"].values())

            if "id" in cols and u["rowid"] is not None:
                vals.append(u["rowid"])
                cur.execute(f"UPDATE hukuki_kartlar SET {set_sql} WHERE id=?", vals)
            else:
                raise RuntimeError("DB güncellemesi için id kolonu bulunamadı.")

        con.commit()

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("142 - BATCH VALIDATOR DÜZELTME DB UYGULAMA RAPORU\n")
        f.write("=" * 100 + "\n")
        f.write(f"Tarih       : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB          : {DB_PATH}\n")
        f.write(f"Simülasyon  : {sim_path}\n")
        f.write(f"DB yaz      : {DB_WRITE}\n")
        f.write(f"Yedek tablo : {backup_table if DB_WRITE and uygulanacak else 'YOK'}\n\n")
        f.write(f"Plan kayıt          : {len(rows)}\n")
        f.write(f"Uygulanan kart      : {len(uygulanacak)}\n")
        f.write(f"Değişiklik toplamı  : {degisiklik_sayisi}\n")
        f.write(f"Kart bulunamadı     : {len(bulunamadi)}\n\n")

        f.write("UYGULANAN DEĞİŞİKLİKLER\n")
        f.write("-" * 100 + "\n")
        for u in uygulanacak:
            f.write(f"Karar: {u['karar_no']} | Kart: {u['kart_no']} | ID: {u['rowid']}\n")
            for k, v in u["changes"].items():
                f.write(f"  - {k}: {v}\n")
            f.write("\n")

        if bulunamadi:
            f.write("\nBULUNAMAYAN KAYITLAR\n")
            f.write("-" * 100 + "\n")
            for b in bulunamadi:
                f.write(json.dumps(b, ensure_ascii=False) + "\n")

    con.close()

    print("\nDB DÜZELTME UYGULAMASI TAMAMLANDI")
    print("-" * 80)
    print(f"Plan kayıt          : {len(rows)}")
    print(f"Uygulanan kart      : {len(uygulanacak)}")
    print(f"Değişiklik toplamı  : {degisiklik_sayisi}")
    print(f"Kart bulunamadı     : {len(bulunamadi)}")
    print(f"DB yaz              : {DB_WRITE}")
    print(f"Yedek tablo         : {backup_table if DB_WRITE and uygulanacak else 'YOK'}")
    print("\nDosya:")
    print(rapor_path)

    if DB_WRITE:
        print("\nDB'ye yazıldı.")
    else:
        print("\nNOT: DB'ye yazılmadı.")

if __name__ == "__main__":
    main()