import sqlite3

DB = r"C:\Users\MSI\Desktop\kik_proje\.py\kik.db"

conn = sqlite3.connect(DB)
c = conn.cursor()


c.execute("""
CREATE TABLE IF NOT EXISTS ai_hazirlik
(
id INTEGER PRIMARY KEY AUTOINCREMENT,
karar_id INTEGER,

karar_no TEXT,

soru TEXT,
ozet TEXT,
sonuc TEXT,

kategori TEXT,

anahtar TEXT,

mevzuat TEXT,

FOREIGN KEY(karar_id)
REFERENCES karar_meta(id)

)
""")


conn.commit()

print("AI HAZIRLIK TABLOSU OLUŞTURULDU")

conn.close()
