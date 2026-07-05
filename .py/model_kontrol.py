from openai import OpenAI

with open("api_key.txt","r",encoding="utf-8") as f:
    key=f.read().strip()


client=OpenAI(api_key=key)


models = client.models.list()


for m in models.data:
    print(m.id)