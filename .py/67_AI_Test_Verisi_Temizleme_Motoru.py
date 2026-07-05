import sqlite3

DB = "kik.db"

print("="*70)
print("KAMU IHALE KARAR AI - TEST VERISI TEMIZLEME MOTORU")
print("="*70)


conn = sqlite3.connect(DB)
cursor = conn.cursor()


# Silinecek test kararları

test_kayitlari = [
    "2026/UY.II-1482",
    "2026/UY.II-1483",
    "2026/UY.II-1487",
    "2026/UY.II-1496",
    "2026/UY.II-1499"
]


print()
print("Silinecek test kayıtları:")
print()


for karar in test_kayitlari:

    cursor.execute(
        "SELECT COUNT(*) FROM kararlar WHERE karar_no=?",
        (karar,)
    )

    var = cursor.fetchone()[0]


    if var:

        cursor.execute(
            "DELETE FROM kararlar WHERE karar_no=?",
            (karar,)
        )

        print("Silindi:")
        print(karar)

    else:

        print("Bulunamadı:")
        print(karar)



conn.commit()



cursor.execute(
    "SELECT COUNT(*) FROM kararlar"
)

toplam = cursor.fetchone()[0]


conn.close()



print()
print("="*70)
print("TEMIZLEME TAMAMLANDI")
print()
print("Kalan gerçek karar:")
print(toplam)
print("="*70)