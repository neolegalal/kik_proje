import sqlite3
from datetime import datetime


DB = "kik.db"



print("="*70)
print("KAMU IHALE KARAR AI - 100 BIN URETIM BASLATMA MOTORU")
print("="*70)



conn = sqlite3.connect(DB)

cursor = conn.cursor()



# =====================================================
# DURUM TABLOSU
# =====================================================


cursor.execute("""

CREATE TABLE IF NOT EXISTS ai_uretim_log

(

id INTEGER PRIMARY KEY AUTOINCREMENT,

karar_id INTEGER,

karar_no TEXT,

durum TEXT,

tarih TEXT

)

""")



conn.commit()





# =====================================================
# TOPLAM KARAR
# =====================================================



cursor.execute("""

SELECT COUNT(*)

FROM kararlar

""")


toplam = cursor.fetchone()[0]





# =====================================================
# AI KARTI OLANLAR
# =====================================================


cursor.execute("""

SELECT COUNT(*)

FROM ai_karar_kartlari

""")


ai_sayisi = cursor.fetchone()[0]





bekleyen = toplam - ai_sayisi





print()

print("TOPLAM KARAR:")

print(toplam)


print()

print("AI KARTI OLAN:")

print(ai_sayisi)


print()

print("BEKLEYEN:")

print(bekleyen)





print()

print("="*70)

print("BEKLEYEN KARARLAR")

print("="*70)





if bekleyen == 0:


    print()

    print("✓ TÜM KARARLAR AI ÜRETİMDEN GEÇMİŞ")



else:



    cursor.execute("""

    SELECT

    id,

    karar_no

    FROM kararlar


    WHERE id NOT IN

    (

    SELECT karar_id

    FROM ai_karar_kartlari

    )


    """)



    liste = cursor.fetchall()



    for karar in liste:



        print()

        print("BEKLEYEN:")

        print(karar[1])



        cursor.execute("""

        INSERT INTO ai_uretim_log

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

        ))



    conn.commit()





print()

print("="*70)

print("100 BIN URETIM KONTROL TAMAMLANDI")

print("="*70)



conn.close()