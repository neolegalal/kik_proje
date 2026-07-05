# -*- coding: utf-8 -*-
import os
import re
import json
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

SCRIPT_136E = os.path.join(PY_DIR, "136E_Batch_Guvenli_Sadeleme_Motoru.py")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def find_lines(code, patterns):
    results = []
    lines = code.splitlines()
    for i, line in enumerate(lines, start=1):
        for p in patterns:
            if re.search(p, line, re.IGNORECASE):
                results.append({
                    "line": i,
                    "pattern": p,
                    "text": line.strip()
                })
                break
    return results


def main():
    print("=" * 80)
    print("155C4 - 136E PRODUCTION ADAPTER ÖN KONTROL")
    print("=" * 80)

    t = tag()

    if not os.path.exists(SCRIPT_136E):
        raise FileNotFoundError(f"136E bulunamadı: {SCRIPT_136E}")

    with open(SCRIPT_136E, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    checks = {
        "script_path": SCRIPT_136E,
        "line_count": len(code.splitlines()),
        "has_openai": bool(re.search(r"OpenAI|client\.chat|responses\.create|chat\.completions", code, re.I)),
        "has_sqlite": bool(re.search(r"sqlite3|connect\(", code, re.I)),
        "has_sys_argv": "sys.argv" in code,
        "has_env": "os.environ" in code or "getenv" in code,
        "has_pdf_reader": bool(re.search(r"pypdf|PyPDF|fitz|pdfplumber|PdfReader", code, re.I)),
        "has_jsonl": ".jsonl" in code.lower(),
        "has_rapor": "rapor" in code.lower(),
        "has_batch": "batch" in code.lower(),
    }

    interesting = {
        "input_output_lines": find_lines(code, [
            r"INPUT", r"OUTPUT", r"JSONL", r"TXT", r"PDF", r"KLASOR", r"DIR", r"PATH",
            r"open\(", r"glob", r"os\.walk", r"listdir"
        ]),
        "db_lines": find_lines(code, [
            r"sqlite3", r"kik\.db", r"INSERT", r"UPDATE", r"hukuki_kartlar", r"connect"
        ]),
        "openai_lines": find_lines(code, [
            r"OpenAI", r"api_key", r"chat\.completions", r"responses\.create", r"model"
        ]),
        "main_lines": find_lines(code, [
            r"if __name__", r"def main", r"main\(", r"LIMIT", r"limit", r"MAX", r"DB_YAZ"
        ]),
    }

    state = {
        "run_id": t,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "checks": checks,
        "recommendation": "136E_ADAPTER_YAZILMALI",
        "notes": [
            "Bu kontrol 136E dosyasını değiştirmez.",
            "Amaç 136E'nin sabit input/output davranışını tespit etmektir.",
            "Sonraki adımda 136E_Production_Adapter yazılacaktır."
        ]
    }

    state_path = os.path.join(STATE_DIR, f"155C4_136E_adapter_on_kontrol_state_{t}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"155C4_136E_adapter_on_kontrol_raporu_{t}.txt")

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump({
            "state": state,
            "interesting": interesting
        }, f, ensure_ascii=False, indent=2)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("155C4 - 136E PRODUCTION ADAPTER ÖN KONTROL RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih             : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"136E Script        : {SCRIPT_136E}\n")
        f.write(f"Satır sayısı       : {checks['line_count']}\n\n")

        f.write("GENEL KONTROLLER\n")
        f.write("-" * 80 + "\n")
        for k, v in checks.items():
            f.write(f"{k:20}: {v}\n")

        for section, rows in interesting.items():
            f.write(f"\n{section.upper()}\n")
            f.write("-" * 80 + "\n")
            for r in rows[:120]:
                f.write(f"L{r['line']:>4} | {r['text']}\n")

        f.write("\nSONUÇ\n")
        f.write("-" * 80 + "\n")
        f.write("136E mevcut haliyle korunacak. Production Adapter yazılacak.\n")
        f.write(f"State: {state_path}\n")

    print("\n136E ADAPTER ÖN KONTROL TAMAMLANDI")
    print("-" * 80)
    print(f"Satır sayısı  : {checks['line_count']}")
    print(f"OpenAI var    : {checks['has_openai']}")
    print(f"SQLite var    : {checks['has_sqlite']}")
    print(f"sys.argv var  : {checks['has_sys_argv']}")
    print(f"env var       : {checks['has_env']}")
    print(f"PDF reader    : {checks['has_pdf_reader']}")
    print("\nDosyalar:")
    print(rapor_path)
    print(state_path)


if __name__ == "__main__":
    main()