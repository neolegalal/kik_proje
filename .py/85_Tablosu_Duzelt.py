import sqlite3


DB = "kik.db"


conn = sqlite3.connect(DB)
c = conn.cursor()


kolonlar = [

    ("iddia_no","INTEGER"),
    ("iddia_ozeti","TEXT"),
    ("kurul_degerlendirmesi","TEXT"),
    ("mevzuat","TEXT"),
    ("anahtar_kelime","TEXT"),
    ("guven","TEXT"),
    ("olusturma_tarihi","TEXT")

]


mevcut = [

row[1] 

for row in c.execute(
"PRAGMA table_info(hukuki_kartlar)"
).fetchall()

]


for kolon, tip in kolonlar:

    if kolon not in mevcut:

        c.execute(
        f"""
        ALTER TABLE hukuki_kartlar
        ADD COLUMN {kolon} {tip}
        """
        )

        print("Eklendi:", kolon)

    else:

        print("Zaten var:", kolon)



conn.commit()

conn.close()


print("TABLO GUNCELLENDI")