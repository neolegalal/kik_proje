import sqlite3
import re


DB = "kik.db"

conn = sqlite3.connect(DB)
cursor = conn.cursor()


print("="*70)
print(" KAMU İHALE KARAR SİSTEMİ - META VERİ GELİŞTİRME MOTORU")
print("="*70)



kararlar = cursor.execute("""
SELECT 
id,
tam_metin,
idare_adi,
ihale_kayit_no
FROM kararlar
""").fetchall()



for k in kararlar:

    karar_id = k[0]
    metin = k[1] or ""
    idare_adi = k[2] or ""
    ikn = k[3] or ""


    print("Analiz:", karar_id)



    # ----------------------------
    # İDARE NORMALİZASYON
    # ----------------------------

    idare = idare_adi.strip()


    if "Belediyesi" in idare:
        idare = idare.replace(
            "Başkanlığı",
            ""
        ).strip()


    elif "Genel Müdürlüğü" in idare:
        idare = idare


    elif "Bakanlığı" in idare:
        idare = idare



    # ----------------------------
    # İHALE YILI
    # ----------------------------

    ihale_yili = ""

    if ikn:

        yil = re.search(
            r"(20\d{2})/",
            ikn
        )

        if yil:
            ihale_yili = yil.group(1)



    # ----------------------------
    # KANUN MADDELERİ
    # ----------------------------

    maddeler=[]


    bulunan = re.findall(
        r"4734 sayılı.*?Kanunu.*?(\d+)[’']?uncu",
        metin
    )


    for m in bulunan:

        madde="4734/"+m

        if madde not in maddeler:
            maddeler.append(madde)



    # alternatif yakalama

    for m in re.findall(
        r"4734 sayılı Kamu İhale Kanunu’nun (\d+)",
        metin
    ):

        madde="4734/"+m

        if madde not in maddeler:
            maddeler.append(madde)



    kanun = ", ".join(maddeler)



    # ----------------------------
    # GÜNCELLE
    # ----------------------------


    cursor.execute("""
    UPDATE kararlar

    SET

    idare=?,
    ihale_yili=?,
    kanun_maddeleri=?

    WHERE id=?

    """,
    (
    idare,
    ihale_yili,
    kanun,
    karar_id
    ))



conn.commit()


print()
print("="*70)
print(" META VERİ GELİŞTİRME TAMAMLANDI")
print("="*70)


conn.close()