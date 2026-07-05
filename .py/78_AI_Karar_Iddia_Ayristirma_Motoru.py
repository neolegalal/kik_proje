import sqlite3
from datetime import datetime


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - IDDIA AYRISTIRMA MOTORU")
print("="*70)



conn = sqlite3.connect(DB)
cursor = conn.cursor()



# yeni tablo

cursor.execute("""
CREATE TABLE IF NOT EXISTS karar_iddialari (

id INTEGER PRIMARY KEY AUTOINCREMENT,

karar_id INTEGER,

karar_no TEXT,

iddia_no INTEGER,

konu TEXT,

uzman_soru TEXT,

iddia_ozeti TEXT,

kurul_cevabi TEXT,

sonuc TEXT,

emsal_ilke TEXT,

mevzuat TEXT,

anahtar_kelime TEXT,

guven TEXT,

olusturma_tarihi TEXT

)

""")


conn.commit()


print("\nTablo hazır: karar_iddialari")



# mevcut kolonları oku

cursor.execute("PRAGMA table_info(kararlar)")

kolonlar=[x[1] for x in cursor.fetchall()]



def kolon_bul(liste):

    for aranan in liste:

        for kolon in kolonlar:

            if aranan in kolon.lower():

                return kolon

    return None




id_col = kolon_bul(
[
"id"
]
)



karar_col = kolon_bul(
[
"karar_no",
"karar"
]
)



ozet_col = kolon_bul(
[
"kisa_ozet",
"ozet",
"summary"
]
)



sonuc_col = kolon_bul(
[
"sonuc"
]
)



emsal_col = kolon_bul(
[
"emsal"
]
)



kelime_col = kolon_bul(
[
"anahtar",
"kelime"
]
)



print("\nBulunan kolonlar")

print("ID:",id_col)

print("Karar:",karar_col)

print("Özet:",ozet_col)

print("Sonuç:",sonuc_col)

print("Emsal:",emsal_col)

print("Kelime:",kelime_col)




sql=f"""

SELECT

{id_col},
{karar_col},
{ozet_col},
{sonuc_col},
{emsal_col},
{kelime_col}

FROM kararlar


"""



kararlar=cursor.execute(sql).fetchall()



print("\nAnaliz edilecek karar:")

print(len(kararlar))



print()



def konu_cikar(metin):


    metin=str(metin).lower()


    konular=[]


    anahtarlar=[


        "aşırı düşük teklif",

        "geçici teminat",

        "kesin teminat",

        "iş deneyim",

        "ortak",

        "ortaklık",

        "aynı kişi",

        "şikayet",

        "itirazen",

        "başvuru",

        "belge",

        "teknik",

        "fiyat dışı unsur",

        "sözleşme",

        "yasak fiil",

        "ihale iptali"


    ]



    for kelime in anahtarlar:


        if kelime in metin:

            konular.append(kelime)



    if not konular:

        konular.append(
        "ihale değerlendirmesi"
        )


    return list(set(konular))




def soru_uret(konu):


    if konu=="aşırı düşük teklif":

        return "Aşırı düşük teklif açıklaması nasıl değerlendirilir?"



    if "teminat" in konu:

        return "Teminat hangi durumlarda gelir kaydedilir?"



    if "ortak" in konu:

        return "Aynı kişinin ortak olduğu şirketler aynı ihaleye teklif verebilir mi?"



    if "şikayet" in konu or "başvuru" in konu:

        return "İdari başvuru şartları ve süreleri nasıl değerlendirilir?"



    if "belge" in konu:

        return "İhale belgeleri mevzuata uygun nasıl değerlendirilir?"



    if "teknik" in konu:

        return "Teknik yeterlilik belgeleri nasıl değerlendirilir?"



    if "fiyat dışı" in konu:

        return "Fiyat dışı unsur kriterleri nasıl uygulanır?"



    if "iptal" in konu:

        return "İhale hangi durumlarda iptal edilebilir?"



    return "Bu kararın hukuki konusu nedir?"





# eski üretimleri temizle

cursor.execute(
"DELETE FROM karar_iddialari"
)

conn.commit()



toplam=0




for karar in kararlar:



    karar_id=karar[0]

    karar_no=karar[1]

    ozet=karar[2]

    sonuc=karar[3]

    emsal=karar[4]

    kelime=karar[5]



    analiz_metni = (

        str(ozet)

        +" "

        +str(kelime)

    )



    konular=konu_cikar(
        analiz_metni
    )



    sira=1



    for konu in konular:



        soru=soru_uret(konu)



        cursor.execute("""

        INSERT INTO karar_iddialari

        (

        karar_id,

        karar_no,

        iddia_no,

        konu,

        uzman_soru,

        iddia_ozeti,

        kurul_cevabi,

        sonuc,

        emsal_ilke,

        mevzuat,

        anahtar_kelime,

        guven,

        olusturma_tarihi

        )

        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)

        """,

        (

        karar_id,

        karar_no,

        sira,

        konu,

        soru,

        ozet,

        sonuc,

        sonuc,

        emsal,

        "4734 sayılı Kamu İhale Kanunu",

        kelime,

        "Yüksek",

        datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        ))



        sira+=1

        toplam+=1




    print(
        "Tamamlandı:",
        karar_no,
        "| Konu:",
        len(konular)
    )





conn.commit()



print()

print("="*70)

print("IDDIA AYRISTIRMA TAMAMLANDI")

print("="*70)


print("Karar sayısı:")

print(len(kararlar))


print("Üretilen hukuki soru kartı:")

print(toplam)


print("="*70)



conn.close()