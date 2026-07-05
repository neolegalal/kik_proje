# -*- coding: utf-8 -*-
"""
157 - 128 PRODUCTION ADAPTER TASARIM ANALİZ MOTORU

Amaç:
- 128_Karar_AI_OpenAI_Toplu_Isleme_Orkestratoru.py dosyasını detaylı analiz eder.
- Dış input alıyor mu, limit var mı, klasör sabit mi, DB yazıyor mu tespit eder.
- OpenAI çağrı yapısını, PDF okuma yapısını, DB insert/update noktalarını raporlar.
- 128'i değiştirmez.
- DB'ye yazmaz.
- OpenAI çağırmaz.
"""

import os
import re
import json
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

SCRIPT_128 = os.path.join(PY_DIR, "128_Karar_AI_OpenAI_Toplu_Isleme_Orkestratoru.py")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def read_code(path):
    for enc in ["utf-8", "utf-8-sig", "cp1254", "latin-1"]:
        try:
            with open(path, "r", encoding=enc, errors="ignore") as f:
                return f.read(), enc
        except Exception:
            pass
    return "", "OKUNAMADI"


def find_lines(code, patterns, context=0):
    lines = code.splitlines()
    results = []

    for i, line in enumerate(lines, start=1):
        for p in patterns:
            if re.search(p, line, re.IGNORECASE):
                start = max(1, i - context)
                end = min(len(lines), i + context)
                results.append({
                    "line": i,
                    "pattern": p,
                    "text": line.rstrip(),
                    "context": [
                        {"line": j, "text": lines[j - 1].rstrip()}
                        for j in range(start, end + 1)
                    ]
                })
                break

    return results


def bool_find(code, patterns):
    return any(re.search(p, code, re.IGNORECASE) for p in patterns)


def extract_functions(code):
    funcs = []
    for m in re.finditer(r"^\s*def\s+([a-zA-Z0-9_]+)\s*\((.*?)\):", code, re.MULTILINE):
        funcs.append({
            "name": m.group(1),
            "args": m.group(2),
            "line": code[:m.start()].count("\n") + 1,
        })
    return funcs


def extract_assignments(code):
    keys = [
        "BASE_DIR", "PY_DIR", "PDF_DIR", "DOWNLOAD_DIR", "DB_PATH",
        "MODEL", "LIMIT", "BATCH", "PDF_KLASOR", "INPUT", "OUTPUT",
        "DB_YAZ", "OPENAI_MODEL", "CLIENT"
    ]

    rows = []
    lines = code.splitlines()

    for i, line in enumerate(lines, start=1):
        s = line.strip()
        for key in keys:
            if re.match(rf"^{re.escape(key)}\s*=", s):
                rows.append({
                    "line": i,
                    "key": key,
                    "text": s
                })
    return rows


def main():
    print("=" * 80)
    print("157 - 128 PRODUCTION ADAPTER TASARIM ANALİZ")
    print("=" * 80)

    t = tag()

    if not os.path.exists(SCRIPT_128):
        raise FileNotFoundError(f"128 motoru bulunamadı: {SCRIPT_128}")

    code, encoding = read_code(SCRIPT_128)
    lines = code.splitlines()

    features = {
        "script": SCRIPT_128,
        "encoding": encoding,
        "line_count": len(lines),
        "has_openai": bool_find(code, [r"\bOpenAI\b", r"openai", r"chat\.completions", r"responses\.create", r"client\.chat"]),
        "has_pdf_reader": bool_find(code, [r"PyPDF2", r"pypdf", r"PdfReader", r"fitz", r"pdfplumber", r"extract_text"]),
        "has_sqlite": bool_find(code, [r"sqlite3", r"kik\.db", r"\.connect\("]),
        "has_insert": bool_find(code, [r"\bINSERT\b", r"executemany"]),
        "has_update": bool_find(code, [r"\bUPDATE\b"]),
        "has_sys_argv": bool_find(code, [r"sys\.argv", r"argparse"]),
        "has_env": bool_find(code, [r"os\.environ", r"getenv", r"dotenv"]),
        "has_limit": bool_find(code, [r"\bLIMIT\b", r"limit", r"MAX_", r"TOPLAM"]),
        "has_jsonl": bool_find(code, [r"\.jsonl", r"jsonlines"]),
        "has_prompt": bool_find(code, [r"prompt", r"SYSTEM", r"USER", r"mesaj", r"talimat"]),
        "has_try_except": bool_find(code, [r"try:", r"except"]),
        "has_sleep": bool_find(code, [r"time\.sleep", r"sleep\("]),
    }

    sections = {
        "assignments": extract_assignments(code),
        "functions": extract_functions(code),
        "openai_lines": find_lines(code, [
            r"\bOpenAI\b",
            r"api_key",
            r"chat\.completions",
            r"responses\.create",
            r"model",
            r"temperature",
            r"max_tokens",
        ], context=3),
        "pdf_lines": find_lines(code, [
            r"PdfReader",
            r"extract_text",
            r"pdf",
            r"os\.walk",
            r"glob",
            r"PDF_DIR",
            r"pdfler",
        ], context=2),
        "db_lines": find_lines(code, [
            r"sqlite3",
            r"kik\.db",
            r"hukuki_kartlar",
            r"INSERT",
            r"UPDATE",
            r"connect",
            r"commit",
        ], context=2),
        "loop_lines": find_lines(code, [
            r"for .*pdf",
            r"for .*file",
            r"for .*dosya",
            r"while ",
            r"range\(",
            r"LIMIT",
            r"Toplam PDF",
            r"İşleniyor",
        ], context=2),
        "output_lines": find_lines(code, [
            r"print\(",
            r"rapor",
            r"log",
            r"json",
            r"txt",
            r"csv",
            r"OK",
            r"HATA",
        ], context=1),
    }

    adapter_recommendation = {
        "need_backup": True,
        "recommended_mode": "128_PARAMETRELI_PRODUCTION_SURUMU",
        "safe_first_limit": 5,
        "pilot_input": "uretim_input/155C1_136E_pilot_input_*.jsonl veya 154_pilot_batch_*.jsonl",
        "required_changes": [
            "sys.argv ile input_jsonl parametresi almalı",
            "sys.argv veya env ile limit almalı",
            "DB yazma varsayılan True olsa bile pilotta kontrol edilebilir olmalı",
            "Sadece input_jsonl içindeki pdf_yolu kayıtlarını işlemeli",
            "İşlenen her karar için production log yazmalı",
            "Aynı karar_no DB'de varsa atlama veya güncelleme politikasını netleştirmeli",
            "İlk pilot 5 karar, sonra 500 karar çalışmalı",
        ]
    }

    state = {
        "run_id": t,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "features": features,
        "adapter_recommendation": adapter_recommendation,
        "sections": sections,
    }

    state_path = os.path.join(STATE_DIR, f"157_128_adapter_tasarim_analiz_{t}.json")
    rapor_path = os.path.join(RAPOR_DIR, f"157_128_adapter_tasarim_analiz_raporu_{t}.txt")

    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("157 - 128 PRODUCTION ADAPTER TASARIM ANALİZ RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih              : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"128 Script          : {SCRIPT_128}\n")
        f.write(f"Encoding            : {encoding}\n")
        f.write(f"Satır sayısı        : {features['line_count']}\n\n")

        f.write("ÖZELLİKLER\n")
        f.write("-" * 80 + "\n")
        for k, v in features.items():
            f.write(f"{k:22}: {v}\n")

        f.write("\nSABİT DEĞİŞKENLER / AYARLAR\n")
        f.write("-" * 80 + "\n")
        for x in sections["assignments"]:
            f.write(f"L{x['line']:>4} | {x['text']}\n")

        f.write("\nFONKSİYONLAR\n")
        f.write("-" * 80 + "\n")
        for x in sections["functions"]:
            f.write(f"L{x['line']:>4} | def {x['name']}({x['args']})\n")

        for title in ["openai_lines", "pdf_lines", "db_lines", "loop_lines"]:
            f.write(f"\n{title.upper()}\n")
            f.write("-" * 80 + "\n")
            for x in sections[title][:80]:
                f.write(f"L{x['line']:>4} | {x['text']}\n")

        f.write("\nADAPTER ÖNERİSİ\n")
        f.write("-" * 80 + "\n")
        f.write(f"Mod                  : {adapter_recommendation['recommended_mode']}\n")
        f.write(f"İlk güvenli limit     : {adapter_recommendation['safe_first_limit']}\n")
        f.write("Gerekli değişiklikler:\n")
        for item in adapter_recommendation["required_changes"]:
            f.write(f"- {item}\n")

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"State JSON           : {state_path}\n")
        f.write(f"Rapor                : {rapor_path}\n")

    print("\n128 ADAPTER TASARIM ANALİZİ TAMAMLANDI")
    print("-" * 80)
    print(f"Satır sayısı  : {features['line_count']}")
    print(f"OpenAI        : {'EVET' if features['has_openai'] else 'HAYIR'}")
    print(f"PDF Reader    : {'EVET' if features['has_pdf_reader'] else 'HAYIR'}")
    print(f"SQLite        : {'EVET' if features['has_sqlite'] else 'HAYIR'}")
    print(f"INSERT        : {'EVET' if features['has_insert'] else 'HAYIR'}")
    print(f"UPDATE        : {'EVET' if features['has_update'] else 'HAYIR'}")
    print(f"sys.argv      : {'EVET' if features['has_sys_argv'] else 'HAYIR'}")
    print(f"env           : {'EVET' if features['has_env'] else 'HAYIR'}")
    print(f"Fonksiyon     : {len(sections['functions'])}")
    print(f"Ayar satırı   : {len(sections['assignments'])}")

    print("\nDosyalar:")
    print(rapor_path)
    print(state_path)

    print("\nNOT: 128 dosyası değiştirilmedi. DB'ye yazılmadı. OpenAI çağrılmadı.")


if __name__ == "__main__":
    main()