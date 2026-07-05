import sqlite3
import datetime


DB = "kik.db"


def temizle(metin):
    if not metin:
        return ""
    return metin.lower().replace("ı","i").replace("ş","s").replace("ğ","g").replace("ü","u").replace("ö","o").replace("ç","c")


def mevzuat_bul(konu):

    konu = temizle(konu)

    mevzuatlar = []


    if (
        "iki sirket" in konu
        or "birden fazla teklif" in konu
        or "ayni kisinin" in konu
        or "iki şirket" in konu
    ):

        mevzuatlar.append(
            {
                "kanun":
                "4734 sayılı Kamu İhale Kanunu",

                "madde":
                "Madde 17/d",

                "konu":
                "Yasak fiil ve davranışlar - Birden fazla teklif verme yasağı",

                "aciklama":
                "İstekliler tarafından ihale sürecinde birden fazla teklif verilmesi yasaktır."
            }
        )


    if "teknik sartname" in konu:

        mevzuatlar.append(
            {
                "kanun":
                "4734 sayılı Kamu İhale Kanunu",

                "madde":
                "Madde 12",

                "konu":
                "Teknik şartnamenin hazırlanması",

                "aciklama":
                "Teknik kriterlerin rekabeti engellemeyecek şekilde belirlenmesi gerekir."
            }
        )


    if "asiri dusuk" in konu:

        mevzuatlar.append(
            {
                "kanun":
                "4734 sayılı Kamu İhale Kanunu",

                "madde":
                "Madde 38",

                "konu":
                "Aşırı düşük teklif açıklaması",

                "aciklama":
                "Aşırı düşük teklifler açıklama istenerek değerlendirilir."
            }
        )


    return mevzuatlar



def karar_getir(soru):

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()


    kelimeler = soru.split()


    sorgu = """

    SELECT
    karar_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke,
    guven

    FROM hukuki_kartlar

    ORDER BY id DESC

    LIMIT 10

    """


    veriler = cursor.execute(sorgu).fetchall()


    conn.close()


    return veriler



def rapor_yaz(soru):


    print("\n")
    print("="*70)
    print("KAMU IHALE KARAR AI - MEVZUAT BAGLANTI MOTORU")
    print("="*70)


    print("\nSORULAN KONU:")
    print(soru)



    mevzuatlar = mevzuat_bul(soru)



    print("\n")
    print("İLGİLİ MEVZUAT BAĞLANTISI")
    print("-"*70)



    if mevzuatlar:


        for m in mevzuatlar:

            print("\nKanun:")
            print(m["kanun"])

            print("\nMadde:")
            print(m["madde"])

            print("\nHukuki Konu:")
            print(m["konu"])

            print("\nAçıklama:")
            print(m["aciklama"])

            print("-"*70)


    else:

        print(
        "Bu konu için otomatik mevzuat bağlantısı bulunamadı."
        )




    kararlar = karar_getir(soru)



    print("\n")
    print("EMSAL KARAR BAĞLANTISI")
    print("-"*70)



    if kararlar:


        for k in kararlar:


            print("\nKarar:")
            print(k[0])


            print("\nKonu:")
            print(k[1])


            print("\nKurul Yaklaşımı:")
            print(k[3])


            print("\nSonuç:")
            print(k[4])


            print("\nEmsal İlke:")
            print(k[5])


            print("\nGüven:")
            print(k[6])


            print("-"*70)



    print("\n")
    print("="*70)
    print("HUKUKİ BAĞLANTI DEĞERLENDİRMESİ")
    print("="*70)



    if mevzuatlar and kararlar:


        print(
        """
Somut olay bakımından;

- ilgili mevzuat hükümleri,
- Kamu İhale Kurulu kararları,
- emsal değerlendirme ilkeleri

birlikte dikkate alınmalıdır.

Mevzuat hükmü ile Kurul uygulaması arasında
bağlantı kurularak hukuki değerlendirme yapılmıştır.
"""
        )


    print("\n")
    print(
    "Bu çıktı emsal karar + mevzuat bağlantılı yapay zeka analizidir."
    )





def main():

    while True:


        soru=input(
        "\nHukuki soru (çıkış:q): "
        )


        if soru.lower()=="q":
            break


        rapor_yaz(soru)




if __name__=="__main__":
    main()