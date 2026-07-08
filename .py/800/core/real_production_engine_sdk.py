# -*- coding: utf-8 -*-
import json, sqlite3
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
PY = BASE / ".py"
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
REAL_DIR = STATE / "real_production_engine"
SUMMARY_DIR = STATE / "platform_summary"
PIPELINE_MODULE_IDS = ['168', '169', '170', '172', '173', '177', '181', '190', '195', '700', '550', '600']

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

class RealProductionEngineSDK:
    def __init__(self, name='800 Real Production Engine SDK', batch_size=10, dry_run=True):
        self.name=name
        self.batch_size=int(batch_size)
        self.dry_run=bool(dry_run)
    def discover_db(self):
        rows=[]
        for name in ('kik.db','kik_proje.db','hukuki_kartlar.db'):
            p=BASE/name
            rows.append({'path':str(p),'exists':p.exists(),'size_bytes':p.stat().st_size if p.exists() else 0})
        return rows
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
            return [{'production_id':i+1,'source':'synthetic','status':'REAL_QUEUE_READY'} for i in range(self.batch_size)]
        preferred=['hukuki_kartlar','kararlar','decisions','kik_kararlari']
        existing=[t.get('table') for t in tables if t.get('table')]
        table=None
        for p in preferred:
            if p in existing: table=p; break
        if not table and existing: table=existing[0]
        if not table: return [{'production_id':i+1,'source':'synthetic','status':'REAL_QUEUE_READY'} for i in range(self.batch_size)]
        batch=[]
        try:
            con=sqlite3.connect(str(db_path)); cur=con.cursor()
            rows=cur.execute('select rowid,* from '+table+' limit ?', (self.batch_size,)).fetchall()
            cols=[d[0] for d in cur.description]
            con.close()
            for idx,row in enumerate(rows, start=1):
                item=dict(zip(cols,row))
                batch.append({'production_id':idx,'source_table':table,'rowid':item.get('rowid'),'status':'REAL_QUEUE_READY','keys':list(item.keys())[:20]})
        except Exception as e:
            batch=[{'production_id':i+1,'source':'synthetic','status':'REAL_QUEUE_READY','error':str(e)} for i in range(self.batch_size)]
        return batch or [{'production_id':i+1,'source':'synthetic','status':'REAL_QUEUE_READY'} for i in range(self.batch_size)]
    def discover_pipeline(self):
        rows=[]
        for mid in PIPELINE_MODULE_IDS:
            hits=list(PY.glob(str(mid)+'*.py'))
            rows.append({'module_id':mid,'exists':len(hits)>0,'count':len(hits),'sample':[str(x) for x in hits[:5]]})
        return rows
    def validate(self, dbs, tables, pipeline, batch):
        db_found=any(d['exists'] for d in dbs)
        table_count=len([t for t in tables if t.get('table')])
        pipe_found=sum(1 for p in pipeline if p['exists'])
        pipe_score=round((pipe_found/len(pipeline))*100,2) if pipeline else 100
        db_score=100 if db_found else 80
        table_score=100 if table_count>0 else 80
        batch_score=100 if batch else 0
        score=round(pipe_score*0.45 + db_score*0.2 + table_score*0.15 + batch_score*0.2,2)
        errors=[]; warnings=[]
        if pipe_score < 50: errors.append('Gerçek production pipeline modüllerinin çoğu bulunamadı.')
        if not db_found: warnings.append('DB bulunamadı; synthetic real-production queue ile devam edildi.')
        if self.dry_run: warnings.append('Dry-run modunda gerçek üretim çağrısı yapılmadı.')
        decision='REAL PRODUCTION CONTEXT READY' if not errors else 'REAL PRODUCTION CONTEXT BLOCKED'
        return {'score':score,'pipeline_score':pipe_score,'db_score':db_score,'table_score':table_score,'batch_score':batch_score,'decision':decision,'errors':errors,'warnings':warnings}
    def plan(self, batch, pipeline, validation):
        queue=[]
        for item in batch:
            queue.append(dict(item, runtime_status='REAL_DRY_RUN_PLANNED' if self.dry_run else 'REAL_EXECUTION_PLANNED'))
        mode='REAL_PRODUCTION_DRY_RUN' if self.dry_run else 'REAL_PRODUCTION_EXECUTION_READY'
        if validation['errors']: mode='PAUSED'
        chain=[p for p in pipeline if p['exists']]
        return {'mode':mode,'batch_size':len(queue),'queue':queue,'chain_modules':chain,'message':str(len(queue))+' real production item planned across '+str(len(chain))+' pipeline module groups.'}
    def run(self):
        REAL_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
        dbs=self.discover_db(); db_path=next((d['path'] for d in dbs if d['exists']), None)
        tables=self.discover_tables(db_path); batch=self.select_batch(db_path,tables); pipeline=self.discover_pipeline(); validation=self.validate(dbs,tables,pipeline,batch); plan=self.plan(batch,pipeline,validation)
        payload={'module':self.name,'created_at':now_text(),'dry_run':self.dry_run,'databases':dbs,'tables':tables,'pipeline':pipeline,'validation':validation,'plan':plan}
        ts=now_stamp()
        snapshot=REAL_DIR/'800_real_production_engine_snapshot.json'
        dashboard=REAL_DIR/'800_real_production_engine_dashboard.json'
        state=REAL_DIR/('800_real_production_engine_state_'+ts+'.json')
        queue_file=REAL_DIR/('800_real_production_queue_'+ts+'.json')
        report=REPORTS/('800_real_production_engine_sdk_raporu_'+ts+'.txt')
        write_json(snapshot,payload); write_json(state,payload); write_json(queue_file, plan['queue'])
        write_json(dashboard, {'status':validation['decision'],'score':validation['score'],'mode':plan['mode'],'batch_size':plan['batch_size'],'chain_modules':len(plan['chain_modules']),'errors':len(validation['errors']),'warnings':len(validation['warnings'])})
        lines=['='*80,'800 REAL PRODUCTION ENGINE SDK','='*80,'Validation : '+str(validation['decision']),'Score      : '+str(validation['score'])+' / 100','Mode       : '+str(plan['mode']),'Batch Size : '+str(plan['batch_size']),'Chain Mods : '+str(len(plan['chain_modules'])),'','Dosyalar:',str(snapshot),str(dashboard),str(queue_file),str(report)]
        report.write_text('\n'.join(lines), encoding='utf-8')
        return {'payload':payload,'paths':{'snapshot':str(snapshot),'dashboard':str(dashboard),'queue':str(queue_file),'state':str(state),'report':str(report)}}
