# -*- coding: utf-8 -*-
import os
import json
import sqlite3
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
DB_PATH = os.path.join(PY_DIR, "kik.db")

RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)

NEW_COLUMNS = {
    "konu_ozeti": "TEXT",
    "anahtar": "TEXT",
}


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def table_columns(cur, table):
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


def count_nonempty(cur, col):
    cur.execute(f"""
        SELECT COUNT(*)
        FROM hukuki_kartlar
        WHERE COALESCE(aktif,1)=1
          AND {col} IS NOT NULL
          AND TRIM({col}) <> ''
    """)
    return cur.fetchone()[0]


def main():
    print("=" * 80)
    print("167 - DB ŞEMA VE ÜRETİM FORMAT REVİZYONU")
    print("=" * 80)

    t = tag()

    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"DB bulunamadı: {DB_PATH}")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    before_cols = table_columns(cur, "hukuki_kartlar")

    backup_table = f"hukuki_kartlar_yedek_167_{t}"
    cur.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM hukuki_kartlar")

    added = []
    already = []

    for col, ddl in NEW_COLUMNS.items():
        if col not in before_cols:
            cur.execute(f"ALTER TABLE hukuki_kartlar ADD COLUMN {col} {ddl}")
            added.append(col)
        else:
            already.append(col)

    con.commit()

    after_cols = table_columns(cur, "hukuki_kartlar")

    cur.execute("SELECT COUNT(*) FROM hukuki_kartlar")
    total_cards = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM hukuki_kartlar WHERE COALESCE(aktif,1)=1")
    active_cards = cur.fetchone()[0]

    nonempty = {}
    for col in NEW_COLUMNS:
        if col in after_cols:
            nonempty[col] = count_nonempty(cur, col)
        else:
            nonempty[col] = None

    con.close()

    state = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "db_path": DB_PATH,
        "backup_table": backup_table,
        "before_columns": before_cols,
        "after_columns": after_cols,
        "added_columns": added,
        "already_columns": already,
        "total_cards": total_cards,
        "active_cards": active_cards,
        "nonempty": nonempty,
        "next_steps": [
            "158 üretim prompt/JSON formatına konu_ozeti ve anahtar alanları eklenecek.",
            "160 v3 importer konu_ozeti ve anahtar kolonlarını DB'ye yazacak şekilde güncellenecek.",
            "151 export konu_ozeti ve anahtar alanlarını dışarı aktaracak şekilde güncellenecek.",
            "Sonra küçük 5 karar test üretimi yapılacak.",
        ],
    }

    state_path = os.path.join(STATE_DIR, f"167_db_sema_revizyon_state_{t}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"167_db_sema_ve_uretim_format_revizyonu_raporu_{t}.txt")

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("167 - DB ŞEMA VE ÜRETİM FORMAT REVİZYONU RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                  : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"DB                     : {DB_PATH}\n")
        f.write(f"Yedek tablo             : {backup_table}\n\n")

        f.write("ŞEMA REVİZYONU\n")
        f.write("-" * 80 + "\n")
        f.write(f"Eklenen kolonlar        : {', '.join(added) if added else 'YOK'}\n")
        f.write(f"Zaten var olan kolonlar : {', '.join(already) if already else 'YOK'}\n\n")

        f.write("VERİ DURUMU\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam kart             : {total_cards}\n")
        f.write(f"Aktif kart              : {active_cards}\n")
        for col, val in nonempty.items():
            f.write(f"{col:25}: dolu={val}\n")

        f.write("\nSONUÇ\n")
        f.write("-" * 80 + "\n")
        f.write("✓ DB şeması Hedef 1 WEB ve Hedef 2 danışmanlık için gerekli yeni alanlara hazırlandı.\n")
        f.write("! Mevcut eski kartlarda bu alanlar doğal olarak boş olabilir.\n")
        f.write("! Bundan sonraki üretimde 158/160/151 zinciri bu alanları kullanacak şekilde güncellenmelidir.\n\n")

        f.write("SONRAKİ ADIMLAR\n")
        f.write("-" * 80 + "\n")
        for s in state["next_steps"]:
            f.write(f"- {s}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"State JSON              : {state_path}\n")
        f.write(f"Rapor                   : {rapor_path}\n")

    print("\n167 DB ŞEMA REVİZYONU TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam kart       : {total_cards}")
    print(f"Aktif kart        : {active_cards}")
    print(f"Eklenen kolonlar  : {', '.join(added) if added else 'YOK'}")
    print(f"Yedek tablo       : {backup_table}")
    print("\nDosya:")
    print(rapor_path)


if __name__ == "__main__":
    main()