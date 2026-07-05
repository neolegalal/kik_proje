import sqlite3
import time
from datetime import datetime
from openai import OpenAI


# ==============================
# AYARLAR
# ==============================

DB = "kik.db"

MODEL = "gpt-5-mini"

# İlk test için:
LIMIT = 100

# Tamamı için:
# LIMIT = None


client = OpenAI(
    api_key=open("api_key.txt").read().strip()
)


# ==============================
# LOG
# ==============================

def log_yaz(mesaj):

    with open(
        "batch_log.txt",
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"{datetime.now()} | {mesaj}\n"
        )



# ==============================
# AI KARAR KARTI ÜRET
# ==============================

def ai_uret(karar_no, konu, ozet, sonuc):

    prompt = f"""

Sen bir Kamu İhale uzmanısın.

Aşağıdaki KİK kararını uzman karar kartına dönüştür.

Karar No:
{karar_no}


Konu:
{konu}


Özet:
{ozet}


Sonuç:
{sonuc}


Aşağıdaki formatta JSON üret:


{{
"soru_basligi":"",
"kisa_ozet":"",
"hukuki_sorun":"",
"gerekce":"",
"sonuc":"",
"emsal_ilke":"",
"mevzuat":"",
"anahtar_kelimeler":"",
"kategori":"",
"alt_kategori":"",
"arama_etiketleri":""
}}

"""


    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role":"system",
                "content":
                "Kamu ihale hukuku uzmanı gibi cevap ver."
            },

            {
                "role":"user",
                "content":prompt
            }
        ]

    )


    return response.choices[0].message.content



# ==============================
# JSON TEMİZLE
# ==============================

import json


def json_temizle(text):

    text=text.replace("```json","")
    text=text.replace("```","")

    return json.loads(text.strip())



# ==============================
# ANA MOTOR
# ==============================


print("="*70)

print(
"KAMU IHALE KARAR AI - 100 BIN BATCH MOTORU"
)

print("="*70)



conn = sqlite3.connect(DB)

cursor = conn.cursor()



# kararlar

cursor.execute("""

SELECT
id,
karar_no,
karar_soru_basligi,
karar_ozeti,
karar_sonuc_ozeti

FROM kararlar

""")


kararlar = cursor.fetchall()



# Daha önce işlenenler

cursor.execute("""

SELECT karar_no
FROM ai_karar_kartlari

""")


tamamlananlar = {

x[0]

for x in cursor.fetchall()

}



sayac = 0



for karar in kararlar:



    id = karar[0]
    karar_no = karar[1]
    konu = karar[2]
    ozet = karar[3]
    sonuc = karar[4]



    if karar_no in tamamlananlar:

        continue



    if LIMIT and sayac >= LIMIT:

        break



    print("\n")
    print("-"*70)

    print(
    "Analiz edilen karar:",
    karar_no
    )



    try:



        cevap = ai_uret(

            karar_no,
            konu,
            ozet,
            sonuc

        )


        data=json_temizle(cevap)



        cursor.execute("""

        INSERT INTO ai_karar_kartlari
        (

        karar_id,
        karar_no,
        soru_basligi,
        kisa_ozet,
        hukuki_sorun,
        gerekce,
        sonuc,
        emsal_ilke,
        mevzuat,
        anahtar_kelimeler,
        kategori,
        alt_kategori,
        arama_etiketleri,
        olusturma_tarihi

        )

        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)

        """,

        (

        id,
        karar_no,

        data.get("soru_basligi"),
        data.get("kisa_ozet"),
        data.get("hukuki_sorun"),
        data.get("gerekce"),
        data.get("sonuc"),
        data.get("emsal_ilke"),
        data.get("mevzuat"),
        data.get("anahtar_kelimeler"),
        data.get("kategori"),
        data.get("alt_kategori"),
        data.get("arama_etiketleri"),

        datetime.now().isoformat()

        ))



        conn.commit()



        print(
        "✓ KAYDEDİLDİ"
        )


        log_yaz(

        f"{karar_no} | OK"

        )


        sayac +=1



        time.sleep(1)




    except Exception as e:



        print(
        "HATA:",
        e
        )


        log_yaz(

        f"{karar_no} | HATA | {e}"

        )



print("\n")

print("="*70)

print(
"TOPLU AI KARAR İŞLEME TAMAMLANDI"
)

print(

"İşlenen yeni karar:",

sayac

)

print("="*70)



conn.close()