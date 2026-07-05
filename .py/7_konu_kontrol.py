import sqlite3


db = sqlite3.connect("./kik.db")

db.row_factory = sqlite3.Row


print("=== KARAR KONULARI ===")


rows = db.execute("""

SELECT 

k.karar_no,
c.soru_basligi,
c.ana_kategori,
c.alt_kategori,
c.anahtar_kelimeler

FROM karar_konulari c

JOIN kararlar k

ON k.id = c.karar_id


""").fetchall()



for r in rows:

    print("\n------------------")

    print("Karar:", r["karar_no"])

    print("Soru:", r["soru_basligi"])

    print("Kategori:", r["ana_kategori"])

    print("Alt:", r["alt_kategori"])

    print("Etiket:", r["anahtar_kelimeler"])



print("\nToplam konu:",len(rows))


db.close()