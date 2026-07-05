import sqlite3


DB = "kik.db"


conn = sqlite3.connect(DB)
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_karar_kartlari (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    karar_id INTEGER,

    karar_no TEXT,


    soru_basligi TEXT,

    kisa_ozet TEXT,

    hukuki_sorun TEXT,


    gerekce TEXT,

    sonuc TEXT,


    emsal_ilke TEXT,


    mevzuat TEXT,


    anahtar_kelimeler TEXT,


    kategori TEXT,

    alt_kategori TEXT,


    arama_etiketleri TEXT,


    emsal_degeri TEXT,


    ai_soru TEXT,

    ai_cevap TEXT,


    olusturma_tarihi TEXT

)

""")


conn.commit()


print("AI karar kartı tablosu oluşturuldu.")


print(
cursor.execute(
"PRAGMA table_info(ai_karar_kartlari)"
).fetchall()
)


conn.close()