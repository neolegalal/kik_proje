import sqlite3


DB = "kik.db"


conn = sqlite3.connect(DB)
cursor = conn.cursor()


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - İDARE NORMALİZASYON MOTORU")
print("="*70)



veriler = cursor.execute("""
SELECT
id,
idare
FROM kararlar
""").fetchall()



for kayit in veriler:

    karar_id = kayit[0]
    idare = kayit[1] or ""


    yeni_idare = idare



    # -----------------------------
    # İDARE STANDARTLAŞTIRMA
    # -----------------------------


    if "Devlet Su İşleri" in idare or "DSİ" in idare:

        yeni_idare = "Devlet Su İşleri (DSİ)"


    elif "Su ve Kanalizasyon" in idare:

        if "Muğla" in idare:

            yeni_idare = "Muğla Su ve Kanalizasyon İdaresi"


        elif "İstanbul" in idare:

            yeni_idare = "İSKİ Genel Müdürlüğü"


        else:

            yeni_idare = "Su ve Kanalizasyon İdaresi"



    elif "Ulaştırma" in idare:

        yeni_idare = "Ulaştırma ve Altyapı Bakanlığı"



    # -----------------------------
    # GÜNCELLE
    # -----------------------------


    cursor.execute("""

    UPDATE kararlar

    SET idare=?

    WHERE id=?

    """,
    (
    yeni_idare,
    karar_id
    ))



    print(
        idare,
        " ---> ",
        yeni_idare
    )



conn.commit()



print()
print("="*70)
print(" NORMALİZASYON TAMAMLANDI")
print("="*70)



conn.close()