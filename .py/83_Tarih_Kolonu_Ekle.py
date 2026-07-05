import sqlite3

conn = sqlite3.connect("kik.db")
cursor = conn.cursor()

try:
    cursor.execute("""
    ALTER TABLE karar_iddialari 
    ADD COLUMN tarih TEXT
    """)

    print("tarih kolonu eklendi")

except Exception as e:
    print("Zaten var:", e)

conn.commit()
conn.close()

print("Tamamlandı")