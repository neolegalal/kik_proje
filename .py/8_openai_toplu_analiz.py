# -*- coding: utf-8 -*-

"""
ADIM 8
KİK kararlarını OpenAI ile toplu analiz eder.

Çıktı:
- karar_konulari
- arama_etiketleri

Her karar içinde birden fazla konu desteklenir.
"""

import sqlite3
import json
import os
from openai import OpenAI


DB = "kik.db"
MODEL = "gpt-4o-mini"


# API KEY
if not os.path.exists("api_key.txt"):
    print("api_key.txt yok")
    exit()

with open("api_key.txt","r",encoding="utf-8") as f:
    KEY=f.read().strip()


client = OpenAI(api_key=KEY)



KATEGORILER = """

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
A11 EKAP ve Elektronik İhale Süreçleri
A12 Rekabet ve Temel İlkeler
A13 Şikayet ve Başvuru Süreçleri
A14 İhale İptali ve Sonlandırılması
A15 Yasaklılık ve Yaptırımlar
A16 Sözleşme Süreci
A17 Sözleşmenin Uygulanması
A18 Yapım İşleri Özel Konuları
A19 Hizmet Alımları Özel Konuları
A20 Mal Alımları Özel Konuları
A21 Kamu Zararı ve Mali Sorumluluk
A22 Mahkeme ve Yargı Kararları
A23 İdareler ve Kurumsal Yapılar
A24 Diğer ve Özel Konular

"""


SISTEM = """

Sen kamu ihale hukuku uzmanısın.

Bir KİK kararını analiz edeceksin.

Önemli:
- Bir karar içinde birden fazla hukuki mesele olabilir.
- Her mesele için ayrı kayıt oluştur.
- Sadece karar metnine bağlı kal.
- Uydurma bilgi ekleme.

"""


def prompt(metin):

    return f"""

Aşağıdaki KİK kararını analiz et.

Her farklı hukuki mesele için ayrı nesne oluştur.

Sadece JSON döndür.

Format:

{{
"konular":[

{{
"soru_basligi":"",
"karar_ozeti":"",
"karar_sonucu":"",
"ana_kategori":"",
"alt_kategori":"",
"anahtar_kelimeler":""
}}

]

}}


Kategoriler:

{KATEGORILER}


Karar metni:

{metin}

"""



def main():

    db=sqlite3.connect(DB)
    db.row_factory=sqlite3.Row


    kararlar=db.execute("""
    SELECT id, karar_no, tam_metin
    FROM kararlar
    WHERE id NOT IN
    (
        SELECT DISTINCT karar_id
        FROM karar_konulari
    )
    """).fetchall()



    print("Analiz edilecek karar:",len(kararlar))


    for k in kararlar:

        print("\n===================")
        print("Karar:",k["karar_no"])


        metin=k["tam_metin"][:30000]


        cevap=client.chat.completions.create(

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


        konular=veri.get("konular",[])


        print("Bulunan konu:",len(konular))


        for konu in konular:


            cursor=db.execute("""

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

            VALUES(?,?,?,?,?,?,?)

            """,

            (

            k["id"],

            konu.get("soru_basligi",""),

            konu.get("karar_ozeti",""),

            konu.get("karar_sonucu",""),

            konu.get("ana_kategori",""),

            konu.get("alt_kategori",""),

            konu.get("anahtar_kelimeler","")

            ))



            konu_id=cursor.lastrowid



            etiketler = konu.get(
                "anahtar_kelimeler",
                ""
            )


            for etiket in etiketler.split(","):


                db.execute("""

                INSERT INTO arama_etiketleri
                (
                konu_id,
                etiket
                )

                VALUES(?,?)

                """,

                (
                konu_id,
                etiket.strip()
                ))



            print(
            "eklendi:",
            konu.get("soru_basligi")
            )


        db.commit()



    db.close()


    print("\n===================")
    print("TÜM ANALİZ TAMAMLANDI")
    print("===================")



if __name__=="__main__":
    main()