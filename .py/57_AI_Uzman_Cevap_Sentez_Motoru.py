import sqlite3
from openai import OpenAI
import json
import math



DB="kik.db"



print("="*70)
print("KAMU IHALE KARAR AI - UZMAN CEVAP SENTEZ MOTORU")
print("="*70)




# API

with open("api_key.txt","r",encoding="utf-8") as f:
    API_KEY=f.read().strip()



client=OpenAI(
    api_key=API_KEY
)



EMBED_MODEL="text-embedding-3-small"

CHAT_MODEL="gpt-5-mini"





# =====================================================
# COSINE
# =====================================================


def cosine_similarity(a,b):


    toplam=0

    a_norm=0

    b_norm=0



    for x,y in zip(a,b):

        toplam+=x*y

        a_norm+=x*x

        b_norm+=y*y



    return toplam/(math.sqrt(a_norm)*math.sqrt(b_norm))






# =====================================================
# SORU
# =====================================================


soru=input("\nHukuki sorunuzu yazınız: ")





# =====================================================
# SORU EMBEDDING
# =====================================================


res=client.embeddings.create(

model=EMBED_MODEL,

input=soru

)



soru_vector=res.data[0].embedding






# =====================================================
# BENZER KARARLARI BUL
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



kararlar=cursor.fetchall()



eslesenler=[]



for karar in kararlar:


    vector=json.loads(karar[2])


    skor=cosine_similarity(

        soru_vector,

        vector

    )


    eslesenler.append(

        (

        karar[0],

        skor,

        karar[1]

        )

    )





eslesenler.sort(

key=lambda x:x[1],

reverse=True

)





# ilk 3 karar

kaynaklar=eslesenler[:3]





# =====================================================
# GPT ICIN BAGLAM
# =====================================================



context=""


for k in kaynaklar:


    context+=f"""

KARAR NO:
{k[0]}

BENZERLIK:
%{round(k[1]*100,2)}

KARAR ICERIGI:

{k[2]}


---------------------

"""





prompt=f"""

Sen kamu ihale hukuku uzmanısın.

Aşağıdaki kullanıcı sorusunu KİK kararlarını dikkate alarak cevapla.


SORU:

{soru}



EMSAL KARARLAR:

{context}



Cevabı:

- hukuki
- sade
- uzman diliyle
- mevzuata dayalı

hazırla.


Sonunda:

"Dayanak Kararlar"

başlığı altında kullanılan kararları listele.


"""






# =====================================================
# AI CEVAP
# =====================================================


cevap=client.chat.completions.create(


model=CHAT_MODEL,


messages=[


{

"role":"system",

"content":"Kamu ihale hukuku uzmanısın."

},


{

"role":"user",

"content":prompt

}


]


)





sonuc=cevap.choices[0].message.content





print()

print("="*70)

print("UZMAN AI CEVABI")

print("="*70)


print()

print(sonuc)





conn.close()