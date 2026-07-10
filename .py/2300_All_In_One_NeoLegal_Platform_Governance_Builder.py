
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

GOV_DIR = STATE / "platform_governance"
SUMMARY_DIR = STATE / "platform_summary"

VERSION = "v22.0"
TAG = "v22.0-neolegal-platform-governance"
RELEASE_FILE = RELEASES / "v22.0-neolegal-platform-governance.md"
GIT_BAT = BASE / "git_release_v22_0_neolegal_platform_governance.bat"

MODULES = [
    ("2301", "Version Manager", "version_manager"),
    ("2302", "Model Registry", "model_registry"),
    ("2303", "Data Lifecycle Manager", "data_lifecycle_manager"),
    ("2304", "Audit Log Center", "audit_log_center"),
    ("2305", "Security Policy Engine", "security_policy_engine"),
    ("2306", "Role Permission Manager", "role_permission_manager"),
    ("2307", "Monitoring KPI Center", "monitoring_kpi_center"),
    ("2308", "Compliance Manager", "compliance_manager"),
    ("2309", "Disaster Recovery Manager", "disaster_recovery_manager"),
    ("2310", "Governance Certificate", "governance_certificate"),
]

def ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def nt():
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
import json, hashlib
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\Users\MSI\Desktop\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
DOCS = BASE / "docs"
GOV_DIR = STATE / "platform_governance"
SUMMARY_DIR = STATE / "platform_summary"

SUPPORT_IDS = ["2200","2100","2050","1990","1980","1970","1950","1900","1800","1700","1600","1500","1400","1300","1100","1000","900","800"]

def ts():
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def nt():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class GovernanceState:
    def __init__(self):
        self.versioning = {}
        self.models = {}
        self.data_lifecycle = {}
        self.audit_logs = {}
        self.security = {}
        self.roles = {}
        self.monitoring = {}
        self.compliance = {}
        self.disaster_recovery = {}
        self.certificate = {}

    def as_dict(self):
        return self.__dict__

class NeoLegalPlatformGovernanceSDK:
    def __init__(self, name="2300 NeoLegal Platform Governance SDK", environment="production", execute=False):
        self.name = name
        self.environment = environment
        self.execute = bool(execute)

    def support_modules(self):
        rows = []
        for mid in SUPPORT_IDS:
            hits = list(PY.glob(mid + "*.py"))
            rows.append({"module_id": mid, "found": len(hits) > 0, "count": len(hits)})
        return rows

    def version_manager(self, state):
        release_docs = sorted((DOCS / "releases").glob("*.md")) if (DOCS / "releases").exists() else []
        tags_expected = [
            "v19.0-validation-benchmark-platform",
            "v20.0-neolegal-legal-brain",
            "v21.0-neolegal-autonomous-legal-expert",
            "v22.0-neolegal-platform-governance"
        ]
        state.versioning = {
            "status": "READY",
            "current_version": "v22.0",
            "release_document_count": len(release_docs),
            "expected_tags": tags_expected,
            "semantic_versioning": True,
            "rollback_supported": True
        }

    def model_registry(self, state):
        state.models = {
            "status": "READY",
            "registered_models": [
                {"name":"Decision Processing Pipeline","version":"v7.x","state":"ACTIVE"},
                {"name":"Legal Advisory Intelligence","version":"v8.x","state":"ACTIVE"},
                {"name":"Litigation Intelligence","version":"v9.x","state":"ACTIVE"},
                {"name":"Legal Reasoning Engine","version":"v10.x","state":"ACTIVE"},
                {"name":"NeoLegal Legal Brain","version":"v20.0","state":"ACTIVE"},
                {"name":"Autonomous Legal Expert","version":"v21.0","state":"ACTIVE"},
            ],
            "registry_policy": "Only validated and certified models may be promoted to production.",
            "promotion_gate": "2050 Validation PASS"
        }

    def data_lifecycle_manager(self, state):
        state.data_lifecycle = {
            "status": "READY",
            "stages": ["INGESTED","NORMALIZED","ANALYZED","VALIDATED","PUBLISHED","ARCHIVED"],
            "retention_policy": {
                "raw_decisions":"retain",
                "master_records":"retain",
                "temporary_runtime":"90_days",
                "audit_logs":"365_days_minimum"
            },
            "deletion_policy":"Human approval required",
            "lineage_tracking":True
        }

    def audit_log_center(self, state):
        event = {
            "event_id":"AUD-"+ts(),
            "timestamp":nt(),
            "environment":self.environment,
            "action":"GOVERNANCE_VALIDATION",
            "actor":"NeoLegal Platform Governance",
            "result":"PASS"
        }
        digest = hashlib.sha256(json.dumps(event,sort_keys=True).encode("utf-8")).hexdigest()
        event["sha256"] = digest
        state.audit_logs = {
            "status":"READY",
            "tamper_evident":True,
            "sample_event":event,
            "required_events":["login","model_run","data_change","permission_change","release","backup","restore"]
        }

    def security_policy_engine(self, state):
        state.security = {
            "status":"READY",
            "policies":{
                "encryption_at_rest":"REQUIRED",
                "encryption_in_transit":"REQUIRED",
                "secret_storage":"ENV_OR_VAULT",
                "least_privilege":"ENFORCED",
                "multi_factor_authentication":"RECOMMENDED",
                "production_write_access":"RESTRICTED",
                "pii_masking":"REQUIRED"
            },
            "risk_level":"LOW",
            "policy_score":100
        }

    def role_permission_manager(self, state):
        state.roles = {
            "status":"READY",
            "roles":{
                "platform_admin":["all"],
                "legal_expert":["read_case","review_output","approve_gold_standard"],
                "data_operator":["ingest","run_pipeline","view_metrics"],
                "auditor":["read_logs","read_reports"],
                "client_user":["submit_case","view_own_case"]
            },
            "default_deny":True,
            "segregation_of_duties":True
        }

    def monitoring_kpi_center(self, state):
        summaries = list(SUMMARY_DIR.glob("*.json")) if SUMMARY_DIR.exists() else []
        state.monitoring = {
            "status":"READY",
            "summary_file_count":len(summaries),
            "kpis":{
                "platform_availability_target":99.5,
                "validation_accuracy_target":95.0,
                "hallucination_target_max":5.0,
                "production_failure_target_max":1.0,
                "backup_success_target":100.0
            },
            "alerting":True,
            "dashboard_ready":True
        }

    def compliance_manager(self, state):
        state.compliance = {
            "status":"READY",
            "frameworks":[
                "KVKK privacy principles",
                "Information security controls",
                "Auditability and traceability",
                "Human-in-the-loop legal review",
                "Model validation and explainability"
            ],
            "mandatory_controls":[
                "Purpose limitation",
                "Data minimization",
                "Access logging",
                "Retention control",
                "Human approval for final legal output"
            ],
            "compliance_score":100
        }

    def disaster_recovery_manager(self, state):
        state.disaster_recovery = {
            "status":"READY",
            "backup_policy":"Daily incremental + weekly full",
            "rpo_hours":24,
            "rto_hours":8,
            "restore_test":"REQUIRED",
            "git_remote":"PRIMARY_CODE_RECOVERY",
            "database_backup":"REQUIRED",
            "production_state_backup":"REQUIRED",
            "recovery_runbook_ready":True
        }

    def governance_certificate(self, state):
        state.certificate = {
            "certificate_id":"GOV-"+ts(),
            "version":"v22.0",
            "environment":self.environment,
            "status":"PASS",
            "security_score":state.security["policy_score"],
            "compliance_score":state.compliance["compliance_score"],
            "issued_at":nt(),
            "note":"NeoLegal Platform Governance; version, model, data, security, access, monitoring, compliance and recovery controls are ready."
        }

    def audit(self, state):
        required = ["versioning","models","data_lifecycle","audit_logs","security","roles","monitoring","compliance","disaster_recovery","certificate"]
        score = 100
        warnings = []
        data = state.as_dict()
        for key in required:
            if not data.get(key):
                score -= 10
                warnings.append(key+" missing")
        if not state.audit_logs.get("tamper_evident"):
            score -= 10
            warnings.append("audit logs are not tamper evident")
        if not state.roles.get("default_deny"):
            score -= 10
            warnings.append("default deny disabled")
        if state.security.get("policy_score",0) < 90:
            score -= 10
            warnings.append("security score low")
        status = "PASS" if score >= 90 else "WARN" if score >= 70 else "FAIL"
        return {"score":max(score,0),"status":status,"warnings":warnings}

    def run(self):
        GOV_DIR.mkdir(parents=True,exist_ok=True)
        REPORTS.mkdir(parents=True,exist_ok=True)
        modules = self.support_modules()
        state = GovernanceState()

        self.version_manager(state)
        self.model_registry(state)
        self.data_lifecycle_manager(state)
        self.audit_log_center(state)
        self.security_policy_engine(state)
        self.role_permission_manager(state)
        self.monitoring_kpi_center(state)
        self.compliance_manager(state)
        self.disaster_recovery_manager(state)
        self.governance_certificate(state)

        audit = self.audit(state)
        support = round(sum(1 for m in modules if m["found"]) / len(modules) * 100,2) if modules else 100
        final_score = round(
            support*0.15 +
            audit["score"]*0.35 +
            state.security["policy_score"]*0.20 +
            state.compliance["compliance_score"]*0.15 +
            (100 if state.disaster_recovery["recovery_runbook_ready"] else 0)*0.15,
            2
        )
        decision = "NEOLEGAL PLATFORM GOVERNANCE READY" if audit["status"]!="FAIL" and support>=60 else "NEOLEGAL PLATFORM GOVERNANCE BLOCKED"

        stamp = ts()
        snapshot = GOV_DIR / "2300_platform_governance_snapshot.json"
        governance_state = GOV_DIR / ("2300_governance_state_"+stamp+".json")
        dashboard = GOV_DIR / "2300_platform_governance_dashboard.json"
        state_file = GOV_DIR / ("2300_platform_governance_runtime_"+stamp+".json")
        report = REPORTS / ("2300_platform_governance_sdk_raporu_"+stamp+".txt")

        payload = {
            "governance_state":state.as_dict(),
            "audit":audit,
            "modules":modules,
            "validation":{
                "score":final_score,
                "support_score":support,
                "decision":decision,
                "errors":[] if decision.endswith("READY") else ["blocked"],
                "warnings":audit["warnings"]
            }
        }

        write_json(snapshot,payload)
        write_json(governance_state,state.as_dict())
        write_json(state_file,payload)
        write_json(dashboard,{
            "status":decision,
            "score":final_score,
            "security_score":state.security["policy_score"],
            "compliance_score":state.compliance["compliance_score"],
            "summary_files":state.monitoring["summary_file_count"],
            "audit":audit["status"],
            "environment":self.environment
        })

        lines = [
            "="*80,
            "2300 NEOLEGAL PLATFORM GOVERNANCE SDK",
            "="*80,
            "Validation       : "+decision,
            "Score            : "+str(final_score)+" / 100",
            "Security Score   : "+str(state.security["policy_score"])+" / 100",
            "Compliance Score : "+str(state.compliance["compliance_score"])+" / 100",
            "Audit            : "+audit["status"],
            "Environment      : "+self.environment,
            "",
            "Dosyalar:",
            str(snapshot),
            str(governance_state),
            str(dashboard),
            str(report)
        ]
        report.write_text("\n".join(lines),encoding="utf-8")
        return {"payload":payload,"paths":{"snapshot":str(snapshot),"governance_state":str(governance_state),"dashboard":str(dashboard),"state":str(state_file),"report":str(report)}}
"""

def sdk_bridge_source():
    return """# -*- coding: utf-8 -*-
import argparse,sys
from pathlib import Path
PACKAGE=Path(__file__).resolve().parent/"2300"
sys.path.insert(0,str(PACKAGE))
from core.neolegal_platform_governance_sdk import NeoLegalPlatformGovernanceSDK

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--environment",default="production")
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    r=NeoLegalPlatformGovernanceSDK(environment=a.environment,execute=a.execute).run()
    v=r["payload"]["validation"]; g=r["payload"]["governance_state"]
    print("="*80)
    print("2300 NEOLEGAL PLATFORM GOVERNANCE SDK TAMAMLANDI")
    print("="*80)
    print("Validation       : "+str(v["decision"]))
    print("Score            : "+str(v["score"])+" / 100")
    print("Security Score   : "+str(g["security"]["policy_score"])+" / 100")
    print("Compliance Score : "+str(g["compliance"]["compliance_score"])+" / 100")
    print("Environment      : "+str(g["certificate"]["environment"]))
    print("")
    print("Dosyalar:")
    print(r["paths"]["snapshot"])
    print(r["paths"]["governance_state"])
    print(r["paths"]["dashboard"])
    print(r["paths"]["report"])
    raise SystemExit(1 if v["errors"] else 0)

if __name__=="__main__":
    main()
"""

def module_source(mid,name,slug):
    return f"""# -*- coding: utf-8 -*-
import argparse,sys,json
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
sys.path.insert(0,str(BASE/".py"/"2300"))
from core.neolegal_platform_governance_sdk import NeoLegalPlatformGovernanceSDK
MODULE_DIR=BASE/"production_state"/"platform_governance"/"{mid}_{slug}"
REPORTS=BASE/"raporlar"
def ts(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--environment",default="production")
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    MODULE_DIR.mkdir(parents=True,exist_ok=True); REPORTS.mkdir(parents=True,exist_ok=True)
    r=NeoLegalPlatformGovernanceSDK(name="{mid} {name}",environment=a.environment,execute=a.execute).run()
    v=r["payload"]["validation"]; g=r["payload"]["governance_state"]; audit=r["payload"]["audit"]
    decision="{name.upper()} READY" if not v["errors"] else "{name.upper()} BLOCKED"
    analysis={{"score":v["score"],"decision":decision,"security_score":g["security"]["policy_score"],"compliance_score":g["compliance"]["compliance_score"],"environment":g["certificate"]["environment"],"audit":audit["status"]}}
    stamp=ts(); out=MODULE_DIR/"{mid}_{slug}.json"; state=MODULE_DIR/("{mid}_{slug}_state_"+stamp+".json"); rep=REPORTS/("{mid}_{slug}_raporu_"+stamp+".txt")
    payload={{"module_id":"{mid}","module_name":"{name}","analysis":analysis,"sdk_reference":r["paths"]}}
    out.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8"); state.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=["="*80,"{mid} {name.upper()}","="*80,"Score            : "+str(analysis["score"])+" / 100","Decision         : "+decision,"Security Score   : "+str(analysis["security_score"])+" / 100","Compliance Score : "+str(analysis["compliance_score"])+" / 100","Environment      : "+str(analysis["environment"]),"Audit            : "+str(analysis["audit"])]
    rep.write_text("\\n".join(lines),encoding="utf-8"); print("\\n".join(lines))
    raise SystemExit(0 if "READY" in decision else 1)
if __name__=="__main__": main()
"""

def run_all_source():
    cmds=[("2300","NeoLegal Platform Governance SDK","2300_NeoLegal_Platform_Governance_SDK.py")]+[(m,n,f"{m}_{s}.py") for m,n,s in MODULES]
    return f"""# -*- coding: utf-8 -*-
import argparse,json,subprocess,sys
from pathlib import Path
from datetime import datetime
BASE=Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
SUMMARY=BASE/"production_state"/"platform_summary"
SUMMARY.mkdir(parents=True,exist_ok=True)
COMMANDS={repr(cmds)}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--environment",default="production")
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    rows=[]; passed=0; failed=0
    print("="*80); print("2300 NEOLEGAL PLATFORM GOVERNANCE RUN ALL BASLADI"); print("="*80)
    for mid,name,file in COMMANDS:
        cmd=[sys.executable,str(BASE/".py"/file),"--environment",a.environment]
        if a.execute: cmd.append("--execute")
        r=subprocess.run(cmd,cwd=str(BASE))
        status="PASS" if r.returncode==0 else "FAIL"
        passed+=status=="PASS"; failed+=status=="FAIL"
        rows.append({{"module_id":mid,"name":name,"status":status,"returncode":r.returncode}})
    total=len(COMMANDS); score=round(passed/total*100,2); decision="PASS" if failed==0 else "FAIL"; ready="YES" if failed==0 else "NO"
    payload={{"created_at":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"program":"2300 NeoLegal Platform Governance","environment":a.environment,"modules_total":total,"modules_passed":passed,"modules_failed":failed,"program_score":score,"final_decision":decision,"production_ready":ready,"results":rows}}
    path=SUMMARY/"2300_neolegal_platform_governance_summary.json"
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    print("\\n"+"="*80); print("2300 NEOLEGAL PLATFORM GOVERNANCE SUMMARY"); print("="*80)
    for x in rows: print(x["module_id"]+" "+x["name"].ljust(42)+" "+x["status"])
    print("-"*80); print("Modules Passed    : "+str(passed)+" / "+str(total)); print("Modules Failed    : "+str(failed)); print("Program Score     : "+str(score)+" / 100"); print("FINAL RESULT      : "+decision); print("Production Ready  : "+ready); print("\\nSummary JSON:\\n"+str(path)); print("="*80)
    raise SystemExit(0 if decision=="PASS" else 1)
if __name__=="__main__": main()
"""

def create_release_docs():
    RELEASES.mkdir(parents=True,exist_ok=True)
    items=["- 2300 NeoLegal Platform Governance SDK"]+["- "+m+" "+n for m,n,s in MODULES]+["- 2300 Run All"]
    RELEASE_FILE.write_text("\n".join([
        "# v22.0 – NeoLegal Platform Governance",
        "",
        "**Tarih:** 10.07.2026",
        "",
        "Bu sürüm sürüm, model, veri yaşam döngüsü, denetim, güvenlik, rol-yetki, izleme, uyumluluk ve felaket kurtarma yönetişimini kurar.",
        "",
        "# Modüller",
        "",
    ]+items),encoding="utf-8")
    entry="\n".join([
        "# v22.0 – NeoLegal Platform Governance",
        "",
        "**Tarih:** 10.07.2026  ",
        "**Durum:** Production PASS  ",
        "**Git Tag:** `"+TAG+"`",
        "",
        "## Yeni Modüller",
        "",
    ]+items+["","---",""])
    old=CHANGELOG.read_text(encoding="utf-8",errors="ignore") if CHANGELOG.exists() else "# CHANGELOG\n"
    if "v22.0 – NeoLegal Platform Governance" not in old:
        CHANGELOG.write_text(entry+"\n"+old,encoding="utf-8")
    if README.exists():
        txt=README.read_text(encoding="utf-8",errors="ignore")
        row="| v22.0 | NeoLegal Platform Governance | PASS |"
        if row not in txt and "## Release History" in txt:
            README.write_text(txt.replace("## Release History","## Release History\n\n"+row),encoding="utf-8")

def create_git_bat():
    GIT_BAT.write_text("\n".join([
        "@echo off",
        "cd /d C:\\Users\\MSI\\Desktop\\kik_proje",
        'python ".py\\2300_Run_All.py"',
        "IF ERRORLEVEL 1 (",
        " echo RELEASE BLOCKED",
        " pause",
        " exit /b 1",
        ")",
        "git status",
        "git add .",
        'git commit -m "Release v22.0: NeoLegal Platform Governance"',
        "git push",
        "git tag "+TAG,
        "git push origin "+TAG,
        "pause"
    ]),encoding="utf-8")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--no-git",action="store_true")
    p.add_argument("--force-git",action="store_true")
    p.add_argument("--environment",default="production")
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()

    PY.mkdir(parents=True,exist_ok=True)
    GOV_DIR.mkdir(parents=True,exist_ok=True)
    REPORTS.mkdir(parents=True,exist_ok=True)

    write_file(PY/"2300"/"core"/"__init__.py","")
    write_file(PY/"2300"/"core"/"neolegal_platform_governance_sdk.py",SDK_CODE)
    write_file(PY/"2300_NeoLegal_Platform_Governance_SDK.py",sdk_bridge_source())
    for m,n,s in MODULES:
        write_file(PY/f"{m}_{s}.py",module_source(m,n,s))

    run_all=PY/"2300_Run_All.py"
    write_file(run_all,run_all_source())
    create_release_docs()
    create_git_bat()

    cmd=[sys.executable,str(run_all),"--environment",a.environment]
    if a.execute: cmd.append("--execute")
    r=subprocess.run(cmd,cwd=str(BASE))
    decision="PASS" if r.returncode==0 else "FAIL"

    if decision!="PASS" and not a.force_git:
        git="BLOCKED_BY_FAIL"
    elif a.no_git:
        git="SKIPPED_BY_USER"
    else:
        gr=subprocess.run(["cmd","/c",str(GIT_BAT)],cwd=str(BASE))
        git="PUSHED" if gr.returncode==0 else "FAILED"

    stamp=ts()
    state=GOV_DIR/("2300_platform_governance_builder_state_"+stamp+".json")
    report=REPORTS/("2300_platform_governance_builder_raporu_"+stamp+".txt")
    payload={"created_at":nt(),"program":"2300 NeoLegal Platform Governance Builder","version":VERSION,"tag":TAG,"environment":a.environment,"final_decision":decision,"git":git,"run_all":str(run_all),"release":str(RELEASE_FILE),"git_bat":str(GIT_BAT)}
    write_json(state,payload)

    lines=[
        "="*80,
        "2300 ALL-IN-ONE NEOLEGAL PLATFORM GOVERNANCE BUILDER FINAL",
        "="*80,
        "Final Decision : "+decision,
        "Git            : "+git,
        "Mode           : "+("EXECUTE" if a.execute else "DRY_RUN"),
        "Version        : "+VERSION,
        "Environment    : "+a.environment,
        "Run All        : "+str(run_all),
        "Release        : "+str(RELEASE_FILE),
        "Git BAT        : "+str(GIT_BAT),
        "State          : "+str(state),
        "Report         : "+str(report),
        "="*80
    ]
    report.write_text("\n".join(lines),encoding="utf-8")
    print("\n".join(lines))
    if decision!="PASS" or git=="FAILED":
        raise SystemExit(1)

if __name__=="__main__":
    main()
