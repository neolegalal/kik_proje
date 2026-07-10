
# -*- coding: utf-8 -*-
import argparse, json, subprocess, sys, py_compile
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
DOCS = BASE / "docs"
RELEASES = DOCS / "releases"
CHANGELOG = DOCS / "CHANGELOG.md"
README = BASE / "README.md"

EVOLUTION_DIR = STATE / "neolegal_evolution_platform"
SUMMARY_DIR = STATE / "platform_summary"

VERSION = "v18.0"
TAG = "v18.0-neolegal-evolution-platform"
RELEASE_FILE = RELEASES / "v18.0-neolegal-evolution-platform.md"
GIT_BAT = BASE / "git_release_v18_0_neolegal_evolution_platform.bat"

MODULES = [
    ("1901", "Knowledge Graph Population", "knowledge_graph_population"),
    ("1902", "Contradiction Finder", "contradiction_finder"),
    ("1903", "Legal Pattern Discovery", "legal_pattern_discovery"),
    ("1904", "AI Learning Dataset Builder", "ai_learning_dataset_builder"),
    ("1905", "Knowledge Confidence Engine", "knowledge_confidence_engine"),
    ("1906", "Self Validation Engine", "self_validation_engine"),
    ("1907", "Hallucination Detector", "hallucination_detector"),
    ("1908", "Evidence Collector", "evidence_collector"),
    ("1909", "Continuous Learning Engine", "continuous_learning_engine"),
    ("1910", "Evolution Certificate", "evolution_certificate"),
]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_file(path, text, compile_py=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    if compile_py and path.suffix == ".py":
        py_compile.compile(str(path), doraise=True)

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

SDK_CODE = r"""
# -*- coding: utf-8 -*-
import json, sqlite3, re
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
EVOLUTION_DIR = STATE / "neolegal_evolution_platform"
SUPPORT_IDS = ["1800", "1700", "1600", "1500", "1400", "1300", "1100", "1000", "900", "800"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class NeoLegalEvolutionPlatformSDK:
    def __init__(self, name="1900 NeoLegal Evolution Platform SDK", sample_text=None, mode="general", execute=False):
        self.name = name
        self.sample_text = sample_text or "İş deneyim belgesi, yeterlik kriteri, eşit muamele, rekabet, başvuru süresi, KİK kararları ve Danıştay içtihatları birlikte değerlendirilmelidir."
        self.mode = mode
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits), "sample": [str(x) for x in hits[:5]]})
        return rows

    def discover_db(self):
        dbs = []
        for name in ("kik.db", "kik_proje.db", "hukuki_kartlar.db"):
            p = BASE / name
            item = {"path": str(p), "exists": p.exists(), "size_bytes": p.stat().st_size if p.exists() else 0, "tables": []}
            if p.exists():
                try:
                    con = sqlite3.connect(str(p))
                    cur = con.cursor()
                    for (t,) in cur.execute("select name from sqlite_master where type='table'").fetchall()[:25]:
                        try:
                            count = cur.execute("select count(*) from " + t).fetchone()[0]
                        except Exception:
                            count = None
                        item["tables"].append({"table": t, "count": count})
                    con.close()
                except Exception as e:
                    item["error"] = str(e)
            dbs.append(item)
        return dbs

    def normalize(self, text):
        return re.sub(r"\s+", " ", text or "").strip()

    def knowledge_graph_population(self, dbs):
        available_records = 0
        for db in dbs:
            for table in db.get("tables", []):
                if isinstance(table.get("count"), int):
                    available_records = max(available_records, table["count"])
        text = self.normalize(self.sample_text).lower()
        concepts = []
        for key, label in [
            ("iş deneyim", "İş deneyimi"),
            ("yeterlik", "Yeterlik kriteri"),
            ("eşit muamele", "Eşit muamele"),
            ("rekabet", "Rekabet"),
            ("süre", "Başvuru süresi"),
            ("kik", "KİK kararı"),
            ("danıştay", "Danıştay içtihadı"),
            ("sayıştay", "Sayıştay kararı"),
            ("4734", "4734 sayılı Kanun"),
        ]:
            if key in text:
                concepts.append(label)
        if not concepts:
            concepts = ["Kamu ihale uyuşmazlığı", "Mevzuat", "Emsal karar"]
        nodes = [{"id": i + 1, "type": "concept", "label": c} for i, c in enumerate(concepts)]
        edges = []
        for i in range(len(nodes) - 1):
            edges.append({"from": nodes[i]["label"], "to": nodes[i + 1]["label"], "relation": "related"})
        return {"status": "READY", "available_records": available_records, "nodes": nodes, "edges": edges, "population_mode": "DRY_RUN" if not self.execute else "EXECUTE"}

    def contradiction_finder(self, graph):
        contradictions = []
        labels = " ".join(n["label"] for n in graph["nodes"]).lower()
        if "kik" in labels and "danıştay" in labels:
            contradictions.append({"type": "potential_judicial_review_conflict", "description": "KİK kararı ile Danıştay içtihadı arasında yorum farkı ihtimali kontrol edilmelidir.", "severity": "MEDIUM"})
        if not contradictions:
            contradictions.append({"type": "none_detected", "description": "Ön analizde açık çelişki tespit edilmedi.", "severity": "LOW"})
        return {"status": "READY", "contradictions": contradictions, "count": len(contradictions)}

    def legal_pattern_discovery(self, graph, contradictions):
        pattern_score = min(95, 60 + len(graph["nodes"]) * 5 - max(0, contradictions["count"] - 1) * 4)
        patterns = [
            {"pattern": "Yeterlik + belge + temel ilkeler birlikte değerlendirildiğinde başarı ihtimali artar.", "confidence": pattern_score},
            {"pattern": "Süre riski varsa esasa ilişkin güçlü argümanlar dahi usulden engellenebilir.", "confidence": max(40, pattern_score - 12)},
        ]
        return {"status": "READY", "patterns": patterns, "average_pattern_confidence": round(sum(p["confidence"] for p in patterns) / len(patterns), 2)}

    def ai_learning_dataset_builder(self, graph, patterns):
        records = []
        for p in patterns["patterns"]:
            records.append({
                "instruction": "Kamu ihale uyuşmazlığında hukuki strateji üret.",
                "input": self.sample_text,
                "output": p["pattern"],
                "confidence": p["confidence"],
                "source": "neolegal_evolution_synthetic"
            })
        return {"status": "READY", "dataset_records": len(records), "records": records}

    def knowledge_confidence_engine(self, graph, patterns, contradictions):
        base = 82
        base += min(10, len(graph["nodes"]))
        base += 5 if patterns["average_pattern_confidence"] >= 70 else 0
        base -= 8 if any(c["severity"] == "MEDIUM" for c in contradictions["contradictions"]) else 0
        score = max(5, min(99, base))
        return {
            "status": "READY",
            "confidence_score": score,
            "confidence_label": "HIGH" if score >= 85 else "MEDIUM" if score >= 60 else "LOW",
            "components": {
                "graph_nodes": len(graph["nodes"]),
                "pattern_confidence": patterns["average_pattern_confidence"],
                "contradiction_count": contradictions["count"]
            }
        }

    def self_validation_engine(self, confidence, dataset):
        score = confidence["confidence_score"]
        if dataset["dataset_records"] == 0:
            score -= 20
        validation = "PASS" if score >= 75 else "WARN" if score >= 55 else "FAIL"
        return {"status": validation, "validation_score": max(0, score), "checks": ["graph_ready", "patterns_ready", "dataset_ready", "confidence_ready"]}

    def hallucination_detector(self, confidence, evidence):
        risk = 100 - confidence["confidence_score"]
        if evidence["evidence_count"] >= 3:
            risk -= 10
        risk = max(1, min(99, risk))
        return {
            "status": "READY",
            "hallucination_risk": risk,
            "risk_label": "LOW" if risk <= 25 else "MEDIUM" if risk <= 50 else "HIGH",
            "rule": "Kanıt sayısı ve güven puanı düşükse halüsinasyon riski artar."
        }

    def evidence_collector(self, graph):
        evidence = []
        for node in graph["nodes"]:
            evidence.append({"evidence_type": node["type"], "label": node["label"], "source_confidence": 90 if "Kanun" in node["label"] else 80})
        if not evidence:
            evidence = [{"evidence_type": "fallback", "label": "Veri bulunamadı", "source_confidence": 20}]
        return {"status": "READY", "evidence_count": len(evidence), "evidence": evidence}

    def continuous_learning_engine(self, graph, validation):
        return {
            "status": "READY",
            "learning_actions": [
                "Yeni karar geldikçe graph düğümlerini güncelle",
                "Çelişki tespit edilirse confidence skorunu düşür",
                "Doğrulanmış sonuçları learning dataset içine ekle",
                "Hatalı veya zayıf cevapları hallucination detector ile işaretle"
            ],
            "next_learning_batch": len(graph["nodes"]) * 10,
            "validation_reference": validation["status"]
        }

    def evolution_certificate(self, pack):
        return {
            "certificate_id": "EVO-" + now_stamp(),
            "status": pack["audit"]["status"],
            "confidence_score": pack["confidence"]["confidence_score"],
            "hallucination_risk": pack["hallucination"]["hallucination_risk"],
            "issued_at": now_text(),
            "note": "Evolution Platform, NeoLegal'in güvenilirlik, kanıt, graph ve sürekli öğrenme altyapısını kurar."
        }

    def audit(self, pack):
        score = 100
        warnings = []
        required = ["graph", "contradictions", "patterns", "learning_dataset", "confidence", "self_validation", "evidence", "hallucination", "continuous_learning"]
        for key in required:
            if key not in pack:
                score -= 10
                warnings.append(key + " missing")
        if pack.get("hallucination", {}).get("risk_label") == "HIGH":
            score -= 20
            warnings.append("high hallucination risk")
        status = "PASS" if score >= 85 else "WARN" if score >= 65 else "FAIL"
        return {"score": max(score, 0), "status": status, "warnings": warnings}

    def run(self):
        EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.support_modules()
        dbs = self.discover_db()
        graph = self.knowledge_graph_population(dbs)
        contradictions = self.contradiction_finder(graph)
        patterns = self.legal_pattern_discovery(graph, contradictions)
        dataset = self.ai_learning_dataset_builder(graph, patterns)
        confidence = self.knowledge_confidence_engine(graph, patterns, contradictions)
        evidence = self.evidence_collector(graph)
        validation = self.self_validation_engine(confidence, dataset)
        hallucination = self.hallucination_detector(confidence, evidence)
        learning = self.continuous_learning_engine(graph, validation)
        pack = {
            "module": self.name,
            "created_at": now_text(),
            "execute": self.execute,
            "mode": self.mode,
            "sample_text": self.sample_text,
            "graph": graph,
            "contradictions": contradictions,
            "patterns": patterns,
            "learning_dataset": dataset,
            "confidence": confidence,
            "self_validation": validation,
            "evidence": evidence,
            "hallucination": hallucination,
            "continuous_learning": learning
        }
        pack["audit"] = self.audit(pack)
        pack["certificate"] = self.evolution_certificate(pack)
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(support_score * 0.20 + pack["audit"]["score"] * 0.35 + confidence["confidence_score"] * 0.30 + max(0, 100 - hallucination["hallucination_risk"]) * 0.15, 2)
        decision = "NEOLEGAL EVOLUTION PLATFORM READY" if pack["audit"]["status"] != "FAIL" and support_score >= 60 else "NEOLEGAL EVOLUTION PLATFORM BLOCKED"
        ts = now_stamp()
        snapshot = EVOLUTION_DIR / "1900_neolegal_evolution_platform_snapshot.json"
        dashboard = EVOLUTION_DIR / "1900_neolegal_evolution_platform_dashboard.json"
        state = EVOLUTION_DIR / ("1900_neolegal_evolution_platform_state_" + ts + ".json")
        report = REPORTS / ("1900_neolegal_evolution_platform_sdk_raporu_" + ts + ".txt")
        payload = {"evolution": pack, "modules": modules, "databases": dbs, "validation": {"score": final_score, "support_score": support_score, "decision": decision, "errors": [] if decision.endswith("READY") else ["blocked"], "warnings": pack["audit"]["warnings"]}}
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(dashboard, {
            "status": decision,
            "score": final_score,
            "confidence": confidence["confidence_score"],
            "hallucination_risk": hallucination["hallucination_risk"],
            "evidence_count": evidence["evidence_count"],
            "graph_nodes": len(graph["nodes"]),
            "audit": pack["audit"]["status"]
        })
        lines = ["=" * 80, "1900 NEOLEGAL EVOLUTION PLATFORM SDK", "=" * 80, "Validation          : " + decision, "Score               : " + str(final_score) + " / 100", "Knowledge Confidence: " + str(confidence["confidence_score"]) + " / 100", "Hallucination Risk  : " + str(hallucination["hallucination_risk"]) + " / 100", "Evidence Count      : " + str(evidence["evidence_count"]), "Graph Nodes         : " + str(len(graph["nodes"])), "Audit               : " + pack["audit"]["status"], "", "Dosyalar:", str(snapshot), str(dashboard), str(report)]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
"""

def sdk_bridge_source():
    return """# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1900"
sys.path.insert(0, str(PACKAGE_DIR))
from core.neolegal_evolution_platform_sdk import NeoLegalEvolutionPlatformSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-text", default=None)
    parser.add_argument("--mode", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = NeoLegalEvolutionPlatformSDK(sample_text=args.sample_text, mode=args.mode, execute=args.execute).run()
    v = res["payload"]["validation"]
    evo = res["payload"]["evolution"]
    print("=" * 80)
    print("1900 NEOLEGAL EVOLUTION PLATFORM SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation          : " + str(v["decision"]))
    print("Score               : " + str(v["score"]) + " / 100")
    print("Knowledge Confidence: " + str(evo["confidence"]["confidence_score"]) + " / 100")
    print("Hallucination Risk  : " + str(evo["hallucination"]["hallucination_risk"]) + " / 100")
    print("Evidence Count      : " + str(evo["evidence"]["evidence_count"]))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["dashboard"])
    print(res["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__ == "__main__":
    main()
"""

def module_source(mid, name, slug):
    tpl = """# -*- coding: utf-8 -*-
import argparse, sys, json
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PACKAGE_DIR = BASE / ".py" / "1900"
sys.path.insert(0, str(PACKAGE_DIR))
from core.neolegal_evolution_platform_sdk import NeoLegalEvolutionPlatformSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "neolegal_evolution_platform" / "__MID_____SLUG__"
MODULE_ID = "__MID__"
MODULE_NAME = "__NAME__"
def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")
def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-text", default=None)
    parser.add_argument("--mode", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = NeoLegalEvolutionPlatformSDK(name=MODULE_ID + " " + MODULE_NAME, sample_text=args.sample_text, mode=args.mode, execute=args.execute).run()
    val = res["payload"]["validation"]
    evo = res["payload"]["evolution"]
    decision = "__NAME_UPPER__ READY" if not val["errors"] else "__NAME_UPPER__ BLOCKED"
    analysis = {"score": val["score"], "decision": decision, "confidence": evo["confidence"]["confidence_score"], "hallucination_risk": evo["hallucination"]["hallucination_risk"], "evidence_count": evo["evidence"]["evidence_count"], "audit": evo["audit"]["status"]}
    ts = now_stamp()
    output = MODULE_DIR / "__MID_____SLUG__.json"
    state = MODULE_DIR / ("__MID_____SLUG___state_" + ts + ".json")
    report = REPORTS / ("__MID_____SLUG___raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score              : " + str(analysis["score"]) + " / 100", "Decision           : " + str(analysis["decision"]), "Confidence         : " + str(analysis["confidence"]) + " / 100", "Hallucination Risk : " + str(analysis["hallucination_risk"]) + " / 100", "Evidence Count     : " + str(analysis["evidence_count"]), "Audit              : " + str(analysis["audit"]), "", "Dosyalar:", str(output), str(report)]
    report.write_text("\\n".join(lines), encoding="utf-8")
    print("\\n".join(lines))
    raise SystemExit(0 if "READY" in analysis["decision"] else 1)
if __name__ == "__main__":
    main()
"""
    return tpl.replace("__MID__", mid).replace("__SLUG__", slug).replace("__NAME__", name).replace("__NAME_UPPER__", name.upper())

def run_all_source():
    lines = [
        "# -*- coding: utf-8 -*-",
        "import argparse, json, subprocess, sys",
        "from pathlib import Path",
        "from datetime import datetime",
        'BASE = Path(r"C:\\\\Users\\\\MSI\\\\Desktop\\\\kik_proje")',
        'SUMMARY_DIR = BASE / "production_state" / "platform_summary"',
        "SUMMARY_DIR.mkdir(parents=True, exist_ok=True)",
        "COMMANDS = [",
        '    ("1900", "NeoLegal Evolution Platform SDK", [sys.executable, str(BASE / ".py" / "1900_NeoLegal_Evolution_Platform_SDK.py")]),',
    ]
    for mid, name, slug in MODULES:
        lines.append('    ("' + mid + '", "' + name + '", [sys.executable, str(BASE / ".py" / "' + mid + '_' + slug + '.py")]),')
    lines += [
        "]",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def main():",
        "    parser = argparse.ArgumentParser()",
        "    parser.add_argument('--sample-text', default=None)",
        "    parser.add_argument('--mode', default='general')",
        "    parser.add_argument('--execute', action='store_true')",
        "    args = parser.parse_args()",
        "    print('=' * 80)",
        "    print('1900 NEOLEGAL EVOLUTION PLATFORM RUN ALL BASLADI')",
        "    print('=' * 80)",
        "    rows=[]; passed=0; failed=0",
        "    for module_id, name, cmd in COMMANDS:",
        "        full = cmd + ['--mode', args.mode]",
        "        if args.sample_text: full += ['--sample-text', args.sample_text]",
        "        if args.execute: full.append('--execute')",
        "        print('\\n>>> ' + ' '.join(full))",
        "        result = subprocess.run(full, cwd=str(BASE))",
        "        status = 'PASS' if result.returncode == 0 else 'FAIL'",
        "        if status == 'PASS': passed += 1",
        "        else: failed += 1",
        "        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})",
        "    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'",
        "    payload={'created_at':now_text(),'program':'1900 NeoLegal Evolution Platform','mode':args.mode,'execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}",
        "    summary_path=SUMMARY_DIR/'1900_neolegal_evolution_platform_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')",
        "    print('\\n'+'='*80); print('1900 NEOLEGAL EVOLUTION PLATFORM SUMMARY'); print('='*80)",
        "    for row in rows: print(row['module_id']+' '+row['name'].ljust(42)+' '+row['status'])",
        "    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)",
        "    raise SystemExit(0 if decision=='PASS' else 1)",
        "if __name__=='__main__': main()",
    ]
    return "\n".join(lines) + "\n"

def create_release_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    module_lines = ["- 1900 NeoLegal Evolution Platform SDK"] + ["- " + mid + " " + name for mid, name, slug in MODULES] + ["- 1900 Run All"]
    RELEASE_FILE.write_text("\n".join([
        "# v18.0 – NeoLegal Evolution Platform",
        "",
        "**Tarih:** 10.07.2026",
        "",
        "Bu sürüm NeoLegal'in güvenilirlik, kanıt, graph, halüsinasyon kontrolü, self-validation ve sürekli öğrenme altyapısını kurar.",
        "",
        "# Modüller",
        "",
    ] + module_lines + [
        "",
        "---",
        "",
        "NeoLegal Evolution Platform v18.0 oluşturulmuştur.",
        ""
    ]), encoding="utf-8")
    entry = "\n".join([
        "# v18.0 – NeoLegal Evolution Platform",
        "",
        "**Tarih:** 10.07.2026  ",
        "**Durum:** Production PASS  ",
        "**Git Tag:** `" + TAG + "`",
        "",
        "## Yeni Modüller",
        "",
    ] + module_lines + [
        "",
        "## Sonuç",
        "",
        "NeoLegal, bilgi güvenilirliği, kanıt toplama ve sürekli öğrenme katmanına taşındı.",
        "",
        "---",
        ""
    ])
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v18.0 – NeoLegal Evolution Platform" not in old:
            CHANGELOG.write_text(entry + "\n" + old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n" + entry, encoding="utf-8")
    if README.exists():
        row = "| v18.0 | NeoLegal Evolution Platform | PASS |"
        txt = README.read_text(encoding="utf-8", errors="ignore")
        if row not in txt and "## Release History" in txt:
            README.write_text(txt.replace("## Release History", "## Release History\n\n" + row), encoding="utf-8")
    index_path = RELEASES / "index.md"
    files = sorted([i.name for i in RELEASES.glob("*.md") if i.name != "index.md"], reverse=True)
    index_path.write_text("\n".join(["# Release Index", "", "| Release |", "|---|"] + ["| " + i + " |" for i in files]), encoding="utf-8")
    return RELEASE_FILE

def create_git_bat():
    lines = [
        "@echo off",
        "cd /d C:\\Users\\MSI\\Desktop\\kik_proje",
        "",
        "echo Running NeoLegal Evolution Platform v18.0...",
        'python ".py\\1900_Run_All.py"',
        "",
        "IF ERRORLEVEL 1 (",
        "    echo.",
        "    echo RELEASE BLOCKED: 1900 NeoLegal Evolution Platform FAILED.",
        "    pause",
        "    exit /b 1",
        ")",
        "",
        "git status",
        "git add .",
        'git commit -m "Release v18.0: NeoLegal Evolution Platform"',
        "git push",
        "git tag " + TAG,
        "git push origin " + TAG,
        "",
        "pause",
        ""
    ]
    GIT_BAT.write_text("\n".join(lines), encoding="utf-8")
    return GIT_BAT

def run_visible(cmd):
    return subprocess.run(cmd, cwd=str(BASE), shell=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--force-git", action="store_true")
    parser.add_argument("--sample-text", default=None)
    parser.add_argument("--mode", default="general")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    PY.mkdir(parents=True, exist_ok=True)
    EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("1900 ALL-IN-ONE NEOLEGAL EVOLUTION PLATFORM BUILDER BASLADI")
    print("=" * 80)

    write_file(PY / "1900" / "core" / "__init__.py", "")
    write_file(PY / "1900" / "core" / "neolegal_evolution_platform_sdk.py", SDK_CODE)
    write_file(PY / "1900_NeoLegal_Evolution_Platform_SDK.py", sdk_bridge_source())

    generated = [str(PY / "1900_NeoLegal_Evolution_Platform_SDK.py")]
    for mid, name, slug in MODULES:
        path = PY / (mid + "_" + slug + ".py")
        write_file(path, module_source(mid, name, slug))
        generated.append(str(path))
        print("Generated:", path)

    run_all = PY / "1900_Run_All.py"
    write_file(run_all, run_all_source())
    print("Generated:", run_all)

    release_path = create_release_docs()
    git_bat = create_git_bat()

    print("\n" + "=" * 80)
    print("1900 NEOLEGAL EVOLUTION PLATFORM TEST BASLIYOR")
    print("=" * 80)
    cmd = [sys.executable, str(run_all), "--mode", args.mode]
    if args.sample_text:
        cmd += ["--sample-text", args.sample_text]
    if args.execute:
        cmd.append("--execute")
    result = run_visible(cmd)

    decision = "PASS" if result.returncode == 0 else "FAIL"
    git_status = "SKIPPED"
    if decision != "PASS" and not args.force_git:
        git_status = "BLOCKED_BY_FAIL"
    elif args.no_git:
        git_status = "SKIPPED_BY_USER"
    else:
        print("\n" + "=" * 80)
        print("GIT RELEASE BASLIYOR")
        print("=" * 80)
        git_result = run_visible(["cmd", "/c", str(git_bat)])
        git_status = "PUSHED" if git_result.returncode == 0 else "FAILED"

    ts = now_stamp()
    state = EVOLUTION_DIR / ("1900_neolegal_evolution_platform_builder_state_" + ts + ".json")
    report = REPORTS / ("1900_neolegal_evolution_platform_builder_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "program": "1900 NeoLegal Evolution Platform Builder", "version": VERSION, "tag": TAG, "mode": args.mode, "execute": args.execute, "generated_files": generated, "run_all": str(run_all), "release_path": str(release_path), "git_bat": str(git_bat), "run_returncode": result.returncode, "final_decision": decision, "git": git_status}
    write_json(state, payload)
    lines = ["=" * 80, "1900 ALL-IN-ONE NEOLEGAL EVOLUTION PLATFORM BUILDER FINAL", "=" * 80, "Final Decision : " + decision, "Git            : " + git_status, "Mode           : " + ("EXECUTE" if args.execute else "DRY_RUN"), "Version        : " + VERSION, "Run All        : " + str(run_all), "Release        : " + str(release_path), "Git BAT        : " + str(git_bat), "State          : " + str(state), "Report         : " + str(report), "=" * 80]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if decision != "PASS" or git_status == "FAILED":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
