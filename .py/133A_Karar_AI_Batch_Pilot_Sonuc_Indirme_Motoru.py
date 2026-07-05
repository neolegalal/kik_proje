# -*- coding: utf-8 -*-

import os
from pathlib import Path
from datetime import datetime
from openai import OpenAI

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
RAPOR_DIR = BASE_DIR / "raporlar"

BATCH_ID = "batch_6a38053017bc81908828bbe50acfd583"

client = OpenAI()


def main():
    print("=" * 80)
    print("133A - KİK KARAR AI BATCH PİLOT SONUÇ İNDİRME MOTORU")
    print("=" * 80)

    batch = client.batches.retrieve(BATCH_ID)

    print("\nBatch ID :", BATCH_ID)
    print("Durum    :", batch.status)
    print("Input    :", batch.input_file_id)

    output_file_id = getattr(batch, "output_file_id", None)
    error_file_id = getattr(batch, "error_file_id", None)

    if error_file_id:
        print("Error    :", error_file_id)

    if batch.status != "completed":
        print("\nBatch henüz tamamlanmamış. Önce 132A ile completed olduğunu doğrula.")
        return

    if not output_file_id:
        print("\nOutput file ID bulunamadı.")
        return

    print("Output   :", output_file_id)
    print("\nSonuç dosyası indiriliyor...")

    content = client.files.content(output_file_id)
    raw = content.read()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = RAPOR_DIR / f"133A_batch_sonuc_{ts}.jsonl"

    with open(out_path, "wb") as f:
        f.write(raw)

    try:
        text = raw.decode("utf-8", errors="replace")
        line_count = len([ln for ln in text.splitlines() if ln.strip()])
    except Exception:
        line_count = "Bilinmiyor"

    log_path = RAPOR_DIR / f"133A_batch_sonuc_indirme_log_{ts}.txt"

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("133A - BATCH PİLOT SONUÇ İNDİRME LOGU\n")
        f.write("=" * 80 + "\n")
        f.write(f"Tarih          : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"Batch ID       : {BATCH_ID}\n")
        f.write(f"Durum          : {batch.status}\n")
        f.write(f"Input File ID  : {batch.input_file_id}\n")
        f.write(f"Output File ID : {output_file_id}\n")
        if error_file_id:
            f.write(f"Error File ID  : {error_file_id}\n")
        f.write(f"Sonuç Dosyası  : {out_path}\n")
        f.write(f"Toplam Satır   : {line_count}\n")

    print("\nKaydedildi:")
    print(out_path)
    print("\nToplam satır:", line_count)

    print("\nLog:")
    print(log_path)

    print("\nTamamlandı.")


if __name__ == "__main__":
    main()