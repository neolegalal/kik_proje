# -*- coding: utf-8 -*-

"""
ADIM 9
Veritabanındaki AI analiz sonuçlarını kontrol eder.
Web sitesine aktarılacak veri formatını gösterir.
"""

import sqlite3


DB = "kik.db"


def main():

    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row


    kararlar = db.execute("""
    SELECT id, karar_no, karar_tarihi, ihale_konusu
    FROM kararlar
    ORDER BY id
    """).fetchall()



    print("\n")
    print("="*80)
    print(" KAMU İHALE KARAR SİSTEMİ - VERİ KONTROL")
    print("="*80)



    for karar in kararlar:


        print("\n")
        print("#"*80)

        print("KARAR NO:")
        print(karar["karar_no"])


        if karar["ihale_konusu"]:
            print("İHALE KONUSU:")
            print(karar["ihale_konusu"])



        konular = db.execute("""
        SELECT *
        FROM karar_konulari
        WHERE karar_id=?
        """,
        (karar["id"],)
        ).fetchall()



        print("\nTOPLAM KONU:",len(konular))


        sayac=1


        for konu in konular:


            print("\n")
            print("-"*60)

            print("KONU",sayac)


            print("\nSORU BAŞLIĞI:")
            print(konu["soru_basligi"])



            print("\nANA KATEGORİ:")
            print(konu["ana_kategori"])



            print("\nALT KATEGORİ:")
            print(konu["alt_kategori"])



            print("\nKARAR ÖZETİ:")
            print(konu["karar_ozeti"][:800])


            print("\nKARAR SONUCU:")
            print(konu["karar_sonucu"][:500])



            etiketler=db.execute("""
            SELECT etiket
            FROM arama_etiketleri
            WHERE konu_id=?
            """,
            (konu["id"],)
            ).fetchall()


            print("\nETİKETLER:")

            print(
                ", ".join(
                    [x["etiket"] for x in etiketler]
                )
            )


            sayac+=1



    db.close()


    print("\n")
    print("="*80)
    print(" KONTROL TAMAMLANDI ")
    print("="*80)



if __name__=="__main__":
    main()