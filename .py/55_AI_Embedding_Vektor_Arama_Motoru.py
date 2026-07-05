import sys
sys.stdout.reconfigure(encoding='utf-8')

import sqlite3
from openai import OpenAI
from datetime import datetime
import json


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - EMBEDDING VEKTOR ARAMA MOTORU")
print("="*70)



# API

with open("api_key.txt","r",encoding="utf-8") as f:
    API_KEY = f.read().strip()


client = OpenAI(
    api_key=API_KEY
)



MODEL = "text-embedding-3-small"



conn = sqlite3.connect(DB)

cursor = conn.cursor()



# =====================================================
# VEKTOR TABLOSU
# =====================================================


cursor.execute("""

CREATE TABLE IF NOT EXISTS karar_embedding


(

id INTEGER PRIMARY KEY AUTOINCREMENT,


karar_id INTEGER,


karar_no TEXT,


metin TEXT,


embedding TEXT,


olusturma_tarihi TEXT


)

""")


conn.commit()



# =====================================================
# AI KARTLARINI AL
# =====================================================


cursor.execute("""

SELECT

id,

karar_no,

kisa_ozet,

hukuki_sorun,

gerekce,

sonuc


FROM ai_karar_kartlari


WHERE id NOT IN

(

SELECT karar_id FROM karar_embedding

)

""")


kararlar = cursor.fetchall()



print()

print("Yeni embedding bekleyen:")

print(len(kararlar))



if len(kararlar)==0:


    print()

    print("✓ Tüm kararların vektörü mevcut")

    conn.close()

    exit()



basarili=0



for karar in kararlar:



    id = karar[0]

    karar_no = karar[1]


    metin = """

Soru:

{}

Hukuki Sorun:

{}

Gerekçe:

{}

Sonuç:

{}

""".format(

karar[2],

karar[3],

karar[4],

karar[5]

)



    print()

    print("-"*70)

    print("Embedding:",karar_no)



    try:



        response = client.embeddings.create(

            model=MODEL,

            input=metin

        )


        vector = response.data[0].embedding



        cursor.execute("""

        INSERT INTO karar_embedding

        (

        karar_id,

        karar_no,

        metin,

        embedding,

        olusturma_tarihi

        )

        VALUES (?,?,?,?,?)

        """,

        (

        id,

        karar_no,

        metin,

        json.dumps(vector),

        datetime.now().isoformat()

        ))



        conn.commit()



        basarili+=1



        print("✓ VEKTÖR OLUŞTU")



    except Exception as e:


        print("HATA:")

        print(e)




conn.close()



print()

print("="*70)

print("EMBEDDING TAMAMLANDI")

print()

print("Başarılı:",basarili)

print("="*70)