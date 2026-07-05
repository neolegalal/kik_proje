import sqlite3
from openai import OpenAI
from datetime import datetime
import time


DB = "kik.db"


print("="*70)
print("KAMU IHALE KARAR AI - API BATCH URETIM MOTORU")
print("="*70)



# =====================================================
# API BAGLANTISI
# =====================================================


with open("api_key.txt","r",encoding="utf-8") as f:
    API_KEY = f.read().strip()



client = OpenAI(
    api_key=API_KEY
)



MODEL = "gpt-5-mini"


BATCH_SIZE = 10



# =====================================================
# DATABASE
# =====================================================


conn = sqlite3.connect(DB)

cursor = conn.cursor()



# API log tablosu


cursor.execute("""

CREATE TABLE IF NOT EXISTS ai_api_log

(

id INTEGER PRIMARY KEY AUTOINCREMENT,

karar_no TEXT,

durum TEXT,

mesaj TEXT,

tarih TEXT

)

""")


conn.commit()



# =====================================================
# ISLENMEMIS KARARLARI BUL
# =====================================================


cursor.execute("""

SELECT

k.id,

k.karar_no,

k.tam_metin


FROM kararlar k


LEFT JOIN ai_karar_kartlari a

ON k.id = a.karar_id


WHERE a.karar_id IS NULL


LIMIT ?

""",(BATCH_SIZE,))



kararlar = cursor.fetchall()



print()

print("Bekleyen karar:")

print(len(kararlar))



if len(kararlar)==0:


    print()

    print("✓ İşlenecek yeni karar yok")

    conn.close()

    exit()



# =====================================================
# AI URETIM
# =====================================================


basarili = 0

hata = 0



for karar in kararlar:


    karar_id = karar[0]

    karar_no = karar[1]

    metin = karar[2] or ""



    print()

    print("-"*70)

    print("Analiz:", karar_no)



    try:



        prompt = f"""

Sen uzman Kamu İhale Hukuku danışmanısın.

Aşağıdaki KİK kararını analiz et.

JSON formatında cevap ver.


Alanlar:


soru_basligi

kisa_ozet

hukuki_sorun

gerekce

sonuc

emsal_ilke

mevzuat

anahtar_kelimeler

kategori

alt_kategori

emsal_degeri



Karar metni:


{metin[:15000]}


"""



        response = client.chat.completions.create(

            model=MODEL,


            messages=[

                {

                "role":"user",

                "content":prompt

                }

            ]

        )



        cevap = response.choices[0].message.content




        cursor.execute("""

        INSERT INTO ai_karar_kartlari

        (

        karar_id,

        karar_no,

        soru_basligi,

        kisa_ozet,

        ai_cevap,

        olusturma_tarihi

        )


        VALUES (?,?,?,?,?,?)

        """,

        (

        karar_id,

        karar_no,

        "AI Analizi",

        cevap[:2000],

        cevap,

        datetime.now().isoformat()

        ))





        cursor.execute("""

        INSERT INTO ai_api_log

        (

        karar_no,

        durum,

        mesaj,

        tarih

        )

        VALUES (?,?,?,?)

        """,

        (

        karar_no,

        "BASARILI",

        "AI karar kartı üretildi",

        datetime.now().isoformat()

        ))



        conn.commit()



        basarili +=1



        print("✓ AI KART OLUŞTU")




    except Exception as e:



        hata +=1



        print("HATA:")

        print(e)



        cursor.execute("""

        INSERT INTO ai_api_log

        (

        karar_no,

        durum,

        mesaj,

        tarih

        )

        VALUES (?,?,?,?)

        """,

        (

        karar_no,

        "HATA",

        str(e),

        datetime.now().isoformat()

        ))



        conn.commit()




    time.sleep(1)






conn.close()



print()

print("="*70)

print("API BATCH ÜRETİM TAMAMLANDI")

print()

print("Başarılı:",basarili)

print("Hata:",hata)

print("="*70)