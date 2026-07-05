import sqlite3
from openai import OpenAI
import json


# ==============================
# OPENAI API
# ==============================

client = OpenAI(
    api_key="BURAYA_API_KEY"
)


# ==============================
# DATABASE
# ==============================

conn = sqlite3.connect("kik.db")
cursor = conn.cursor()



# Yeni alanlar

alanlar = [

("ai_danisman_soru","TEXT"),
("ai_hukuki_konu_danisman","TEXT"),
("ai_arama_kelime_danisman","TEXT")

]


for alan,tip in alanlar:

    try:

        cursor.execute(
            f"ALTER TABLE kararlar ADD COLUMN {alan} {tip}"
        )

        print("Eklendi:",alan)


    except:
        pass



conn.commit()



# ==============================
# 69 VERİLERİNDEN DÖNÜŞÜM
# ==============================


cursor.execute("""

SELECT

id,
karar_no,
ai_soru_basligi,
ai_hukuki_sorun,
ai_kisa_ozet,
ai_sonuc,
ai_emsal_ilke


FROM kararlar


WHERE ai_danisman_soru IS NULL


""")


kararlar = cursor.fetchall()



print("="*70)
print("KAMU IHALE KARAR AI - UZMAN SORU DONUSUM MOTORU")
print("="*70)

print()

print("Dönüştürülecek:",len(kararlar))



for row in kararlar:


    id = row[0]
    karar_no = row[1]


    print("-"*60)

    print("Dönüştürülüyor:")
    print(karar_no)



    prompt=f"""

Sen kamu ihale hukuku uzmanısın.

Aşağıdaki karar analizini danışmanların arayacağı
hukuki soru formatına çevir.


ÖNEMLİ:

Karar başlığı üretme.

Uzmanın Google'a veya AI'a soracağı
gerçek hukuki soruyu üret.


Mevcut analiz:

Karar başlığı:
{row[2]}


Hukuki sorun:
{row[3]}


Özet:
{row[4]}


Sonuç:
{row[5]}


Emsal:
{row[6]}



SADECE JSON DÖN:

{{

"soru":
"Örneğin:
Aynı kişinin ortak olduğu iki şirket aynı ihaleye birlikte teklif verebilir mi?",


"konu":
"Hukuki konu",


"arama":
[
"kelime1",
"kelime2",
"kelime3"
]

}}

"""



    try:


        cevap = client.chat.completions.create(

            model="gpt-4.1-mini",

            messages=[

            {
            "role":"user",
            "content":prompt
            }

            ],

            temperature=0.1

        )


        veri=json.loads(
            cevap.choices[0].message.content
        )



        cursor.execute("""

        UPDATE kararlar

        SET


        ai_danisman_soru=?,

        ai_hukuki_konu_danisman=?,

        ai_arama_kelime_danisman=?


        WHERE id=?

        """,

        (

        veri.get("soru"),

        veri.get("konu"),

        json.dumps(
            veri.get("arama"),
            ensure_ascii=False
        ),

        id

        ))


        conn.commit()



        print(
        "Tamamlandı:",
        karar_no
        )



    except Exception as e:


        print("HATA:")
        print(e)





print()

print("="*70)

print("DANISMAN SORU DONUSUM TAMAMLANDI")

print("İşlenen:",len(kararlar))

print("="*70)



conn.close()