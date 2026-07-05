# -*- coding: utf-8 -*-

import os
import json
import glob
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")


def latest_file(pattern):
    files = glob.glob(os.path.join(RAPOR_DIR, pattern))
    if not files:
        raise Exception(f"Dosya bulunamadı: {pattern}")
    return max(files, key=os.path.getmtime)


def load_jsonl(path):
    rows = []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            try:
                rows.append(json.loads(line))
            except:
                pass

    return rows


def card_title(card):
    return (
        card.get("baslik")
        or card.get("başlık")
        or "-"
    )


def card_question(card):
    return (
        card.get("hukuki_soru")
        or "-"
    )


def card_result(card):
    return (
        card.get("sonuc")
        or "-"
    )


def card_type(card):
    return (
        card.get("sonuc_tipi")
        or "-"
    )


def main():

    print("=" * 80)
    print("136F - GÜVENLİ SADELEME KONTROL RAPORU")
    print("=" * 80)

    source_file = latest_file(
        "136E_batch_guvenli_sadelesmis_*.jsonl"
    )

    rows = load_jsonl(source_file)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    txt_report = os.path.join(
        RAPOR_DIR,
        f"136F_guvenli_sadeleme_kontrol_{ts}.txt"
    )

    csv_report = os.path.join(
        RAPOR_DIR,
        f"136F_guvenli_sadeleme_ozet_{ts}.csv"
    )

    total_decisions = 0
    total_cards = 0
    total_risk = 0

    with open(txt_report, "w", encoding="utf-8") as rpt, \
         open(csv_report, "w", encoding="utf-8-sig") as csv:

        csv.write(
            "karar_no,kart_sayisi,riskli\n"
        )

        rpt.write("=" * 120 + "\n")
        rpt.write("136F GUVENLI SADELEME KONTROL RAPORU\n")
        rpt.write("=" * 120 + "\n\n")

        rpt.write(f"Kaynak Dosya : {source_file}\n\n")

        for row in rows:

            karar_no = row.get("karar_no", "")

            kartlar = row.get("kartlar", [])

            meta = row.get("meta", {})

            riskli = meta.get("riskli", False)

            total_decisions += 1
            total_cards += len(kartlar)

            if riskli:
                total_risk += 1

            csv.write(
                f'"{karar_no}",{len(kartlar)},{riskli}\n'
            )

            rpt.write("\n")
            rpt.write("=" * 120 + "\n")
            rpt.write(f"KARAR NO : {karar_no}\n")
            rpt.write(f"KART SAYISI : {len(kartlar)}\n")
            rpt.write(
                f"RISKLI : {'EVET' if riskli else 'HAYIR'}\n"
            )
            rpt.write("=" * 120 + "\n")

            for idx, card in enumerate(kartlar, start=1):

                rpt.write("\n")
                rpt.write(f"[KART {idx}]\n")
                rpt.write(
                    f"Başlık      : {card_title(card)}\n"
                )
                rpt.write(
                    f"Hukuki Soru : {card_question(card)}\n"
                )
                rpt.write(
                    f"Sonuç Tipi  : {card_type(card)}\n"
                )
                rpt.write(
                    f"Sonuç       : {card_result(card)}\n"
                )

        rpt.write("\n\n")
        rpt.write("=" * 120 + "\n")
        rpt.write("GENEL OZET\n")
        rpt.write("=" * 120 + "\n")

        rpt.write(
            f"Karar Sayısı : {total_decisions}\n"
        )

        rpt.write(
            f"Toplam Kart  : {total_cards}\n"
        )

        rpt.write(
            f"Riskli Karar : {total_risk}\n"
        )

    print()
    print("KONTROL RAPORU OLUŞTURULDU")
    print("-" * 80)
    print(f"Karar Sayısı : {total_decisions}")
    print(f"Toplam Kart  : {total_cards}")
    print(f"Riskli Karar : {total_risk}")
    print()
    print("Dosyalar:")
    print(txt_report)
    print(csv_report)
    print()
    print("NOT: DB'ye yazılmadı.")


if __name__ == "__main__":
    main()