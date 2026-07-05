# -*- coding: utf-8 -*-

import os
import re
from pathlib import Path
from datetime import datetime
from openai import OpenAI

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
RAPOR_DIR = BASE_DIR / "raporlar"

client = OpenAI()

# Buraya batch id'yi sabit yazdım; log arama hatasını bypass ediyoruz.
BATCH_ID = "batch_6a38053017bc81908828bbe50acfd583"

print("=" * 80)
print("132A - KİK KARAR AI BATCH PİLOT DURUM KONTROL")
print("=" * 80)

batch = client.batches.retrieve(BATCH_ID)

print()
print("Batch ID:", BATCH_ID)
print("Durum   :", batch.status)
print("Input   :", batch.input_file_id)

if getattr(batch, "output_file_id", None):
    print("Output  :", batch.output_file_id)

if getattr(batch, "error_file_id", None):
    print("Error   :", batch.error_file_id)

rapor = RAPOR_DIR / f"132A_batch_durum_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

with open(rapor, "w", encoding="utf-8") as f:
    f.write("132A BATCH DURUM RAPORU\n")
    f.write("=" * 60 + "\n")
    f.write(f"Batch ID      : {BATCH_ID}\n")
    f.write(f"Durum         : {batch.status}\n")
    f.write(f"Input File ID : {batch.input_file_id}\n")
    if getattr(batch, "output_file_id", None):
        f.write(f"Output File ID: {batch.output_file_id}\n")
    if getattr(batch, "error_file_id", None):
        f.write(f"Error File ID : {batch.error_file_id}\n")

print()
print("Log oluşturuldu:")
print(rapor)