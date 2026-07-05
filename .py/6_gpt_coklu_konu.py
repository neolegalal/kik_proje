# -*- coding: utf-8 -*-

import sqlite3
import json
import os

from openai import OpenAI


DB = "./kik.db"
MODEL = "gpt-4o-mini"

TEST_ID = 5


with open("api_key.txt","r",encoding="utf-8") as f:
    API_KEY = f.read().strip()


client = OpenAI(api_key=API_KEY)



SISTEM = """
Sen kamu ihale hukuku uzmanısın.

Görevin KİK kararlarını veri tabanı için analiz etmektir.

Bir karar içinde birden fazla bağımsız hukuki mesele olabilir.
Her meseleyi ayrı çıkar.

Asla bilgi uydurma.
Sadece karar metnindeki bilgileri kullan.

Çıktıyı sadece JSON olarak ver.
"""




KATEGORI = """

A01 İhaleye Katılım ve Yeterlik

A02 İş Deneyimi ve Mesleki Yeterlik

A03 Mali Yeterlik ve Mali Durum

A04 İhale Dokümanı ve Şartnameler

A05 İlan ve İhale Usulleri

A06 Teklif Hazırlama ve Sunulması

A07 Tekliflerin Değerlendirilmesi

A08 Aşırı Düşük Teklifler

A09 Teminat İşlemleri

A10 Fiyat ve Maliyet Unsurları

A11 EKAP ve Elektronik Süreçler

A12 Rekabet ve Temel İlkeler

A13 Şikayet ve Başvuru Süreçleri

A14 İhale İptali ve Sonlandırılması

A15 Yasaklılık ve Yaptırımlar

A16 Sözleşme Süreci

A17 Sözleşmenin Uygulanması

A18 Yapım İşleri

A19 Hizmet Alımları

A20 Mal Alımları

A21 Kamu Zararı

A22 Mahkeme Kararları

A23 İdareler

A24 Diğer

"""




def prompt(metin):

    return f"""

Aşağıdaki KİK kararını analiz et.

Her ayrı hukuki konu için kayıt oluştur.

JSON:

{{
"konular":[

{{
"soru_basligi":"",
"karar_ozeti":"",
"karar_sonuc_ozeti":"",
"ana_kategori":"",
"alt_kategori":"",
"etiketler":[]
}}

]

}}


Kategori listesi:

{KATEGORI}


Karar:

{metin}

"""





def main():


    db = sqlite3.connect(DB)

    db.row_factory = sqlite3.Row



    karar = db.execute(
        """
        SELECT *
        FROM kararlar
        WHERE id=?
        """,
        (TEST_ID,)
    ).fetchone()



    if not karar:

        print("Karar bulunamadı")
        return



    print("-----------------------------")
    print("Karar:", karar["karar_no"])
    print("GPT analiz başlıyor...")
    print("-----------------------------")



    metin = karar["tam_metin"][:30000]



    cevap = client.chat.completions.create(

        model=MODEL,

        messages=[

        {
        "role":"system",
        "content":SISTEM
        },

        {
        "role":"user",
        "content":prompt(metin)
        }

        ],


        temperature=0.2,


        response_format={
        "type":"json_object"
        }

    )



    veri=json.loads(
        cevap.choices[0].message.content
    )



    konular=veri["konular"]



    for konu in konular:



        cursor=db.execute(

        """

        INSERT INTO karar_konulari

        (

        karar_id,

        soru_basligi,

        karar_ozeti,

        karar_sonucu,

        ana_kategori,

        alt_kategori,

        anahtar_kelimeler

        )

        VALUES (?,?,?,?,?,?,?)

        """,

        (

        karar["id"],

        konu["soru_basligi"],

        konu["karar_ozeti"],

        konu["karar_sonuc_ozeti"],

        konu["ana_kategori"],

        konu["alt_kategori"],

        ",".join(konu["etiketler"])

        )

        )



        konu_id=cursor.lastrowid



        for etiket in konu["etiketler"]:


            db.execute(

            """

            INSERT INTO arama_etiketleri

            (

            konu_id,

            etiket

            )

            VALUES (?,?)

            """,

            (

            konu_id,

            etiket

            )

            )




    db.commit()



    print("==============================")
    print("BAŞARILI")
    print("Eklenen konu:",len(konular))
    print("==============================")



    db.close()





if __name__=="__main__":

    main()