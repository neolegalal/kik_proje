# -*- coding: utf-8 -*-
import json, os, shutil, sqlite3, subprocess
from pathlib import Path
from datetime import datetime
BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
MASTER_DIR = STATE / "production_master"
SUMMARY_DIR = STATE / "platform_summary"
CORE_MODULE_IDS = ['168', '169', '170', '172', '173', '177', '181', '190', '195', '700', '800', '801']
PLATFORM_MODULE_IDS = ['400', '500', '550', '600', '206', '207', '208', '209', '210', '211', '212']
def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def safe_read(path):
    path=Path(path)
    if not path.exists(): return ''
    for enc in ('utf-8','utf-8-sig','cp1254','latin-1'):
        try: return path.read_text(encoding=enc, errors='ignore')
        except Exception: pass
    return ''
def safe_json(path):
    try: return json.loads(safe_read(path))
    except Exception: return None
def write_json(path,data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
class ProductionMasterSDK:
    def __init__(self, name='900 Production Master SDK', target=100000, batch_size=10, dry_run=True):
        self.name=name; self.target=int(target); self.batch_size=int(batch_size); self.dry_run=bool(dry_run)
    def discover_db(self):
        rows=[]
        for name in ('kik.db','kik_proje.db','hukuki_kartlar.db'):
            p=BASE/name
            item={'path':str(p),'exists':p.exists(),'size_bytes':p.stat().st_size if p.exists() else 0,'tables':[],'error':None}
            if p.exists():
                try:
                    con=sqlite3.connect(str(p)); cur=con.cursor(); tables=cur.execute("select name from sqlite_master where type='table'").fetchall()
                    for (t,) in tables[:30]:
                        try: count=cur.execute('select count(*) from '+t).fetchone()[0]
                        except Exception: count=None
                        item['tables'].append({'table':t,'count':count})
                    con.close()
                except Exception as e: item['error']=str(e)
            rows.append(item)
        return rows
    def discover_modules(self):
        def scan(ids):
            out=[]
            for mid in ids:
                hits=list(PY.glob(str(mid)+'*.py'))
                out.append({'module_id':mid,'found':len(hits)>0,'count':len(hits),'sample':[str(x) for x in hits[:5]]})
            return out
        return {'core':scan(CORE_MODULE_IDS),'platform':scan(PLATFORM_MODULE_IDS)}
    def discover_summaries(self):
        rows=[]
        if SUMMARY_DIR.exists():
            for f in SUMMARY_DIR.glob('*_summary.json'):
                data=safe_json(f) or {}
                rows.append({'path':str(f),'final_decision':data.get('final_decision'),'score':data.get('program_score') or data.get('production_score'),'ready':data.get('production_ready')})
        return rows
    def build_queue_plan(self, dbs):
        db_found=any(d['exists'] for d in dbs)
        available=0
        for db in dbs:
            for t in db.get('tables',[]):
                if isinstance(t.get('count'), int): available=max(available, t['count'])
        planned=min(self.batch_size, available if available else self.batch_size)
        queue=[{'queue_id':i+1,'status':'MASTER_DRY_RUN_PLANNED' if self.dry_run else 'MASTER_EXECUTION_PLANNED'} for i in range(planned)]
        return {'db_found':db_found,'available_count':available,'planned_batch':planned,'target':self.target,'queue':queue}
    def estimate_cost(self):
        # Conservative placeholder: actual cost will be filled by API runtime later.
        estimated_tokens_per_item=2500
        estimated_total_tokens=self.batch_size*estimated_tokens_per_item
        return {'estimated_tokens_per_item':estimated_tokens_per_item,'estimated_total_tokens':estimated_total_tokens,'estimated_api_calls':self.batch_size,'mode':'ESTIMATE_ONLY'}
    def plan_workers(self):
        workers=1 if self.batch_size<=10 else 2 if self.batch_size<=100 else 4
        return {'recommended_workers':workers,'batch_size':self.batch_size,'strategy':'controlled_pilot' if self.batch_size<=100 else 'scaled_production'}
    def progress(self, queue_plan):
        completed=0; planned=queue_plan['planned_batch']
        pct=round((completed/planned)*100,2) if planned else 0
        return {'target':self.target,'planned_batch':planned,'completed':completed,'progress_percent':pct,'eta':'not_started'}
    def validate(self, dbs, modules, summaries, queue_plan):
        core_found=sum(1 for x in modules['core'] if x['found']); core_total=len(modules['core'])
        plat_found=sum(1 for x in modules['platform'] if x['found']); plat_total=len(modules['platform'])
        core_score=round((core_found/core_total)*100,2) if core_total else 100
        platform_score=round((plat_found/plat_total)*100,2) if plat_total else 100
        db_score=100 if any(d['exists'] for d in dbs) else 80
        summary_pass=sum(1 for s in summaries if s.get('final_decision')=='PASS')
        summary_score=100 if summary_pass>=5 else 85 if summary_pass>=2 else 70
        queue_score=100 if queue_plan['planned_batch']>0 else 0
        score=round(core_score*0.35 + platform_score*0.20 + db_score*0.15 + summary_score*0.15 + queue_score*0.15,2)
        errors=[]; warnings=[]
        if core_score<70: errors.append('Core production modules are incomplete.')
        if platform_score<60: warnings.append('Some platform support modules are missing.')
        if not any(d['exists'] for d in dbs): warnings.append('DB not found; master will use synthetic queue until DB is available.')
        if self.dry_run: warnings.append('Master is running in dry-run mode.')
        decision='PRODUCTION MASTER READY' if not errors else 'PRODUCTION MASTER BLOCKED'
        return {'score':score,'core_score':core_score,'platform_score':platform_score,'db_score':db_score,'summary_score':summary_score,'queue_score':queue_score,'decision':decision,'errors':errors,'warnings':warnings}
    def run(self):
        MASTER_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
        dbs=self.discover_db(); modules=self.discover_modules(); summaries=self.discover_summaries(); queue_plan=self.build_queue_plan(dbs); cost=self.estimate_cost(); workers=self.plan_workers(); progress=self.progress(queue_plan); validation=self.validate(dbs,modules,summaries,queue_plan)
        payload={'module':self.name,'created_at':now_text(),'target':self.target,'batch_size':self.batch_size,'dry_run':self.dry_run,'databases':dbs,'modules':modules,'summaries':summaries,'queue_plan':queue_plan,'cost':cost,'workers':workers,'progress':progress,'validation':validation}
        ts=now_stamp(); snapshot=MASTER_DIR/'900_production_master_snapshot.json'; dashboard=MASTER_DIR/'900_production_master_dashboard.json'; state=MASTER_DIR/('900_production_master_state_'+ts+'.json'); report=REPORTS/('900_production_master_sdk_raporu_'+ts+'.txt')
        write_json(snapshot,payload); write_json(state,payload); write_json(dashboard, {'status':validation['decision'],'score':validation['score'],'target':self.target,'batch_size':self.batch_size,'mode':'DRY_RUN' if self.dry_run else 'EXECUTE','planned_batch':queue_plan['planned_batch'],'workers':workers['recommended_workers'],'warnings':len(validation['warnings']),'errors':len(validation['errors'])})
        lines=['='*80,'900 PRODUCTION MASTER SDK','='*80,'Validation : '+str(validation['decision']),'Score      : '+str(validation['score'])+' / 100','Target     : '+str(self.target),'Batch Size : '+str(self.batch_size),'Mode       : '+('DRY_RUN' if self.dry_run else 'EXECUTE'),'Workers    : '+str(workers['recommended_workers']),'Planned    : '+str(queue_plan['planned_batch']),'','Dosyalar:',str(snapshot),str(dashboard),str(report)]
        report.write_text('\n'.join(lines), encoding='utf-8')
        return {'payload':payload,'paths':{'snapshot':str(snapshot),'dashboard':str(dashboard),'state':str(state),'report':str(report)}}
