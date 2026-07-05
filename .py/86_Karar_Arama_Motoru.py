# -*- coding: utf-8 -*-

import sqlite3


DB="kik.db"



def skor_hesapla(metin, kelimeler):

    skor=0

    metin=metin.lower()


    for k in kelimeler:

        if k in metin:

            skor += 1


    return skor





def ara(cursor,soru):


    kelimeler=[

        x.lower()

        for x in soru.split()

        if len(x)>2

    ]



    kartlar=cursor.execute("""

    SELECT

    karar_no,
    baslik,
    hukuki_soru,
    kurul_degerlendirmesi,
    sonuc,
    emsal_ilke

    FROM hukuki_kartlar


    """).fetchall()



    sonuc=[]



    for kart in kartlar:


        metin=" ".join([

            str(kart[1]),
            str(kart[2]),
            str(kart[3]),
            str(kart[4]),
            str(kart[5])

        ])


        skor=skor_hesapla(

            metin,

            kelimeler

        )



        if skor>0:

            sonuc.append(

                (

                skor,

                kart

                )

            )



    sonuc.sort(

        key=lambda x:x[0],

        reverse=True

    )


    return [

        x[1]

        for x in sonuc[:10]

    ]





def main():


    print("="*70)

    print("KAMU IHALE KARAR AI - ARAMA MOTORU")

    print("="*70)



    conn=sqlite3.connect(DB)

    c=conn.cursor()



    while True:


        soru=input("\nHukuki soru (çıkış:q): ")



        if soru.lower()=="q":

            break



        cevap=ara(c,soru)



        print("\nSONUÇLAR\n")



        for i,k in enumerate(cevap,1):


            print("-"*70)

            print("SONUÇ:",i)

            print("Karar:",k[0])

            print("Konu:",k[1])

            print()

            print("Soru:")

            print(k[2])

            print()

            print("Kurul:")

            print(k[3])

            print()

            print("Sonuç:")

            print(k[4])

            print()

            print("Emsal:")

            print(k[5])



    conn.close()




if __name__=="__main__":

    main()