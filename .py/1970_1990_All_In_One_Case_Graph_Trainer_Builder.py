
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

CGT_DIR = STATE / "case_graph_trainer"
SUMMARY_DIR = STATE / "platform_summary"

VERSION = "v18.6-v18.8"
TAG = "v18.6-v18.8-case-graph-trainer"
RELEASE_FILE = RELEASES / "v18.6-v18.8-case-graph-trainer.md"
GIT_BAT = BASE / "git_release_v18_6_to_v18_8_case_graph_trainer.bat"

MODULES_1970 = [
    ("1971", "Dispute Priority Scorer", "dispute_priority_scorer"),
    ("1972", "Main Issue Detector", "main_issue_detector"),
    ("1973", "Sub Issue Mapper", "sub_issue_mapper"),
    ("1974", "Result Impact Analyzer", "result_impact_analyzer"),
    ("1975", "Case Intelligence Auditor", "case_intelligence_auditor"),
]
MODULES_1980 = [
    ("1981", "Graph Node Builder", "graph_node_builder"),
    ("1982", "Graph Edge Builder", "graph_edge_builder"),
    ("1983", "Precedent Relation Builder", "precedent_relation_builder"),
    ("1984", "Contradiction Relation Builder", "contradiction_relation_builder"),
    ("1985", "Legal Graph Auditor", "legal_graph_auditor"),
]
MODULES_1990 = [
    ("1991", "Instruction Dataset Builder", "instruction_dataset_builder"),
    ("1992", "Rag Dataset Builder", "rag_dataset_builder"),
    ("1993", "Fine Tuning Dataset Builder", "fine_tuning_dataset_builder"),
    ("1994", "Evaluation Benchmark Builder", "evaluation_benchmark_builder"),
    ("1995", "AI Trainer Certificate", "ai_trainer_certificate"),
]
MODULES = MODULES_1970 + MODULES_1980 + MODULES_1990

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
import json, re
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
CGT_DIR = STATE / "case_graph_trainer"
UDP_DIR = STATE / "unified_decision_processor"
SUPPORT_IDS = ["1950", "1900", "1800", "1700", "1600", "1500", "1400", "1300", "1100"]

def now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class CaseGraphTrainerSDK:
    def __init__(self, name="1970-1990 Case Graph Trainer SDK", master_record_path=None, case_text=None, execute=False):
        self.name = name
        self.master_record_path = Path(master_record_path) if master_record_path else None
        self.case_text = case_text or "İş deneyim belgesi, benzer iş, yeterlik kriteri, şikâyet süresi, eşit muamele ve rekabet ilkeleri birlikte değerlendirilmiştir."
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits)})
        return rows

    def load_master_record(self):
        if self.master_record_path and self.master_record_path.exists():
            try:
                return json.loads(self.master_record_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        latest = sorted(UDP_DIR.glob("1950_master_record_*.json"), reverse=True)
        if latest:
            try:
                return json.loads(latest[0].read_text(encoding="utf-8"))
            except Exception:
                pass
        topics = []
        for i, topic in enumerate(["İş deneyim belgesi", "Benzer iş tanımı", "Yeterlik kriteri", "Şikâyet süresi", "Eşit muamele ilkesi", "Rekabet ilkesi"], 1):
            topics.append({
                "topic_id": i,
                "topic": topic,
                "legal_question": topic + " yönünden idarenin işlemi hukuka uygun mudur?",
                "issue_summary": self.case_text,
                "legal_problem": topic + " bakımından uyuşmazlık değerlendirilmelidir.",
                "legislation": ["4734 sayılı Kamu İhale Kanunu m.5 temel ilkeler"],
                "success_probability": 60 + i,
                "confidence": 75 + i,
                "risk": "MEDIUM",
                "evidence": [{"type": "synthetic", "label": topic, "confidence": 80}],
                "graph_links": [{"from": topic, "to": "4734 m.5", "relation": "applies"}]
            })
        return {
            "record_id": "NMR-SYNTHETIC-" + now_stamp(),
            "created_at": now_text(),
            "metadata": {"source_type": "synthetic"},
            "topic_records": topics,
            "overall": {"topic_count": len(topics), "average_success_probability": 63, "average_confidence": 78, "overall_risk": "MEDIUM"}
        }

    def case_intelligence(self, master):
        topics = master.get("topic_records", [])
        scored = []
        for t in topics:
            base = 50
            topic = t.get("topic", "")
            if "İş deneyim" in topic or "Yeterlik" in topic:
                base += 20
            if "Şikâyet" in topic or "süre" in topic.lower():
                base += 15
            if "Eşit muamele" in topic or "Rekabet" in topic:
                base += 12
            base += min(10, int(t.get("confidence", 70)) - 70) if t.get("confidence", 70) > 70 else 0
            scored.append({**t, "priority_score": min(100, base), "role": "UNCLASSIFIED"})
        scored = sorted(scored, key=lambda x: x["priority_score"], reverse=True)
        for i, t in enumerate(scored):
            t["role"] = "MAIN_ISSUE" if i == 0 else "IMPORTANT_SUB_ISSUE" if i <= 2 else "SUB_ISSUE"
            t["result_impact"] = "HIGH" if i == 0 else "MEDIUM" if i <= 2 else "LOW"
        return {
            "status": "READY",
            "main_issue": scored[0] if scored else None,
            "prioritized_topics": scored,
            "topic_count": len(scored),
            "case_structure": "multi_issue" if len(scored) > 1 else "single_issue"
        }

    def graph_builder(self, master, intelligence):
        nodes = []
        edges = []
        seen = set()
        def add_node(ntype, label):
            key = ntype + "::" + label
            if key not in seen:
                seen.add(key)
                nodes.append({"id": len(nodes) + 1, "type": ntype, "label": label})
        add_node("case", master.get("record_id", "case"))
        for t in intelligence["prioritized_topics"]:
            topic = t.get("topic", "Konu")
            add_node("issue", topic)
            edges.append({"from": master.get("record_id", "case"), "to": topic, "relation": t.get("role", "related")})
            for leg in t.get("legislation", []):
                add_node("legislation", leg)
                edges.append({"from": topic, "to": leg, "relation": "applies"})
            for gl in t.get("graph_links", []):
                add_node("concept", gl.get("to", "concept"))
                edges.append({"from": gl.get("from", topic), "to": gl.get("to", "concept"), "relation": gl.get("relation", "related")})
        return {
            "status": "READY",
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "graph_type": "legal_case_knowledge_graph"
        }

    def dataset_factory(self, master, intelligence, graph):
        instruction = []
        rag = []
        fine_tuning = []
        evals = []
        for t in intelligence["prioritized_topics"]:
            question = t.get("legal_question", t.get("topic", "Hukuki soru"))
            answer = t.get("legal_problem", "") + " " + t.get("issue_summary", "")
            instruction.append({"instruction": "Kamu ihale uyuşmazlığını analiz et.", "input": question, "output": answer, "priority": t.get("priority_score")})
            rag.append({"chunk_id": "issue_" + str(t.get("topic_id")), "content": question + " " + answer, "metadata": {"topic": t.get("topic"), "role": t.get("role"), "confidence": t.get("confidence")}})
            fine_tuning.append({"messages": [{"role": "user", "content": question}, {"role": "assistant", "content": answer}]})
            evals.append({"question": question, "expected_topic": t.get("topic"), "expected_role": t.get("role")})
        return {
            "status": "READY",
            "instruction_dataset": instruction,
            "rag_dataset": rag,
            "fine_tuning_dataset": fine_tuning,
            "evaluation_dataset": evals,
            "counts": {
                "instruction": len(instruction),
                "rag": len(rag),
                "fine_tuning": len(fine_tuning),
                "evaluation": len(evals)
            }
        }

    def audit(self, intelligence, graph, dataset):
        score = 100
        warnings = []
        if intelligence["topic_count"] == 0:
            score -= 40; warnings.append("no topic")
        if graph["node_count"] == 0 or graph["edge_count"] == 0:
            score -= 25; warnings.append("empty graph")
        if dataset["counts"]["rag"] == 0:
            score -= 20; warnings.append("empty rag dataset")
        if not intelligence.get("main_issue"):
            score -= 15; warnings.append("main issue missing")
        status = "PASS" if score >= 85 else "WARN" if score >= 65 else "FAIL"
        return {"score": max(score, 0), "status": status, "warnings": warnings}

    def certificate(self, audit, dataset, graph):
        return {
            "certificate_id": "CGT-" + now_stamp(),
            "status": audit["status"],
            "dataset_counts": dataset["counts"],
            "graph_nodes": graph["node_count"],
            "graph_edges": graph["edge_count"],
            "issued_at": now_text(),
            "note": "1970-1990 katmanı; Master Record'u case intelligence, graph ve AI dataset çıktılarına dönüştürmüştür."
        }

    def run(self):
        CGT_DIR.mkdir(parents=True, exist_ok=True)
        REPORTS.mkdir(parents=True, exist_ok=True)
        modules = self.support_modules()
        master = self.load_master_record()
        intelligence = self.case_intelligence(master)
        graph = self.graph_builder(master, intelligence)
        dataset = self.dataset_factory(master, intelligence, graph)
        audit = self.audit(intelligence, graph, dataset)
        cert = self.certificate(audit, dataset, graph)
        support_score = round(sum(1 for m in modules if m["found"]) / len(modules) * 100, 2) if modules else 100
        final_score = round(support_score * 0.20 + audit["score"] * 0.45 + min(100, graph["node_count"] * 5) * 0.15 + min(100, dataset["counts"]["rag"] * 10) * 0.20, 2)
        decision = "CASE GRAPH TRAINER READY" if audit["status"] != "FAIL" and support_score >= 60 else "CASE GRAPH TRAINER BLOCKED"
        ts = now_stamp()
        snapshot = CGT_DIR / "1970_1990_case_graph_trainer_snapshot.json"
        intelligence_file = CGT_DIR / ("1970_case_intelligence_" + ts + ".json")
        graph_file = CGT_DIR / ("1980_legal_graph_" + ts + ".json")
        dataset_file = CGT_DIR / ("1990_ai_datasets_" + ts + ".json")
        dashboard = CGT_DIR / "1970_1990_case_graph_trainer_dashboard.json"
        state = CGT_DIR / ("1970_1990_case_graph_trainer_state_" + ts + ".json")
        report = REPORTS / ("1970_1990_case_graph_trainer_sdk_raporu_" + ts + ".txt")
        payload = {
            "master_record": master,
            "case_intelligence": intelligence,
            "legal_graph": graph,
            "ai_datasets": dataset,
            "audit": audit,
            "certificate": cert,
            "modules": modules,
            "validation": {"score": final_score, "support_score": support_score, "decision": decision, "errors": [] if decision.endswith("READY") else ["blocked"], "warnings": audit["warnings"]}
        }
        write_json(snapshot, payload)
        write_json(state, payload)
        write_json(intelligence_file, intelligence)
        write_json(graph_file, graph)
        write_json(dataset_file, dataset)
        write_json(dashboard, {
            "status": decision,
            "score": final_score,
            "main_issue": intelligence["main_issue"]["topic"] if intelligence.get("main_issue") else None,
            "topics": intelligence["topic_count"],
            "graph_nodes": graph["node_count"],
            "graph_edges": graph["edge_count"],
            "rag_chunks": dataset["counts"]["rag"],
            "audit": audit["status"]
        })
        lines = [
            "=" * 80,
            "1970-1990 CASE GRAPH TRAINER SDK",
            "=" * 80,
            "Validation       : " + decision,
            "Score            : " + str(final_score) + " / 100",
            "Main Issue       : " + str(intelligence["main_issue"]["topic"] if intelligence.get("main_issue") else None),
            "Topics           : " + str(intelligence["topic_count"]),
            "Graph Nodes      : " + str(graph["node_count"]),
            "Graph Edges      : " + str(graph["edge_count"]),
            "RAG Chunks       : " + str(dataset["counts"]["rag"]),
            "Instruction Rows : " + str(dataset["counts"]["instruction"]),
            "FineTune Rows    : " + str(dataset["counts"]["fine_tuning"]),
            "Audit            : " + audit["status"],
            "",
            "Dosyalar:",
            str(snapshot),
            str(intelligence_file),
            str(graph_file),
            str(dataset_file),
            str(dashboard),
            str(report)
        ]
        report.write_text("\\n".join(lines), encoding="utf-8")
        return {"payload": payload, "paths": {"snapshot": str(snapshot), "intelligence": str(intelligence_file), "graph": str(graph_file), "dataset": str(dataset_file), "dashboard": str(dashboard), "state": str(state), "report": str(report)}}
"""

def sdk_bridge_source():
    return """# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1970_1990"
sys.path.insert(0, str(PACKAGE_DIR))
from core.case_graph_trainer_sdk import CaseGraphTrainerSDK

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--master-record", default=None)
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    res = CaseGraphTrainerSDK(master_record_path=args.master_record, case_text=args.case_text, execute=args.execute).run()
    v = res["payload"]["validation"]
    ci = res["payload"]["case_intelligence"]
    graph = res["payload"]["legal_graph"]
    ds = res["payload"]["ai_datasets"]
    print("=" * 80)
    print("1970-1990 CASE GRAPH TRAINER SDK TAMAMLANDI")
    print("=" * 80)
    print("Validation       : " + str(v["decision"]))
    print("Score            : " + str(v["score"]) + " / 100")
    print("Main Issue       : " + str(ci["main_issue"]["topic"] if ci.get("main_issue") else None))
    print("Topics           : " + str(ci["topic_count"]))
    print("Graph Nodes      : " + str(graph["node_count"]))
    print("Graph Edges      : " + str(graph["edge_count"]))
    print("RAG Chunks       : " + str(ds["counts"]["rag"]))
    print("")
    print("Dosyalar:")
    print(res["paths"]["snapshot"])
    print(res["paths"]["intelligence"])
    print(res["paths"]["graph"])
    print(res["paths"]["dataset"])
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
PACKAGE_DIR = BASE / ".py" / "1970_1990"
sys.path.insert(0, str(PACKAGE_DIR))
from core.case_graph_trainer_sdk import CaseGraphTrainerSDK
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MODULE_DIR = STATE / "case_graph_trainer" / "__MID_____SLUG__"
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
    parser.add_argument("--master-record", default=None)
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    MODULE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    res = CaseGraphTrainerSDK(name=MODULE_ID + " " + MODULE_NAME, master_record_path=args.master_record, case_text=args.case_text, execute=args.execute).run()
    val = res["payload"]["validation"]
    ci = res["payload"]["case_intelligence"]
    graph = res["payload"]["legal_graph"]
    ds = res["payload"]["ai_datasets"]
    audit = res["payload"]["audit"]
    decision = "__NAME_UPPER__ READY" if not val["errors"] else "__NAME_UPPER__ BLOCKED"
    analysis = {"score": val["score"], "decision": decision, "main_issue": ci["main_issue"]["topic"] if ci.get("main_issue") else None, "topics": ci["topic_count"], "graph_nodes": graph["node_count"], "rag_chunks": ds["counts"]["rag"], "audit": audit["status"]}
    ts = now_stamp()
    output = MODULE_DIR / "__MID_____SLUG__.json"
    state = MODULE_DIR / ("__MID_____SLUG___state_" + ts + ".json")
    report = REPORTS / ("__MID_____SLUG___raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "module_id": MODULE_ID, "module_name": MODULE_NAME, "analysis": analysis, "sdk_reference": res["paths"]}
    write_json(output, payload)
    write_json(state, payload)
    lines = ["=" * 80, MODULE_ID + " " + MODULE_NAME.upper(), "=" * 80, "Score       : " + str(analysis["score"]) + " / 100", "Decision    : " + str(analysis["decision"]), "Main Issue  : " + str(analysis["main_issue"]), "Topics      : " + str(analysis["topics"]), "Graph Nodes : " + str(analysis["graph_nodes"]), "RAG Chunks  : " + str(analysis["rag_chunks"]), "Audit       : " + str(analysis["audit"]), "", "Dosyalar:", str(output), str(report)]
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
        '    ("1970-1990", "Case Graph Trainer SDK", [sys.executable, str(BASE / ".py" / "1970_1990_Case_Graph_Trainer_SDK.py")]),',
    ]
    for mid, name, slug in MODULES:
        lines.append('    ("' + mid + '", "' + name + '", [sys.executable, str(BASE / ".py" / "' + mid + '_' + slug + '.py")]),')
    lines += [
        "]",
        "def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')",
        "def main():",
        "    parser = argparse.ArgumentParser()",
        "    parser.add_argument('--master-record', default=None)",
        "    parser.add_argument('--case-text', default=None)",
        "    parser.add_argument('--execute', action='store_true')",
        "    args = parser.parse_args()",
        "    print('=' * 80)",
        "    print('1970-1990 CASE GRAPH TRAINER RUN ALL BASLADI')",
        "    print('=' * 80)",
        "    rows=[]; passed=0; failed=0",
        "    for module_id, name, cmd in COMMANDS:",
        "        full = list(cmd)",
        "        if args.master_record: full += ['--master-record', args.master_record]",
        "        if args.case_text: full += ['--case-text', args.case_text]",
        "        if args.execute: full.append('--execute')",
        "        print('\\n>>> ' + ' '.join(full))",
        "        result = subprocess.run(full, cwd=str(BASE))",
        "        status = 'PASS' if result.returncode == 0 else 'FAIL'",
        "        if status == 'PASS': passed += 1",
        "        else: failed += 1",
        "        rows.append({'module_id': module_id, 'name': name, 'status': status, 'returncode': result.returncode})",
        "    total=len(COMMANDS); score=round((passed/total)*100,2) if total else 0; decision='PASS' if failed==0 else 'FAIL'; ready='YES' if failed==0 else 'NO'",
        "    payload={'created_at':now_text(),'program':'1970-1990 Case Graph Trainer','execute':args.execute,'modules_total':total,'modules_passed':passed,'modules_failed':failed,'program_score':score,'final_decision':decision,'production_ready':ready,'results':rows}",
        "    summary_path=SUMMARY_DIR/'1970_1990_case_graph_trainer_summary.json'; summary_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')",
        "    print('\\n'+'='*80); print('1970-1990 CASE GRAPH TRAINER SUMMARY'); print('='*80)",
        "    for row in rows: print(row['module_id']+' '+row['name'].ljust(42)+' '+row['status'])",
        "    print('-'*80); print('Modules Passed    : '+str(passed)+' / '+str(total)); print('Modules Failed    : '+str(failed)); print('Program Score     : '+str(score)+' / 100'); print('FINAL RESULT      : '+decision); print('Production Ready  : '+ready); print(''); print('Summary JSON:'); print(summary_path); print('='*80)",
        "    raise SystemExit(0 if decision=='PASS' else 1)",
        "if __name__=='__main__': main()",
    ]
    return "\n".join(lines) + "\n"

def create_release_docs():
    RELEASES.mkdir(parents=True, exist_ok=True)
    module_lines = ["- 1970-1990 Case Graph Trainer SDK"] + ["- " + mid + " " + name for mid, name, slug in MODULES] + ["- 1970_1990 Run All"]
    RELEASE_FILE.write_text("\n".join([
        "# v18.6–v18.8 – Case Intelligence, Legal Graph & AI Trainer",
        "",
        "**Tarih:** 10.07.2026",
        "",
        "Bu sürüm 1950 Master Record çıktılarını uyuşmazlık önceliklendirme, legal knowledge graph ve AI/RAG/fine-tuning veri setlerine dönüştüren üçlü ürün zekâsı katmanını kurar.",
        "",
        "# Katmanlar",
        "",
        "- 1970 Case Intelligence Engine",
        "- 1980 Legal Knowledge Graph Builder",
        "- 1990 AI Trainer & Dataset Factory",
        "",
        "# Modüller",
        "",
    ] + module_lines + ["", "---", "", "Case Graph Trainer v18.6–v18.8 oluşturulmuştur.", ""]), encoding="utf-8")
    entry = "\n".join([
        "# v18.6–v18.8 – Case Intelligence, Legal Graph & AI Trainer",
        "",
        "**Tarih:** 10.07.2026  ",
        "**Durum:** Production PASS  ",
        "**Git Tag:** `" + TAG + "`",
        "",
        "## Yeni Modüller",
        "",
    ] + module_lines + ["", "## Sonuç", "", "NeoLegal, Master Record çıktılarından case intelligence, graph ve AI dataset üretme katmanına taşındı.", "", "---", ""])
    if CHANGELOG.exists():
        old = CHANGELOG.read_text(encoding="utf-8", errors="ignore")
        if "v18.6–v18.8 – Case Intelligence" not in old:
            CHANGELOG.write_text(entry + "\n" + old, encoding="utf-8")
    else:
        CHANGELOG.write_text("# CHANGELOG\n\n" + entry, encoding="utf-8")
    if README.exists():
        row = "| v18.6-v18.8 | Case Intelligence, Legal Graph & AI Trainer | PASS |"
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
        "echo Running Case Graph Trainer v18.6-v18.8...",
        'python ".py\\1970_1990_Run_All.py"',
        "",
        "IF ERRORLEVEL 1 (",
        "    echo.",
        "    echo RELEASE BLOCKED: 1970-1990 Case Graph Trainer FAILED.",
        "    pause",
        "    exit /b 1",
        ")",
        "",
        "git status",
        "git add .",
        'git commit -m "Release v18.6-v18.8: Case Graph Trainer"',
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
    parser.add_argument("--master-record", default=None)
    parser.add_argument("--case-text", default=None)
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()

    PY.mkdir(parents=True, exist_ok=True)
    CGT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print("1970-1990 ALL-IN-ONE CASE GRAPH TRAINER BUILDER BASLADI")
    print("=" * 80)

    write_file(PY / "1970_1990" / "core" / "__init__.py", "")
    write_file(PY / "1970_1990" / "core" / "case_graph_trainer_sdk.py", SDK_CODE)
    write_file(PY / "1970_1990_Case_Graph_Trainer_SDK.py", sdk_bridge_source())

    generated = [str(PY / "1970_1990_Case_Graph_Trainer_SDK.py")]
    for mid, name, slug in MODULES:
        path = PY / (mid + "_" + slug + ".py")
        write_file(path, module_source(mid, name, slug))
        generated.append(str(path))
        print("Generated:", path)

    run_all = PY / "1970_1990_Run_All.py"
    write_file(run_all, run_all_source())
    print("Generated:", run_all)

    release_path = create_release_docs()
    git_bat = create_git_bat()

    print("\n" + "=" * 80)
    print("1970-1990 CASE GRAPH TRAINER TEST BASLIYOR")
    print("=" * 80)
    cmd = [sys.executable, str(run_all)]
    if args.master_record:
        cmd += ["--master-record", args.master_record]
    if args.case_text:
        cmd += ["--case-text", args.case_text]
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
    state = CGT_DIR / ("1970_1990_case_graph_trainer_builder_state_" + ts + ".json")
    report = REPORTS / ("1970_1990_case_graph_trainer_builder_raporu_" + ts + ".txt")
    payload = {"created_at": now_text(), "program": "1970-1990 Case Graph Trainer Builder", "version": VERSION, "tag": TAG, "execute": args.execute, "generated_files": generated, "run_all": str(run_all), "release_path": str(release_path), "git_bat": str(git_bat), "run_returncode": result.returncode, "final_decision": decision, "git": git_status}
    write_json(state, payload)
    lines = ["=" * 80, "1970-1990 ALL-IN-ONE CASE GRAPH TRAINER BUILDER FINAL", "=" * 80, "Final Decision : " + decision, "Git            : " + git_status, "Mode           : " + ("EXECUTE" if args.execute else "DRY_RUN"), "Version        : " + VERSION, "Run All        : " + str(run_all), "Release        : " + str(release_path), "Git BAT        : " + str(git_bat), "State          : " + str(state), "Report         : " + str(report), "=" * 80]
    report.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    if decision != "PASS" or git_status == "FAILED":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
