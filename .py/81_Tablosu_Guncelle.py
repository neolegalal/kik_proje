import sqlite3

DB = "kik.db"

conn = sqlite3.connect(DB)
cursor = conn.cursor()

kolonlar = [
    "kurul_degerlendirmesi TEXT",
    "kaynak TEXT",
    "iddia_turu TEXT",
    "guven TEXT"
]

for kolon in kolonlar:
    try:
        cursor.execute(
            f"ALTER TABLE karar_iddialari ADD COLUMN {kolon}"
        )
        print("Eklendi:", kolon)

    except Exception as e:
        print("Zaten var:", kolon)

conn.commit()
conn.close()

print("TABLO GUNCELLENDI")