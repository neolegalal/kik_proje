# -*- coding: utf-8 -*-
import sqlite3
from config import BASE_DIR, STATE_DIR, REPORT_DIR, SERVICE_REGISTRY_FILE, QUEUE_FILE, WORKER_FILE, MIN_DISK_GB
from utils import now_stamp, ensure_dirs, disk_free_gb, safe_json, latest_file, safe_read, write_json

def discover_db():
    candidates = [p for p in BASE_DIR.rglob("*.db") if "kik" in p.name.lower()]
    candidates = list(set(candidates))
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        return {"status":"FAIL","count":0,"message":"DB yok"}
    db = candidates[0]
    try:
        conn = sqlite3.connect(str(db)); cur = conn.cursor()
        tables = [x[0] for x in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        table = "hukuki_kartlar" if "hukuki_kartlar" in tables else (tables[0] if tables else None)
        if not table:
            return {"status":"FAIL","path":str(db),"count":0,"message":"Tablo yok"}
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        conn.close()
        return {"status":"PASS","path":str(db),"table":table,"count":count,"message":f"DB OK: {count}"}
    except Exception as e:
        return {"status":"FAIL","path":str(db),"count":0,"message":str(e)}

def registry_health():
    reg = safe_json(SERVICE_REGISTRY_FILE)
    if not reg:
        return {"status":"FAIL","found":0,"total":0,"message":"Registry yok"}
    flat = reg.get("flat_services",{})
    total = len(flat); found = sum(1 for x in flat.values() if x.get("status")=="FOUND")
    return {"status":"PASS" if found==total and total else "WARNING","found":found,"total":total,"message":f"{found}/{total} servis"}

def queue_health():
    q = safe_json(QUEUE_FILE)
    if not q:
        return {"status":"WARNING","total":0,"message":"Queue yok"}
    jobs = q.get("jobs",[])
    counts = {}
    for j in jobs:
        counts[j.get("status","UNKNOWN")] = counts.get(j.get("status","UNKNOWN"),0)+1
    return {"status":"PASS","total":len(jobs),"waiting":counts.get("WAITING",0),"running":counts.get("RUNNING",0),"finished":counts.get("FINISHED",0),"failed":counts.get("FAILED",0),"message":f"Queue total={len(jobs)}"}

def worker_health():
    w = safe_json(WORKER_FILE)
    if not w:
        return {"status":"WARNING","total":0,"message":"Worker yok"}
    workers = w.get("workers",[])
    counts = {}
    for x in workers:
        counts[x.get("status","UNKNOWN")] = counts.get(x.get("status","UNKNOWN"),0)+1
    return {"status":"PASS","total":len(workers),"idle":counts.get("IDLE",0),"running":counts.get("RUNNING",0),"message":f"Workers total={len(workers)}"}

def latest_health(pattern, tokens, label):
    f = latest_file(STATE_DIR, pattern)
    if not f:
        return {"status":"WARNING","message":f"{label} yok"}
    txt = safe_read(f).lower()
    ok = any(t.lower() in txt for t in tokens)
    return {"status":"PASS" if ok else "WARNING","file":str(f),"message":label}

def run():
    ensure_dirs(STATE_DIR, REPORT_DIR)
    ts = now_stamp()
    free = disk_free_gb(BASE_DIR)
    parts = {
        "registry":registry_health(),
        "db":discover_db(),
        "disk":{"status":"PASS" if free>=MIN_DISK_GB else "FAIL","free_gb":free,"message":f"Disk {free} GB"},
        "queue":queue_health(),
        "worker":worker_health(),
        "recovery":latest_health("197_v4_recovery_manager_state_*.json",["recovery clean"],"Recovery"),
        "orchestrator":latest_health("199_v3_orchestrator_state_*.json",["orchestrator certified"],"Orchestrator")
    }
    score = 100
    errors=[]; warnings=[]
    for k,v in parts.items():
        if v.get("status")=="FAIL":
            score-=20; errors.append(k)
        elif v.get("status")=="WARNING":
            score-=5; warnings.append(k)
    score=max(0,score)
    decision = "PLATFORM BLOCKED" if errors else ("PLATFORM READY" if score>=90 else "PLATFORM REVIEW")
    result={"score":score,"decision":decision,"errors":errors,"warnings":warnings}
    state=STATE_DIR/f"199_pkg_health_state_{ts}.json"
    report=REPORT_DIR/f"199_pkg_health_raporu_{ts}.txt"
    write_json(state,{"health":parts,"result":result})
    report.write_text("\n".join(["="*80,"199 PACKAGE - PLATFORM HEALTH","="*80,f"Score    : {score} / 100",f"Decision : {decision}",f"Errors   : {len(errors)}",f"Warnings : {len(warnings)}",f"DB Count : {parts['db'].get('count')}",f"Queue    : W={parts['queue'].get('waiting')} R={parts['queue'].get('running')} F={parts['queue'].get('finished')} Fail={parts['queue'].get('failed')}",f"Workers  : idle={parts['worker'].get('idle')} running={parts['worker'].get('running')} total={parts['worker'].get('total')}","", "Dosyalar:",str(state),str(report)]), encoding="utf-8")
    return {"health":parts,"result":result,"paths":{"state":str(state),"report":str(report)}}
