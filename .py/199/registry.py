# -*- coding: utf-8 -*-
from config import PY_DIR, STATE_DIR, REPORT_DIR, REGISTRY_DIR, SERVICE_REGISTRY_FILE
from utils import now_stamp, ensure_dirs, disk_free_gb, find_scripts, file_info, write_json

SERVICES = {
    "core": {"181":"Production Controller","192":"Resume Engine","193":"Smart Resume Validation","194":"Production Guardian","195":"Runtime Monitor"},
    "certification": {"196":"Production Certification Suite","196B":"Dynamic Certification"},
    "recovery": {"197":"Recovery Manager"},
    "orchestration": {"198":"Queue / Worker / Controlled Execution","199":"Production Manager"},
    "pipeline": {"168":"Production","188":"Auto Cleaner","172":"AI Quality","175":"Coverage","176":"Priority","177":"Legal Accuracy","185":"Self Healing","178":"Merge","179":"Optimize","180":"Complexity","169":"DB Import","170":"Export","173":"Acceptance","182":"Drift","183":"Sampling","184":"Dashboard","190":"Supervisor"}
}

def run():
    ensure_dirs(STATE_DIR, REPORT_DIR, REGISTRY_DIR)
    ts = now_stamp()
    registry = {"module":"199 Package Service Registry","disk_free_gb":disk_free_gb(PY_DIR.parent),"categories":{},"flat_services":{}}
    for cat, services in SERVICES.items():
        registry["categories"][cat] = {}
        for prefix, label in services.items():
            scripts = find_scripts(PY_DIR, prefix)
            primary = scripts[0] if scripts else None
            item = {"prefix":prefix,"label":label,"category":cat,"status":"FOUND" if primary else "MISSING","primary_script":file_info(primary) if primary else None,"script_count":len(scripts)}
            registry["categories"][cat][prefix] = item
            registry["flat_services"][prefix] = item
    found = sum(1 for x in registry["flat_services"].values() if x["status"]=="FOUND")
    total = len(registry["flat_services"])
    score = 100 if found == total else max(0, 100 - (total-found)*5)
    decision = "REGISTRY READY" if found == total else "REGISTRY REVIEW"
    result = {"score":score,"decision":decision,"errors":[],"warnings":[]}
    state = STATE_DIR / f"199_pkg_registry_state_{ts}.json"
    report = REPORT_DIR / f"199_pkg_registry_raporu_{ts}.txt"
    write_json(SERVICE_REGISTRY_FILE, registry)
    write_json(state, {"registry":registry,"result":result})
    report.write_text("\n".join(["="*80,"199 PACKAGE - SERVICE REGISTRY","="*80,f"Score    : {score} / 100",f"Decision : {decision}",f"Found    : {found} / {total}","", "Dosyalar:",str(SERVICE_REGISTRY_FILE),str(state),str(report)]), encoding="utf-8")
    return {"registry":registry,"result":result,"paths":{"registry":str(SERVICE_REGISTRY_FILE),"state":str(state),"report":str(report)}}
