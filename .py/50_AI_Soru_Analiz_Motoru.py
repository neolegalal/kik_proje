import sqlite3
import re


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - SORU ANALIZ MOTORU")
print("="*70)


soru = input("\nHukuki sorunuzu yazınız: ")


def kelimeleri_cikar(metin):

    temiz = re.sub(
        r"[^a-zA-ZçğıöşüÇĞİÖŞÜ0-9 ]",
        "",
        metin
    )

    kelimeler = temiz.lower().split()

    return list(set(kelimeler))


anahtarlar = kelimeleri_cikar(soru)


print("\nANALİZ SONUCU")
print("-"*70)


print("Soru:")
print(soru)


print("\nAnahtar Kelimeler:")

for k in anahtarlar:
    print("-", k)



conn = sqlite3.connect(DB)
cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_soru_log
(
id INTEGER PRIMARY KEY AUTOINCREMENT,
soru TEXT,
anahtar TEXT
)
""")


cursor.execute("""
INSERT INTO ai_soru_log
(soru,anahtar)
VALUES (?,?)
""",
(
soru,
",".join(anahtarlar)
))


conn.commit()

conn.close()


print("\n✓ Soru analiz edildi ve kaydedildi")