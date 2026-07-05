from openai import OpenAI

with open("api_key.txt", "r", encoding="utf-8") as f:
    api_key = f.read().strip()

client = OpenAI(api_key=api_key)