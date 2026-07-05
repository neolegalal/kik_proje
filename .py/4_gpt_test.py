# -*- coding: utf-8 -*-

"""
ADIM 4 (TEST): OpenAI - KİK karar analiz testi

Tek karar üzerinde:
- karar soru başlığı
- karar özeti
- karar sonucu
- kategori
- anahtar kelime

üretir.

Çalıştırma:
python 4_gpt_test.py
"""


import sqlite3
import json
import os


try:
    from openai import OpenAI

except ImportError:

    print("openai kütüphanesi yok.")
    print("Kurulum: python -m pip install openai")
    exit(1)



# =====================
# AYARLAR
# =====================


DB_DOSYASI = "./kik.db"

MODEL = "gpt-4o-mini"

TEST_ID = 5



# =====================
# API KEY
# =====================


if not os.path.exists("api_key.txt"):

    print("HATA: api_key.txt bulunamadı")
    exit(1)



with open(
    "api_key.txt",
    "r",
    encoding="utf-8"

) as f:

    API_KEY = f.read().strip()



# yanlışlıkla key: yazıldıysa temizle

API_KEY = API_KEY.replace(
    "key:",
    ""
).strip()



client = OpenAI(
    api_key=API_KEY
)



# =====================
# KATEGORİLER
# =====================


KATEGORILER = """

A01 İhaleye Katılım ve Yeterlik

A02 İş Deneyimi ve Mesleki Yeterlik

A03 Mali Yeterlik

A04 İhale Dokümanı ve Şartnameler

A05 İlan ve İhale Usulleri

A06 Teklif Hazırlama ve Sunulması

A07 Tekliflerin Değerlendirilmesi

A08 Aşırı Düşük Teklif

A09 Teminat İşlemleri

A10 Fiyat ve Maliyet

A11 EKAP ve Elektronik İhale

A12 Rekabet ve Temel İlkeler

A13 Şikayet ve Başvuru Süreçleri

A14 İhale İptali ve Sonlandırılması

A15 Yasaklılık

A16 Sözleşme Süreci

A17 Sözleşmenin Uygulanması

A18 Yapım İşleri

A19 Hizmet Alımları

A20 Mal Alımları

A21 Kamu Zararı

A22 Mahkeme Kararları

A23 İdari İşlemler

A24 Diğer

"""



# =====================
# SYSTEM
# =====================


SISTEM = """

Sen kamu ihale hukuku uzmanısın.

Kamu İhale Kurulu kararlarını analiz edip
hukuki veri tabanı için yapılandırılmış içerik hazırlıyorsun.

Sadece verilen karar metnini kullan.

Bilgi uydurma.

"""


# =====================
# PROMPT
# =====================


def prompt_olustur(metin):


    return f"""

Aşağıdaki Kamu İhale Kurulu kararını analiz et.

Sadece geçerli JSON döndür.

Başka açıklama yazma.


FORMAT:


{{

"ihale_ili":

"karar_soru_basligi":

"karar_ozeti":

"karar_sonuc_ozeti":

"ana_kategori":

"anahtar_kelimeler":

}}



KURALLAR:



karar_soru_basligi:


Kararın cevapladığı hukuki soruyu yaz.


Google'da hukukçu veya ihale uzmanının arayacağı şekilde olsun.


Örnek:

"İdare, Kamu İhale Kurulu düzeltici işlem kararını uygulamadan ihaleyi iptal edebilir mi?"


Genel ifadeler kullanma.






karar_ozeti:


Düz metin paragraf halinde yaz.


Şu sırayı takip et:


1- Başvuru sahibi

2- İhale konusu

3- Başvuru sebebi

4- Kurulun hukuki değerlendirmesi



Madde işareti kullanma.


Python sözlüğü oluşturma.






karar_sonuc_ozeti:


Şu şekilde başla:


"Kamu İhale Kurulu;"


Sonrasında karar sonucunu maddeler halinde yaz.


Son bölüm:


"Sonuç olarak:"


ile başlasın ve kararın pratik etkisini açıkla.






ana_kategori:


Aşağıdaki listeden en uygun 1-3 kategori seç:


{KATEGORILER}






anahtar_kelimeler:


5-8 adet kısa anahtar kelime yaz.

Virgülle ayır.





KARAR METNİ:


{metin}


"""



# =====================
# ANA PROGRAM
# =====================


def main():



    db = sqlite3.connect(
        DB_DOSYASI
    )


    db.row_factory = sqlite3.Row



    karar = db.execute(

        """

        SELECT

        karar_no,
        tam_metin

        FROM kararlar

        WHERE id=?


        """,

        (TEST_ID,)

    ).fetchone()



    if not karar:

        print("Karar bulunamadı.")
        return



    print("--------------------------------")

    print(
        "Test kararı:",
        karar["karar_no"]
    )


    metin = karar["tam_metin"]



    print(
        "Metin uzunluğu:",
        len(metin)
    )



    # token kontrolü

    metin = metin[:30000]



    print()

    print(
        "OpenAI çalışıyor..."
    )



    try:


        cevap = client.chat.completions.create(


            model=MODEL,


            messages=[


                {

                "role":"system",

                "content":SISTEM

                },


                {

                "role":"user",

                "content":prompt_olustur(metin)

                }


            ],


            temperature=0.2,


            response_format={

                "type":"json_object"

            }



        )



        sonuc = cevap.choices[0].message.content



        veri = json.loads(
            sonuc
        )



        print()

        print("="*70)



        print(
            "\n>>> KARAR SORU BAŞLIĞI <<<\n"
        )

        print(
            veri["karar_soru_basligi"]
        )



        print(
            "\n>>> KARAR ÖZETİ <<<\n"
        )

        print(
            veri["karar_ozeti"]
        )



        print(
            "\n>>> KARAR SONUCU <<<\n"
        )

        print(
            veri["karar_sonuc_ozeti"]
        )



        print(
            "\n>>> ANA KATEGORİ <<<\n"
        )

        print(
            veri["ana_kategori"]
        )



        print(
            "\n>>> ANAHTAR KELİMELER <<<\n"
        )

        print(
            veri["anahtar_kelimeler"]
        )


        print()

        print("="*70)



        print(
            "\nToken:"
        )

        print(
            cevap.usage
        )



    except Exception as e:


        print(
            "HATA:",
            e
        )



    db.close()



if __name__ == "__main__":

    main()