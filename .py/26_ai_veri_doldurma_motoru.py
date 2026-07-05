import sqlite3


print("="*70)
print(" AI VERİ DOLDURMA MOTORU")
print("="*70)


conn = sqlite3.connect(
r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"
)

c = conn.cursor()



# eski veriyi temizle
c.execute("DELETE FROM ai_hazirlik")



rows = c.execute("""

SELECT

kk.id,
k.karar_no,
kk.soru_basligi,
kk.karar_ozeti,
kk.karar_sonucu,
kk.ana_kategori,
kk.anahtar_kelimeler,
k.kanun_maddeleri


FROM karar_konulari kk

JOIN kararlar k

ON kk.karar_id = k.id


""").fetchall()



for r in rows:


    c.execute("""

    INSERT INTO ai_hazirlik
    (
    karar_id,
    karar_no,
    soru,
    ozet,
    sonuc,
    kategori,
    anahtar,
    mevzuat
    )


    VALUES
    (?,?,?,?,?,?,?,?)


    """,

    (
    r[0],
    r[1],
    r[2],
    r[3],
    r[4],
    r[5],
    r[6],
    r[7]
    )
    )



conn.commit()



print("AI HAZIRLIK VERİLERİ DOLDURULDU")

print(
"Toplam kayıt:",
c.execute(
"SELECT COUNT(*) FROM ai_hazirlik"
).fetchone()[0]
)



conn.close()