import sqlite3
from datetime import datetime


DB="kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - GUVENILIRLIK ANALIZ MOTORU")
print("="*70)


conn=sqlite3.connect(DB)
cursor=conn.cursor()



# kolon ekleme

kolonlar=[

("ai_guven_orani","TEXT"),
("ai_mevzuat_dayanak","TEXT"),
("ai_hukuki_dikkat","TEXT"),
("ai_emsal_gucu","TEXT")

]


for kolon,tur in kolonlar:

    try:

        cursor.execute(
        f"ALTER TABLE kararlar ADD COLUMN {kolon} {tur}"
        )

        print("Eklendi:",kolon)

    except:

        pass



cursor.execute("""
SELECT
id,
karar_no,
ai_soru_basligi,
ai_sonuc,
ai_emsal_ilke

FROM kararlar

WHERE ai_guven_orani IS NULL

""")


kayitlar=cursor.fetchall()


print()
print("Analiz edilecek:")
print(len(kayitlar))
print()



for id,karar_no,soru,sonuc,ilke in kayitlar:


    print("-"*60)
    print("Analiz:")
    print(karar_no)


    if not sonuc:
        continue



    # basit hukuk puanlama


    guven="Orta"


    if ilke and len(ilke)>100:

        guven="Yüksek"



    mevzuat=""


    metin=(sonuc+" "+str(ilke))


    if "4734" in metin:

        mevzuat+="4734 sayılı Kamu İhale Kanunu "


    if "38" in metin:

        mevzuat+="Madde 38 "


    if "17" in metin:

        mevzuat+="Madde 17 "


    dikkat=""

    if "ortak" in str(soru).lower():

        dikkat=(
        "Somut olayda ortaklık yapısı, temsil yetkisi "
        "ve teklif ilişkisi ayrıca değerlendirilmelidir."
        )


    elif "aşırı" in str(soru).lower():

        dikkat=(
        "Açıklamanın yeterliliği ihale konusu işin "
        "niteliğine göre incelenmelidir."
        )


    else:

        dikkat=(
        "Somut olayın şartları ve ilgili mevzuat birlikte "
        "değerlendirilmelidir."
        )



    emsal=""

    if guven=="Yüksek":

        emsal="Doğrudan emsal niteliğinde güçlü karar"

    else:

        emsal="Benzer konu içeren karar"



    cursor.execute("""

    UPDATE kararlar

    SET

    ai_guven_orani=?,
    ai_mevzuat_dayanak=?,
    ai_hukuki_dikkat=?,
    ai_emsal_gucu=?

    WHERE id=?


    """,

    (
    guven,
    mevzuat,
    dikkat,
    emsal,
    id

    ))



    print("Tamamlandı:",karar_no)



conn.commit()



print()
print("="*70)
print("GUVENILIRLIK ANALIZI TAMAMLANDI")
print()
print("İşlenen:")
print(len(kayitlar))
print("="*70)



conn.close()