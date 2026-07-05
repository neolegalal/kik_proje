# -*- coding: utf-8 -*-

import os
from datetime import datetime
from openai import OpenAI

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")

JSONL_PATH = r"C:\Users\MSI\Desktop\kik_proje\raporlar\130A_batch_pilot_karsilastirma_20260621_183517.jsonl"

client = OpenAI()


def main():

    print("=" * 80)
    print("131A - KİK KARAR AI BATCH PİLOT BAŞLATMA MOTORU")
    print("=" * 80)

    if not os.path.exists(JSONL_PATH):
        print("JSONL bulunamadı:")
        print(JSONL_PATH)
        return

    print("\nJSONL bulundu:")
    print(JSONL_PATH)

    print("\n1) Dosya yükleniyor...")

    with open(JSONL_PATH, "rb") as f:
        uploaded = client.files.create(
            file=f,
            purpose="batch"
        )

    print("Dosya yüklendi.")
    print("File ID :", uploaded.id)

    print("\n2) Batch oluşturuluyor...")

    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )

    print("\nBATCH BAŞLATILDI")
    print("-" * 80)
    print("Batch ID :", batch.id)
    print("Durum    :", batch.status)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    log_file = os.path.join(
        RAPOR_DIR,
        f"131A_batch_baslatma_{ts}.txt"
    )

    with open(log_file, "w", encoding="utf-8") as f:

        f.write("131A BATCH PİLOT BAŞLATMA\n")
        f.write("=" * 80 + "\n")
        f.write(f"Tarih     : {datetime.now()}\n")
        f.write(f"JSONL     : {JSONL_PATH}\n")
        f.write(f"FILE_ID   : {uploaded.id}\n")
        f.write(f"BATCH_ID  : {batch.id}\n")
        f.write(f"STATUS    : {batch.status}\n")

    print("\nLog:")
    print(log_file)

    print("\nTamamlandı.")


if __name__ == "__main__":
    main()