# -*- coding: utf-8 -*-

import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(r"C:\Users\MSI\Desktop\kik_proje")
RAPOR_DIR = BASE_DIR / "raporlar"

SONUC_JSONL = RAPOR_DIR / "133A_batch_sonuc_20260621_184819.jsonl"


def main():
    print("=" * 80)
    print("134A - KİK KARAR AI BATCH PİLOT SONUÇ ÖN KONTROL MOTORU")
    print("=" * 80)

    if not SONUC_JSONL.exists():
        print("Sonuç JSONL bulunamadı:")
        print(SONUC_JSONL)
        return

    toplam_satir = 0
    basarili = 0
    hatali = 0
    toplam_kart = 0

    ornekler = []

    for line in SONUC_JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue

        toplam_satir += 1

        try:
            obj = json.loads(line)

            custom_id = obj.get("custom_id", "")
            error = obj.get("error")

            if error:
                hatali += 1
                ornekler.append((custom_id, "ERROR", str(error)[:500]))
                continue

            content = (
                obj.get("response", {})
                .get("body", {})
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
            )

            data = json.loads(content)
            kartlar = data.get("kartlar", [])

            basarili += 1
            toplam_kart += len(kartlar)

            if len(ornekler) < 5:
                ornekler.append((
                    custom_id,
                    data.get("karar_no", ""),
                    f"kart sayısı: {len(kartlar)}"
                ))

        except Exception as e:
            hatali += 1
            ornekler.append(("PARSE_HATA", "", str(e)[:500]))

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    rapor = RAPOR_DIR / f"134A_batch_on_kontrol_raporu_{ts}.txt"

    with open(rapor, "w", encoding="utf-8") as f:
        f.write("134A - BATCH PİLOT SONUÇ ÖN KONTROL RAPORU\n")
        f.write("=" * 80 + "\n")
        f.write(f"Tarih          : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"JSONL          : {SONUC_JSONL}\n")
        f.write(f"Toplam satır   : {toplam_satir}\n")
        f.write(f"Başarılı       : {basarili}\n")
        f.write(f"Hatalı         : {hatali}\n")
        f.write(f"Toplam kart    : {toplam_kart}\n")
        if basarili:
            f.write(f"Ortalama kart  : {round(toplam_kart / basarili, 2)}\n")
        f.write("\nÖRNEKLER\n")
        f.write("-" * 80 + "\n")
        for x in ornekler:
            f.write(str(x) + "\n")

    print("\nÖN KONTROL SONUCU")
    print("-" * 80)
    print(f"Toplam satır  : {toplam_satir}")
    print(f"Başarılı      : {basarili}")
    print(f"Hatalı        : {hatali}")
    print(f"Toplam kart   : {toplam_kart}")
    if basarili:
        print(f"Ortalama kart : {round(toplam_kart / basarili, 2)}")

    print("\nÖrnekler:")
    for x in ornekler:
        print(x)

    print("\nRapor:")
    print(rapor)


if __name__ == "__main__":
    main()