import sqlite3
from datetime import datetime


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - 100 BIN ISLEME YONETIM MOTORU")
print("="*70)



conn = sqlite3.connect(DB)
cursor = conn.cursor()



# takip tablosu

cursor.execute("""

CREATE TABLE IF NOT EXISTS ai_isleme_log
(

id INTEGER PRIMARY KEY AUTOINCREMENT,

karar_id INTEGER,

karar_no TEXT,

durum TEXT,

tarih TEXT

)

""")



# toplam karar

cursor.execute("""

SELECT COUNT(*)

FROM kararlar

""")


toplam = cursor.fetchone()[0]



# işlenmiş kararlar


cursor.execute("""

SELECT COUNT(*)

FROM ai_karar_kartlari

""")


islenen = cursor.fetchone()[0]



bekleyen = toplam - islenen



print()

print("TOPLAM KARAR:")
print(toplam)


print()

print("AI KARTI OLAN:")
print(islenen)


print()

print("BEKLEYEN:")
print(bekleyen)



print()

print("="*70)
print("BEKLEYEN KARAR LİSTESİ")
print("="*70)



cursor.execute("""

SELECT

k.id,

k.karar_no

FROM kararlar k


LEFT JOIN ai_karar_kartlari a

ON k.id=a.karar_id


WHERE a.karar_id IS NULL


LIMIT 20

""")



bekleyenler = cursor.fetchall()



if not bekleyenler:

    print()

    print("✓ TÜM KARARLAR İŞLENMİŞ")


else:


    for karar in bekleyenler:


        print()

        print(
        "Bekleyen:",
        karar[1]
        )



        cursor.execute("""

        INSERT INTO ai_isleme_log

        (

        karar_id,

        karar_no,

        durum,

        tarih

        )

        VALUES (?,?,?,?)

        """,
        (

        karar[0],

        karar[1],

        "BEKLIYOR",

        datetime.now().isoformat()

        )
        )



conn.commit()
conn.close()



print()

print("="*70)

print("100 BIN ISLEME KONTROL TAMAMLANDI")

print("="*70)