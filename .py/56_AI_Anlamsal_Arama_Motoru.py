import sqlite3
from openai import OpenAI
import json
import math


DB = "kik.db"



print("="*70)
print("KAMU IHALE KARAR AI - ANLAMSAL ARAMA MOTORU")
print("="*70)



# API

with open("api_key.txt","r",encoding="utf-8") as f:
    API_KEY=f.read().strip()



client=OpenAI(
    api_key=API_KEY
)



MODEL="text-embedding-3-small"



# =====================================================
# COSINE BENZERLIK
# =====================================================


def cosine_similarity(a,b):


    toplam=0

    a_norm=0

    b_norm=0



    for x,y in zip(a,b):

        toplam += x*y

        a_norm += x*x

        b_norm += y*y



    if a_norm==0 or b_norm==0:

        return 0



    return toplam/(math.sqrt(a_norm)*math.sqrt(b_norm))





# =====================================================
# SORU AL
# =====================================================


soru=input("\nHukuki sorunuzu yazınız: ")



# =====================================================
# SORU EMBEDDING
# =====================================================



response=client.embeddings.create(

    model=MODEL,

    input=soru

)



soru_vector=response.data[0].embedding





# =====================================================
# DATABASE
# =====================================================


conn=sqlite3.connect(DB)

cursor=conn.cursor()



cursor.execute("""

SELECT

karar_no,

metin,

embedding


FROM karar_embedding


""")



kayitlar=cursor.fetchall()



sonuclar=[]



for kayit in kayitlar:



    karar_no=kayit[0]


    embedding=json.loads(kayit[2])



    skor=cosine_similarity(

        soru_vector,

        embedding

    )



    sonuclar.append(

        (

        karar_no,

        skor,

        kayit[1]

        )

    )





# Büyükten küçüğe

sonuclar.sort(

    key=lambda x:x[1],

    reverse=True

)





print()

print("="*70)

print("EN BENZER EMSAL KARARLAR")

print("="*70)





for sonuc in sonuclar[:5]:


    print()

    print("-"*70)


    print("Karar No:")

    print(sonuc[0])


    print()

    print("Benzerlik:")

    print("%",round(sonuc[1]*100,2))



print()

print("="*70)

print("ANLAMSAL ARAMA TAMAMLANDI")

print("="*70)



conn.close()