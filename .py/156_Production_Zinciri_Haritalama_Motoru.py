# -*- coding: utf-8 -*-
"""
156 - PRODUCTION ZİNCİRİ HARİTALAMA MOTORU

Amaç:
- .py klasöründeki tüm Python scriptlerini analiz eder.
- OpenAI, SQLite, PDF, JSONL, DB yazma/okuma, subprocess, Selenium vb. işaretleri çıkarır.
- Muhtemel AI motorlarını, DB yazanları, validator/export motorlarını sınıflandırır.
- Production pipeline için envanter üretir.
- Hiçbir scripti çalıştırmaz.
- DB'ye yazmaz.

Kullanım:
  python ".py\\156_Production_Zinciri_Haritalama_Motoru.py"
"""

import os
import re
import csv
import json
from datetime import datetime

BASE_DIR = r"C:\Users\MSI\Desktop\kik_proje"
PY_DIR = os.path.join(BASE_DIR, ".py")
RAPOR_DIR = os.path.join(BASE_DIR, "raporlar")
STATE_DIR = os.path.join(BASE_DIR, "production_state")

os.makedirs(RAPOR_DIR, exist_ok=True)
os.makedirs(STATE_DIR, exist_ok=True)


def tag():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def safe_read(path):
    for enc in ["utf-8", "utf-8-sig", "cp1254", "latin-1"]:
        try:
            with open(path, "r", encoding=enc, errors="ignore") as f:
                return f.read(), enc
        except Exception:
            continue
    return "", "OKUNAMADI"


def bool_find(code, patterns):
    for p in patterns:
        if re.search(p, code, re.IGNORECASE):
            return True
    return False


def count_find(code, patterns):
    total = 0
    for p in patterns:
        total += len(re.findall(p, code, re.IGNORECASE))
    return total


def extract_imports(code):
    imports = set()
    for m in re.finditer(r"^\s*import\s+([a-zA-Z0-9_.,\s]+)", code, re.MULTILINE):
        raw = m.group(1)
        for part in raw.split(","):
            mod = part.strip().split(" as ")[0].strip()
            if mod:
                imports.add(mod)
    for m in re.finditer(r"^\s*from\s+([a-zA-Z0-9_\.]+)\s+import\s+", code, re.MULTILINE):
        imports.add(m.group(1).strip())
    return sorted(imports)


def extract_paths(code):
    paths = set()

    patterns = [
        r"r[\"']([^\"']{3,})[\"']",
        r"[\"']([^\"']{3,})[\"']",
    ]

    for p in patterns:
        for m in re.finditer(p, code):
            s = m.group(1)
            if any(x in s.lower() for x in [
                "c:\\", ".py", ".db", ".jsonl", ".json", ".txt", ".csv",
                "raporlar", "export", "batch", "pdf", "kik_proje"
            ]):
                paths.add(s)

    return sorted(paths)


def extract_called_scripts(code):
    called = set()

    for m in re.finditer(r"([0-9]{2,3}[A-Za-z0-9_ÇĞİÖŞÜçğıöşü\-]*\.py)", code):
        called.add(m.group(1))

    for m in re.finditer(r"subprocess\.(?:run|Popen|call)\((.*?)\)", code, re.DOTALL):
        block = m.group(1)
        for sm in re.finditer(r"([0-9]{2,3}[A-Za-z0-9_ÇĞİÖŞÜçğıöşü\-]*\.py)", block):
            called.add(sm.group(1))

    return sorted(called)


def role_guess(filename, code, flags):
    name = filename.lower()

    if flags["has_openai"]:
        if flags["has_pdf_reader"] or flags["has_pdf_text_extract"]:
            return "AI_PDF_URETIM_MOTORU_ADAYI"
        return "AI_MOTORU_ADAYI"

    if flags["has_sqlite"] and flags["has_insert"]:
        return "DB_YAZMA_MOTORU"

    if "validator" in name or "kontrol" in name or "kalite" in name:
        return "VALIDATOR_KALITE_MOTORU"

    if "export" in name or "rag" in name or "web" in name:
        return "EXPORT_MOTORU"

    if "batch" in name or "orkestrator" in name or "runner" in name:
        return "BATCH_ORKESTRASYON_MOTORU"

    if flags["has_selenium"] or flags["has_requests"]:
        return "WEB_VERI_TOPLAMA_MOTORU"

    if flags["has_pdf_reader"] or flags["has_pdf_text_extract"]:
        return "PDF_OKUMA_PARSE_MOTORU"

    if flags["has_docx"]:
        return "DOCX_MOTORU"

    if flags["has_excel"]:
        return "EXCEL_MOTORU"

    return "YARDIMCI_SCRIPT"


def analyze_script(path):
    filename = os.path.basename(path)
    code, encoding = safe_read(path)
    lines = code.splitlines()

    flags = {
        "has_openai": bool_find(code, [
            r"\bOpenAI\b",
            r"openai",
            r"chat\.completions",
            r"responses\.create",
            r"client\.chat",
            r"gpt-",
        ]),
        "has_sqlite": bool_find(code, [
            r"sqlite3",
            r"\.connect\(",
            r"kik\.db",
        ]),
        "has_select": bool_find(code, [
            r"\bSELECT\b",
        ]),
        "has_insert": bool_find(code, [
            r"\bINSERT\b",
            r"\bexecutemany\b",
        ]),
        "has_update": bool_find(code, [
            r"\bUPDATE\b",
        ]),
        "has_delete": bool_find(code, [
            r"\bDELETE\b",
        ]),
        "has_pdf_reader": bool_find(code, [
            r"PyPDF2",
            r"pypdf",
            r"PdfReader",
            r"fitz",
            r"pdfplumber",
            r"pymupdf",
        ]),
        "has_pdf_text_extract": bool_find(code, [
            r"extract_text",
            r"page\.get_text",
            r"pdf",
        ]),
        "has_json": bool_find(code, [
            r"\bjson\b",
            r"\.json",
        ]),
        "has_jsonl": bool_find(code, [
            r"\.jsonl",
            r"jsonlines",
        ]),
        "has_csv": bool_find(code, [
            r"\bcsv\b",
            r"\.csv",
        ]),
        "has_docx": bool_find(code, [
            r"docx",
            r"Document",
            r"\.docx",
        ]),
        "has_excel": bool_find(code, [
            r"openpyxl",
            r"pandas",
            r"\.xlsx",
            r"\.xls",
        ]),
        "has_selenium": bool_find(code, [
            r"selenium",
            r"webdriver",
        ]),
        "has_requests": bool_find(code, [
            r"requests",
            r"urllib",
            r"aiohttp",
        ]),
        "has_subprocess": bool_find(code, [
            r"subprocess",
            r"os\.system",
        ]),
        "has_sys_argv": bool_find(code, [
            r"sys\.argv",
            r"argparse",
        ]),
        "has_env": bool_find(code, [
            r"os\.environ",
            r"getenv",
            r"\.env",
            r"dotenv",
        ]),
        "has_backup": bool_find(code, [
            r"yedek",
            r"backup",
            r"CREATE TABLE.*yedek",
        ]),
        "has_active_quality": bool_find(code, [
            r"aktif",
            r"kalite_etiketi",
            r"kalite_notu",
        ]),
    }

    imports = extract_imports(code)
    paths = extract_paths(code)
    called_scripts = extract_called_scripts(code)

    counts = {
        "openai_count": count_find(code, [r"OpenAI", r"openai", r"chat\.completions", r"responses\.create"]),
        "sqlite_count": count_find(code, [r"sqlite3", r"kik\.db", r"hukuki_kartlar"]),
        "insert_count": count_find(code, [r"\bINSERT\b"]),
        "update_count": count_find(code, [r"\bUPDATE\b"]),
        "select_count": count_find(code, [r"\bSELECT\b"]),
        "pdf_count": count_find(code, [r"pdf", r"PdfReader", r"fitz", r"pdfplumber"]),
        "jsonl_count": count_find(code, [r"\.jsonl"]),
        "subprocess_count": count_find(code, [r"subprocess"]),
    }

    role = role_guess(filename, code, flags)

    return {
        "script": filename,
        "path": path,
        "encoding": encoding,
        "line_count": len(lines),
        "role_guess": role,
        **flags,
        **counts,
        "imports": imports,
        "called_scripts": called_scripts,
        "paths": paths,
    }


def short_bool(v):
    return "EVET" if v else ""


def main():
    print("=" * 80)
    print("156 - PRODUCTION ZİNCİRİ HARİTALAMA MOTORU")
    print("=" * 80)

    t = tag()

    if not os.path.isdir(PY_DIR):
        raise NotADirectoryError(f".py klasörü bulunamadı: {PY_DIR}")

    scripts = []
    for fn in os.listdir(PY_DIR):
        if fn.lower().endswith(".py"):
            scripts.append(os.path.join(PY_DIR, fn))

    scripts.sort(key=lambda p: os.path.basename(p).lower())

    analyses = []
    for i, path in enumerate(scripts, start=1):
        analyses.append(analyze_script(path))
        if i % 25 == 0 or i == len(scripts):
            print(f"Analiz edildi: {i}/{len(scripts)}")

    ai_scripts = [x for x in analyses if x["has_openai"]]
    db_write_scripts = [x for x in analyses if x["has_sqlite"] and (x["has_insert"] or x["has_update"] or x["has_delete"])]
    db_read_scripts = [x for x in analyses if x["has_sqlite"] and x["has_select"]]
    pdf_scripts = [x for x in analyses if x["has_pdf_reader"] or x["has_pdf_text_extract"]]
    validator_scripts = [x for x in analyses if x["role_guess"] == "VALIDATOR_KALITE_MOTORU"]
    export_scripts = [x for x in analyses if x["role_guess"] == "EXPORT_MOTORU"]
    batch_scripts = [x for x in analyses if x["role_guess"] == "BATCH_ORKESTRASYON_MOTORU"]
    subprocess_scripts = [x for x in analyses if x["has_subprocess"]]

    ai_candidates = sorted(
        ai_scripts,
        key=lambda x: (
            x["has_pdf_reader"] or x["has_pdf_text_extract"],
            x["has_sqlite"],
            x["openai_count"],
            x["line_count"],
        ),
        reverse=True
    )

    summary = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_dir": BASE_DIR,
        "py_dir": PY_DIR,
        "total_scripts": len(analyses),
        "ai_scripts": len(ai_scripts),
        "db_write_scripts": len(db_write_scripts),
        "db_read_scripts": len(db_read_scripts),
        "pdf_scripts": len(pdf_scripts),
        "validator_scripts": len(validator_scripts),
        "export_scripts": len(export_scripts),
        "batch_scripts": len(batch_scripts),
        "subprocess_scripts": len(subprocess_scripts),
        "top_ai_candidates": [
            {
                "script": x["script"],
                "role_guess": x["role_guess"],
                "line_count": x["line_count"],
                "openai_count": x["openai_count"],
                "sqlite_count": x["sqlite_count"],
                "pdf_count": x["pdf_count"],
                "jsonl_count": x["jsonl_count"],
            }
            for x in ai_candidates[:20]
        ],
    }

    json_path = os.path.join(STATE_DIR, f"156_production_zinciri_harita_{t}.json")
    csv_path = os.path.join(RAPOR_DIR, f"156_production_zinciri_harita_{t}.csv")
    rapor_path = os.path.join(RAPOR_DIR, f"156_production_zinciri_haritalama_raporu_{t}.txt")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": summary,
            "analyses": analyses,
        }, f, ensure_ascii=False, indent=2)

    csv_fields = [
        "script", "line_count", "role_guess",
        "has_openai", "has_sqlite", "has_select", "has_insert", "has_update", "has_delete",
        "has_pdf_reader", "has_pdf_text_extract", "has_json", "has_jsonl", "has_csv",
        "has_docx", "has_excel", "has_selenium", "has_requests", "has_subprocess",
        "has_sys_argv", "has_env", "has_backup", "has_active_quality",
        "openai_count", "sqlite_count", "insert_count", "update_count", "select_count",
        "pdf_count", "jsonl_count", "subprocess_count",
        "called_scripts",
        "imports",
    ]

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, delimiter=";")
        writer.writeheader()
        for x in analyses:
            row = {}
            for field in csv_fields:
                val = x.get(field, "")
                if isinstance(val, bool):
                    val = short_bool(val)
                elif isinstance(val, list):
                    val = ", ".join(str(v) for v in val[:30])
                row[field] = val
            writer.writerow(row)

    with open(rapor_path, "w", encoding="utf-8") as f:
        f.write("156 - PRODUCTION ZİNCİRİ HARİTALAMA RAPORU\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Tarih                 : {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        f.write(f"BASE_DIR              : {BASE_DIR}\n")
        f.write(f"PY_DIR                : {PY_DIR}\n\n")

        f.write("GENEL ÖZET\n")
        f.write("-" * 80 + "\n")
        f.write(f"Toplam script          : {summary['total_scripts']}\n")
        f.write(f"OpenAI içeren          : {summary['ai_scripts']}\n")
        f.write(f"DB yazan               : {summary['db_write_scripts']}\n")
        f.write(f"DB okuyan              : {summary['db_read_scripts']}\n")
        f.write(f"PDF ile ilgili         : {summary['pdf_scripts']}\n")
        f.write(f"Validator/Kalite       : {summary['validator_scripts']}\n")
        f.write(f"Export                 : {summary['export_scripts']}\n")
        f.write(f"Batch/Orkestrasyon     : {summary['batch_scripts']}\n")
        f.write(f"Subprocess kullanan    : {summary['subprocess_scripts']}\n\n")

        f.write("EN GÜÇLÜ AI MOTORU ADAYLARI\n")
        f.write("-" * 80 + "\n")
        if ai_candidates:
            for x in ai_candidates[:30]:
                f.write(
                    f"{x['script']} | rol={x['role_guess']} | "
                    f"satır={x['line_count']} | openai={x['openai_count']} | "
                    f"sqlite={x['sqlite_count']} | pdf={x['pdf_count']} | jsonl={x['jsonl_count']}\n"
                )
        else:
            f.write("OpenAI kullanan script bulunamadı.\n")

        f.write("\nDB YAZAN SCRIPT'LER\n")
        f.write("-" * 80 + "\n")
        for x in db_write_scripts:
            f.write(
                f"{x['script']} | rol={x['role_guess']} | "
                f"insert={x['insert_count']} | update={x['update_count']} | select={x['select_count']}\n"
            )

        f.write("\nPDF / PARSE SCRIPT'LERİ\n")
        f.write("-" * 80 + "\n")
        for x in pdf_scripts[:80]:
            f.write(
                f"{x['script']} | rol={x['role_guess']} | "
                f"pdf_count={x['pdf_count']} | jsonl={x['jsonl_count']}\n"
            )

        f.write("\nVALIDATOR / KALİTE SCRIPT'LERİ\n")
        f.write("-" * 80 + "\n")
        for x in validator_scripts:
            f.write(f"{x['script']} | satır={x['line_count']} | sqlite={short_bool(x['has_sqlite'])}\n")

        f.write("\nEXPORT SCRIPT'LERİ\n")
        f.write("-" * 80 + "\n")
        for x in export_scripts:
            f.write(f"{x['script']} | satır={x['line_count']} | jsonl={short_bool(x['has_jsonl'])}\n")

        f.write("\nBATCH / ORKESTRASYON SCRIPT'LERİ\n")
        f.write("-" * 80 + "\n")
        for x in batch_scripts:
            f.write(f"{x['script']} | satır={x['line_count']} | subprocess={short_bool(x['has_subprocess'])}\n")

        f.write("\nSCRIPT ENVANTERİ\n")
        f.write("-" * 80 + "\n")
        for x in analyses:
            f.write(
                f"{x['script']} | {x['role_guess']} | "
                f"OpenAI={short_bool(x['has_openai'])} | "
                f"DB={short_bool(x['has_sqlite'])} | "
                f"PDF={short_bool(x['has_pdf_reader'] or x['has_pdf_text_extract'])} | "
                f"JSONL={short_bool(x['has_jsonl'])} | "
                f"ARGV={short_bool(x['has_sys_argv'])}\n"
            )

        f.write("\nDOSYALAR\n")
        f.write("-" * 80 + "\n")
        f.write(f"JSON harita            : {json_path}\n")
        f.write(f"CSV harita             : {csv_path}\n")
        f.write(f"Rapor                  : {rapor_path}\n")

    print("\nPRODUCTION ZİNCİRİ HARİTALAMA TAMAMLANDI")
    print("-" * 80)
    print(f"Toplam script       : {summary['total_scripts']}")
    print(f"OpenAI içeren       : {summary['ai_scripts']}")
    print(f"DB yazan            : {summary['db_write_scripts']}")
    print(f"PDF ile ilgili      : {summary['pdf_scripts']}")
    print(f"Validator/Kalite    : {summary['validator_scripts']}")
    print(f"Export              : {summary['export_scripts']}")
    print(f"Batch/Orkestrasyon  : {summary['batch_scripts']}")

    print("\nEn güçlü AI adayları:")
    if ai_candidates:
        for x in ai_candidates[:10]:
            print(f"- {x['script']} | rol={x['role_guess']} | openai={x['openai_count']} | pdf={x['pdf_count']} | db={x['sqlite_count']}")
    else:
        print("- OpenAI kullanan script bulunamadı.")

    print("\nDosyalar:")
    print(rapor_path)
    print(csv_path)
    print(json_path)


if __name__ == "__main__":
    main()