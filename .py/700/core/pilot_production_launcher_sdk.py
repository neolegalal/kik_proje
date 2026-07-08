# -*- coding: utf-8 -*-
import json, sqlite3
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
PILOT_DIR = STATE / "pilot_production"
SUMMARY_DIR = STATE / "platform_summary"
PIPELINE_FILES = ['168_Production.py', '169_DB_Import.py', '170_WEB_RAG_Export.py', '172_AI_Quality.py', '173_Master_Acceptance.py', '177_Legal_Accuracy.py', '181_Final_Master_Production_Controller.py', '190_Production_Supervisor.py', '195_Runtime_Monitor.py', '550_Run_All.py', '600_670_Run_All.py']
PIPELINE_MODULE_IDS = ['168', '169', '170', '172', '173', '177', '181', '190', '195', '550', '600']

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

class PilotProductionLauncherSDK:
    def __init__(self, name='700 Pilot Production Launcher SDK', batch_size=10, dry_run=True):
        self.name=name
        self.batch_size=int(batch_size)
        self.dry_run=bool(dry_run)
    def discover_db(self):
        candidates=[]
        for name in ('kik.db','kik_proje.db','hukuki_kartlar.db'):
            p=BASE/name
            candidates.append({'path':str(p),'exists':p.exists(),'size_bytes':p.stat().st_size if p.exists() else 0})
        return candidates
    def discover_tables(self, db_path):
        if not db_path or not Path(db_path).exists(): return []
        try:
            con=sqlite3.connect(str(db_path)); cur=con.cursor()
            rows=cur.execute("select name from sqlite_master where type='table'").fetchall()
            tables=[]
            for (name,) in rows:
                try: count=cur.execute('select count(*) from '+name).fetchone()[0]
                except Exception: count=None
                tables.append({'table':name,'count':count})
            con.close(); return tables
        except Exception as e:
            return [{'error':str(e)}]
    def select_batch(self, db_path, tables):
        if not db_path or not Path(db_path).exists():
            return [{'pilot_id':i+1,'source':'synthetic','status':'QUEUED'} for i in range(self.batch_size)]
        preferred=['hukuki_kartlar','kararlar','decisions','kik_kararlari']
        table=None
        existing=[t.get('table') for t in tables if t.get('table')]
        for p in preferred:
            if p in existing: table=p; break
        if not table and existing: table=existing[0]
        if not table: return [{'pilot_id':i+1,'source':'synthetic','status':'QUEUED'} for i in range(self.batch_size)]
        batch=[]
        try:
            con=sqlite3.connect(str(db_path)); cur=con.cursor()
            rows=cur.execute('select rowid,* from '+table+' limit ?', (self.batch_size,)).fetchall()
            cols=[d[0] for d in cur.description]
            con.close()
            for idx,row in enumerate(rows, start=1):
                item=dict(zip(cols,row))
                batch.append({'pilot_id':idx,'source_table':table,'rowid':item.get('rowid'),'status':'QUEUED','keys':list(item.keys())[:20]})
        except Exception as e:
            batch=[{'pilot_id':i+1,'source':'synthetic','status':'QUEUED','error':str(e)} for i in range(self.batch_size)]
        if not batch: batch=[{'pilot_id':i+1,'source':'synthetic','status':'QUEUED'} for i in range(self.batch_size)]
        return batch
    def discover_pipeline(self):
        rows=[]
        for idx, file in enumerate(PIPELINE_FILES):
            p=PY/file
            module_id = PIPELINE_MODULE_IDS[idx] if idx < len(PIPELINE_MODULE_IDS) else file.split('_')[0]
            fuzzy = list(PY.glob(str(module_id) + '*.py'))
            exists = p.exists() or len(fuzzy) > 0
            rows.append({'file':file,'module_id':module_id,'path':str(p),'exists':exists,'exact_exists':p.exists(),'fuzzy_count':len(fuzzy),'fuzzy_sample':[str(x) for x in fuzzy[:5]]})
        return rows
    def validate(self, dbs, pipeline, batch):
        db_found=any(d['exists'] for d in dbs)
        pipe_found=sum(1 for p in pipeline if p['exists'])
        pipe_total=len(pipeline)
        pipe_score=round((pipe_found/pipe_total)*100,2) if pipe_total else 100
        db_score=100 if db_found else 80
        batch_score=100 if batch else 0
        score=round(pipe_score*0.55 + db_score*0.25 + batch_score*0.20,2)
        errors=[]; warnings=[]
        if pipe_score < 50: warnings.append('Ana production pipeline dosyaları exact/fuzzy aramada sınırlı bulundu; dry-run pilot yine de kurulabilir.')
        if not db_found: warnings.append('DB bulunamadı; synthetic pilot queue ile devam edildi.')
        decision='PILOT PRODUCTION CONTEXT READY' if not errors else 'PILOT PRODUCTION CONTEXT BLOCKED'
        return {'score':score,'pipeline_score':pipe_score,'db_score':db_score,'batch_score':batch_score,'decision':decision,'errors':errors,'warnings':warnings}
    def plan(self, batch, validation):
        queue=[dict(item, runtime_status='PLANNED_DRY_RUN' if self.dry_run else 'PLANNED_EXECUTION') for item in batch]
        mode='PILOT_DRY_RUN' if self.dry_run else 'PILOT_EXECUTION_READY'
        if validation['errors']: mode='PAUSED'
        return {'mode':mode,'batch_size':len(queue),'queue':queue,'message':str(len(queue))+' pilot production item planned.'}
    def run(self):
        PILOT_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
        dbs=self.discover_db(); db_path=next((d['path'] for d in dbs if d['exists']), None)
        tables=self.discover_tables(db_path); batch=self.select_batch(db_path,tables); pipeline=self.discover_pipeline(); validation=self.validate(dbs,pipeline,batch); plan=self.plan(batch,validation)
        payload={'module':self.name,'created_at':now_text(),'dry_run':self.dry_run,'databases':dbs,'tables':tables,'pipeline':pipeline,'validation':validation,'plan':plan}
        ts=now_stamp()
        snapshot=PILOT_DIR/'700_pilot_production_snapshot.json'
        dashboard=PILOT_DIR/'700_pilot_production_dashboard.json'
        state=PILOT_DIR/('700_pilot_production_state_'+ts+'.json')
        queue_file=PILOT_DIR/('700_pilot_queue_'+ts+'.json')
        report=REPORTS/('700_pilot_production_sdk_raporu_'+ts+'.txt')
        write_json(snapshot,payload); write_json(state,payload); write_json(queue_file, plan['queue'])
        write_json(dashboard, {'status':validation['decision'],'score':validation['score'],'mode':plan['mode'],'batch_size':plan['batch_size'],'errors':len(validation['errors']),'warnings':len(validation['warnings'])})
        lines=['='*80,'700 PILOT PRODUCTION LAUNCHER SDK','='*80,'Validation : '+str(validation['decision']),'Score      : '+str(validation['score'])+' / 100','Mode       : '+str(plan['mode']),'Batch Size : '+str(plan['batch_size']),'','Dosyalar:',str(snapshot),str(dashboard),str(queue_file),str(report)]
        report.write_text('\n'.join(lines), encoding='utf-8')
        return {'payload':payload,'paths':{'snapshot':str(snapshot),'dashboard':str(dashboard),'queue':str(queue_file),'state':str(state),'report':str(report)}}
