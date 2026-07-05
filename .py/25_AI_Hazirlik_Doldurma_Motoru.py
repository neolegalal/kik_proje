import sqlite3

DB = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"

conn = sqlite3.connect(DB)
c = conn.cursor()


# karar_meta + kararlar birleşimi
rows = c.execute("""
SELECT 
k.id,
k.karar_no,
km.kanun_maddeleri,
km.karar_sonucu
FROM kararlar k
JOIN karar_meta km
ON k.id = km.karar_id
""").fetchall()


for r in rows:

    karar_id = r[0]
    karar_no = r[1]
    mevzuat = r[2]
    sonuc = r[3]


    # örnek AI soru üretimi
    soru = "Bu kararda uyuşmazlık konusu nedir?"

    ozet = "Kamu ihale sürecinde başvuru sahibinin iddiaları ve idarenin işlemleri değerlendirilmiştir."

    kategori = "Genel İhale Uyuşmazlıkları"

    anahtar = "ihale, teklif, değerlendirme"


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
    VALUES (?,?,?,?,?,?,?,?)
    """,
    (
    karar_id,
    karar_no,
    soru,
    ozet,
    sonuc,
    kategori,
    anahtar,
    mevzuat
    ))


conn.commit()

print("AI HAZIRLIK VERİLERİ DOLDURULDU")

conn.close()