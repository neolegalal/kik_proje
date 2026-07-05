# -*- coding: utf-8 -*-

import os
from datetime import datetime
from openai import OpenAI

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

JSONL_PATH = r"C:\Users\MSI\Desktop\kik_proje\raporlar\130_supheli_kart_batch_pilot_20260621_182550.jsonl"

client = OpenAI()

def main():
    print("=" * 80)
    print("131 - KİK KARAR AI BATCH BAŞLATMA MOTORU")
    print("=" * 80)

    if not os.path.exists(JSONL_PATH):
        print("JSONL dosyası bulunamadı:")
        print(JSONL_PATH)
        return

    print("Yüklenecek JSONL:")
    print(JSONL_PATH)

    with open(JSONL_PATH, "rb") as f:
        uploaded_file = client.files.create(
            file=f,
            purpose="batch"
        )

    print("\nDosya yüklendi.")
    print("File ID:", uploaded_file.id)

    batch = client.batches.create(
        input_file_id=uploaded_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )

    print("\nBatch başlatıldı.")
    print("Batch ID:", batch.id)
    print("Durum   :", batch.status)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(RAPOR_DIR, f"131_batch_baslatma_log_{ts}.txt")

    with open(log_path, "w", encoding="utf-8") as out:
        out.write("131 - KİK KARAR AI BATCH BAŞLATMA LOGU\n")
        out.write("=" * 80 + "\n")
        out.write(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        out.write(f"JSONL: {JSONL_PATH}\n")
        out.write(f"File ID: {uploaded_file.id}\n")
        out.write(f"Batch ID: {batch.id}\n")
        out.write(f"Durum: {batch.status}\n")

    print("\nLog kaydedildi:")
    print(log_path)

if __name__ == "__main__":
    main()