import sqlite3
from datetime import datetime


DB = "kik.db"


def temiz(text):
    if not text:
        return ""
    return text.strip()


def karar_getir(soru):

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    kelimeler = soru.lower().split()

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
    WHERE 
    """

    şartlar = []

    for k in kelimeler:
        şartlar.append("""
        (
        lower(baslik) LIKE ?
        OR lower(hukuki_soru) LIKE ?
        OR lower(anahtar_kelime) LIKE ?
        OR lower(emsal_ilke) LIKE ?
        )
        """)

    sorgu += " OR ".join(şartlar)

    params = []

    for k in kelimeler:
        arama = f"%{k}%"
        params.extend([
            arama,
            arama,
            arama,
            arama
        ])

    sorgu += """
    LIMIT 5
    """

    cursor.execute(sorgu, params)

    sonuc = cursor.fetchall()

    conn.close()

    return sonuc



def sentez_uret(soru, kararlar):

    print("\n")
    print("="*70)
    print("KAMU IHALE KARAR AI - HUKUKİ SENTEZ MOTORU")
    print("="*70)


    print("\nSORULAN KONU:")
    print(soru)


    if not kararlar:

        print("\nBu konuda eşleşen emsal karar bulunamadı.")
        return


    print("\n")
    print("EMSAL KARARLARIN BİRLİKTE ANALİZİ")
    print("-"*70)


    ilkeler = []


    for i,k in enumerate(kararlar,1):

        karar_no, konu, soru, kurul, sonuc, ilke, guven = k


        print(f"""

{i}. KARAR
----------------------------------------

Karar No:
{karar_no}

Hukuki Konu:
{temiz(konu)}

Hukuki Sorun:
{temiz(soru)}

KİK Yaklaşımı:
{temiz(kurul)}

Sonuç:
{temiz(sonuc)}

Emsal İlke:
{temiz(ilke)}

Güven:
{temiz(guven)}

----------------------------------------
""")


        if ilke:
            ilkeler.append(ilke)



    print("\n")
    print("="*70)
    print("HUKUKİ SENTEZ")
    print("="*70)


    print(f"""

Kamu İhale Kurulu kararları birlikte değerlendirildiğinde;

"{soru}"

konusunda Kurul uygulamasında;

- isteklilerin davranışları,
- teklif verme yöntemi,
- ihale dokümanı hükümleri,
- ilgili mevzuat düzenlemeleri,
- önceki Kurul kararları

birlikte değerlendirilmektedir.


ORTAK EMSAL YAKLAŞIM:


""")


    for i in set(ilkeler):

        print("- " + i)


    print("""
Sonuç olarak benzer uyuşmazlıklarda,
öncelikle somut olayın özellikleri ile
Kurul'un önceki kararlarında ortaya koyduğu
hukuki yaklaşım birlikte değerlendirilmelidir.


Bu çıktı emsal karar destekli yapay zeka hukuki sentez analizidir.
""")


    print("="*70)



def main():

    while True:

        soru=input(
        "\nHukuki soru (çıkış:q): "
        )


        if soru.lower()=="q":
            break


        kararlar = karar_getir(soru)


        sentez_uret(
            soru,
            kararlar
        )



if __name__=="__main__":
    main()