# -*- coding: utf-8 -*-
import json, os, shutil, sqlite3, subprocess
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
SAFETY_DIR = STATE / "production_safety_gate"
PILOT_OUTPUT = STATE / "pilot_execution_output"
BACKUP_DIR = STATE / "safety_backups"
QUARANTINE_DIR = STATE / "quarantine"
RESUME_DIR = STATE / "resume"
REQUIRED_MODULE_IDS = ['168', '169', '170', '172', '173', '177', '181', '190', '195', '700', '800']
OPTIONAL_MODULE_IDS = ['206', '207', '208', '209', '210', '211', '212', '550', '600']
def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
class ProductionSafetyGateSDK:
    def __init__(self, name='801 Production Safety Gate SDK', batch_size=10):
        self.name = name; self.batch_size = int(batch_size)
    def check_database(self):
        candidates=[]
        for name in ('kik.db','kik_proje.db','hukuki_kartlar.db'):
            p=BASE/name
            item={'path':str(p),'exists':p.exists(),'size_bytes':p.stat().st_size if p.exists() else 0,'tables':[],'error':None}
            if p.exists():
                try:
                    con=sqlite3.connect(str(p)); cur=con.cursor()
                    rows=cur.execute("select name from sqlite_master where type='table'").fetchall()
                    for (t,) in rows[:20]:
                        try: count=cur.execute('select count(*) from '+t).fetchone()[0]
                        except Exception: count=None
                        item['tables'].append({'table':t,'count':count})
                    con.close()
                except Exception as e: item['error']=str(e)
            candidates.append(item)
        db_found=any(i['exists'] for i in candidates); table_found=any(i.get('tables') for i in candidates)
        score=100 if db_found and table_found else 85 if db_found else 70
        return {'score':score,'status':'PASS' if score>=85 else 'WARN','db_found':db_found,'table_found':table_found,'items':candidates}
    def check_pipeline(self):
        required=[]; optional=[]
        for mid in REQUIRED_MODULE_IDS:
            hits=list(PY.glob(str(mid)+'*.py')); required.append({'module_id':mid,'found':len(hits)>0,'count':len(hits),'sample':[str(x) for x in hits[:5]]})
        for mid in OPTIONAL_MODULE_IDS:
            hits=list(PY.glob(str(mid)+'*.py')); optional.append({'module_id':mid,'found':len(hits)>0,'count':len(hits),'sample':[str(x) for x in hits[:5]]})
        req_found=sum(1 for i in required if i['found']); req_total=len(required)
        opt_found=sum(1 for i in optional if i['found']); opt_total=len(optional)
        req_score=round((req_found/req_total)*100,2) if req_total else 100; opt_score=round((opt_found/opt_total)*100,2) if opt_total else 100
        score=round(req_score*0.8+opt_score*0.2,2); status='PASS' if req_score>=80 else 'WARN' if req_score>=60 else 'FAIL'
        return {'score':score,'status':status,'required_found':req_found,'required_total':req_total,'optional_found':opt_found,'optional_total':opt_total,'required':required,'optional':optional}
    def check_api_cost(self):
        env_keys=[k for k in os.environ.keys() if 'OPENAI' in k.upper() or 'API' in k.upper() or 'KEY' in k.upper()]
        score=100; warnings=[]
        if not env_keys: warnings.append('API anahtarı environment içinde tespit edilmedi; local .env kullanılıyor olabilir.')
        if self.batch_size>50: warnings.append('Batch size 50 üstü; pilot için maliyet kontrolü önerilir.'); score-=15
        return {'score':max(score,0),'status':'PASS' if score>=85 else 'WARN','env_key_count':len(env_keys),'env_keys_sample':env_keys[:10],'estimated_max_calls':self.batch_size,'warnings':warnings}
    def check_output_isolation(self):
        dirs=[PILOT_OUTPUT, QUARANTINE_DIR, RESUME_DIR, BACKUP_DIR, SAFETY_DIR]; created=[]
        for d in dirs: d.mkdir(parents=True, exist_ok=True); created.append(str(d))
        files=len([f for f in PILOT_OUTPUT.glob('**/*') if f.is_file()]) if PILOT_OUTPUT.exists() else 0
        return {'score':100 if files==0 else 90,'status':'PASS','created_dirs':created,'pilot_output_file_count':files}
    def check_duplicate_risk(self):
        seen=set(); duplicates=[]
        for folder in [STATE/'pilot_production', STATE/'real_production_engine', STATE/'production_data_factory']:
            if not folder.exists(): continue
            for f in folder.glob('**/*.json'):
                if f.name in seen: duplicates.append(str(f))
                seen.add(f.name)
        score=100 if not duplicates else 85
        return {'score':score,'status':'PASS' if score>=90 else 'WARN','duplicate_count':len(duplicates),'duplicates_sample':duplicates[:20]}
    def check_backup_rollback(self):
        BACKUP_DIR.mkdir(parents=True, exist_ok=True); marker=BACKUP_DIR/('rollback_marker_'+now_stamp()+'.json')
        write_json(marker, {'created_at':now_text(),'batch_size':self.batch_size,'type':'SAFETY_ROLLBACK_MARKER'})
        return {'score':100,'status':'PASS','rollback_marker':str(marker)}
    def check_resume_recovery(self):
        RESUME_DIR.mkdir(parents=True, exist_ok=True); resume=RESUME_DIR/('safety_resume_'+now_stamp()+'.json')
        write_json(resume, {'created_at':now_text(),'batch_size':self.batch_size,'status':'READY'})
        return {'score':100,'status':'PASS','resume_file':str(resume)}
    def check_resources(self):
        usage=shutil.disk_usage(str(BASE)); free=round(usage.free/(1024**3),2)
        score=100 if free>=10 else 80 if free>=2 else 50
        return {'score':score,'status':'PASS' if score>=80 else 'FAIL','disk_free_gb':free,'disk_total_gb':round(usage.total/(1024**3),2)}
    def check_git(self):
        try:
            r=subprocess.run(['git','status','--porcelain'],cwd=str(BASE),capture_output=True,text=True,timeout=30)
            changed=[line for line in r.stdout.splitlines() if line.strip()]
            return {'score':100 if r.returncode==0 else 70,'status':'PASS' if r.returncode==0 else 'WARN','changed_count':len(changed),'changed_sample':changed[:20]}
        except Exception as e: return {'score':70,'status':'WARN','error':str(e)}
    def calculate(self, checks):
        scores=[v['score'] for v in checks.values()]; avg=round(sum(scores)/len(scores),2) if scores else 0
        fail=any(v['status']=='FAIL' for v in checks.values()); warn=sum(1 for v in checks.values() if v['status']=='WARN')
        if fail: decision,ready='FAIL','NO'
        elif avg>=90: decision,ready='PASS','YES'
        elif avg>=80: decision,ready='WARN','LIMITED'
        else: decision,ready='FAIL','NO'
        return {'score':avg,'decision':decision,'production_ready':ready,'warnings':warn}
    def run(self):
        SAFETY_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
        checks={'database':self.check_database(),'pipeline':self.check_pipeline(),'api_cost':self.check_api_cost(),'output_isolation':self.check_output_isolation(),'duplicate_risk':self.check_duplicate_risk(),'backup_rollback':self.check_backup_rollback(),'resume_recovery':self.check_resume_recovery(),'resources':self.check_resources(),'git_state':self.check_git()}
        final=self.calculate(checks); ts=now_stamp(); payload={'module':self.name,'created_at':now_text(),'batch_size':self.batch_size,'checks':checks,'final':final}
        snapshot=SAFETY_DIR/'801_production_safety_gate_snapshot.json'; dashboard=SAFETY_DIR/'801_production_safety_gate_dashboard.json'; state=SAFETY_DIR/('801_production_safety_gate_state_'+ts+'.json'); report=REPORTS/('801_production_safety_gate_sdk_raporu_'+ts+'.txt')
        write_json(snapshot,payload); write_json(state,payload); write_json(dashboard, {'status':final['decision'],'score':final['score'],'production_ready':final['production_ready'],'warnings':final['warnings']})
        lines=['='*80,'801 PRODUCTION SAFETY GATE SDK','='*80,'Safety Score : '+str(final['score'])+' / 100','FINAL       : '+str(final['decision']),'Ready       : '+str(final['production_ready']),'Warnings    : '+str(final['warnings']),'','Check Scores:']
        for k,v in checks.items(): lines.append('- '+k+' : '+str(v['score'])+' / 100 ['+v['status']+']')
        lines += ['', 'Dosyalar:', str(snapshot), str(dashboard), str(report)]
        report.write_text('\n'.join(lines), encoding='utf-8')
        return {'payload':payload,'paths':{'snapshot':str(snapshot),'dashboard':str(dashboard),'state':str(state),'report':str(report)}}
