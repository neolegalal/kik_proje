# -*- coding: utf-8 -*-
import json
from pathlib import Path
from datetime import datetime

BASE = Path(r"C:\\Users\\MSI\\Desktop\\kik_proje")
STATE = BASE / "production_state"
REPORTS = BASE / "raporlar"
IPE_DIR = STATE / "intelligent_production_engine"
SOURCE_CHECKS = [('production_os', 'production_os'), ('data_factory', 'production_data_factory'), ('factory_runtime', 'production_factory_runtime'), ('scheduler', 'scheduler'), ('execution', 'execution'), ('automation', 'automation'), ('self_healing', 'self_healing'), ('learning', 'learning'), ('ai_orchestrator', 'ai_orchestrator'), ('platform_summary', 'platform_summary')]

def now_stamp(): return datetime.now().strftime('%Y%m%d_%H%M%S')
def now_text(): return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
def safe_read(path):
    path = Path(path)
    if not path.exists(): return ''
    for enc in ('utf-8','utf-8-sig','cp1254','latin-1'):
        try: return path.read_text(encoding=enc, errors='ignore')
        except Exception: pass
    return ''
def safe_json(path):
    try: return json.loads(safe_read(path))
    except Exception: return None
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

class IntelligentProductionEngineSDK:
    def __init__(self, name='600 Intelligent Production Engine SDK'):
        self.name = name
    def discover_sources(self):
        rows=[]
        for key, folder in SOURCE_CHECKS:
            folder_path = STATE / folder
            exists = folder_path.exists()
            files = [i for i in folder_path.glob('**/*') if i.is_file()] if exists else []
            rows.append({'key':key,'folder':str(folder_path),'exists':exists,'file_count':len(files),'json_count':len([i for i in files if i.suffix.lower()=='.json'])})
        return rows
    def discover_production_inputs(self):
        candidates=[]
        for p in [BASE/'kik.db', BASE/'kik_proje.db', STATE/'platform_summary'/'550_production_factory_runtime_summary.json', STATE/'platform_summary'/'500_production_data_factory_summary.json', STATE/'platform_summary'/'400_production_os_summary.json']:
            candidates.append({'path':str(p),'exists':p.exists(),'size_bytes':p.stat().st_size if p.exists() else 0})
        return candidates
    def validate(self, sources, inputs):
        found=sum(1 for i in sources if i['exists'])
        total=len(sources)
        source_score=round((found/total)*100,2) if total else 100
        input_found=sum(1 for i in inputs if i['exists'])
        input_score=100 if input_found>=3 else 90 if input_found==2 else 80 if input_found==1 else 65
        score=round(source_score*0.65 + input_score*0.35, 2)
        errors=[]; warnings=[]
        if source_score < 60: errors.append('IPE kaynaklarının çoğu bulunamadı.')
        if input_found < 2: warnings.append('Gerçek üretim inputları sınırlı; küçük batch ile başlanmalı.')
        decision='INTELLIGENT PRODUCTION ENGINE CONTEXT READY' if not errors else 'INTELLIGENT PRODUCTION ENGINE CONTEXT BLOCKED'
        return {'score':score,'source_score':source_score,'input_score':input_score,'decision':decision,'errors':errors,'warnings':warnings}
    def plan(self, sources, inputs, validation):
        operations=[]
        for src in sources:
            operations.append({'operation':'BIND_'+src['key'].upper(),'status':'READY' if src['exists'] else 'MISSING','file_count':src['file_count'],'json_count':src['json_count']})
        operations.append({'operation':'DECIDE_PRODUCTION_STRATEGY','status':'PLANNED'})
        operations.append({'operation':'OPTIMIZE_BATCH_ORDER','status':'PLANNED'})
        operations.append({'operation':'OPTIMIZE_AI_COST_TOKEN','status':'PLANNED'})
        operations.append({'operation':'COORDINATE_WORKER_CLUSTER','status':'PLANNED'})
        operations.append({'operation':'ENABLE_KNOWLEDGE_CACHE','status':'PLANNED'})
        operations.append({'operation':'ENABLE_HUMAN_REVIEW_GATE','status':'PLANNED'})
        mode='INTELLIGENT_PRODUCTION_CONTROLLED' if not validation['errors'] else 'PAUSED'
        return {'mode':mode,'operations':operations,'message':str(len(operations))+' Intelligent Production operation planned.'}
    def run(self):
        IPE_DIR.mkdir(parents=True, exist_ok=True); REPORTS.mkdir(parents=True, exist_ok=True)
        sources=self.discover_sources(); inputs=self.discover_production_inputs(); validation=self.validate(sources, inputs); plan=self.plan(sources, inputs, validation)
        payload={'module':self.name,'created_at':now_text(),'sources':sources,'inputs':inputs,'validation':validation,'plan':plan}
        ts=now_stamp()
        snapshot=IPE_DIR/'600_intelligent_production_engine_snapshot.json'
        dashboard=IPE_DIR/'600_intelligent_production_engine_dashboard.json'
        state=IPE_DIR/('600_intelligent_production_engine_state_'+ts+'.json')
        report=REPORTS/('600_intelligent_production_engine_sdk_raporu_'+ts+'.txt')
        write_json(snapshot,payload); write_json(state,payload)
        write_json(dashboard, {'status':validation['decision'],'score':validation['score'],'mode':plan['mode'],'operation_count':len(plan['operations']),'errors':len(validation['errors']),'warnings':len(validation['warnings'])})
        lines=['='*80,'600 INTELLIGENT PRODUCTION ENGINE SDK','='*80,'Validation : '+str(validation['decision']),'Score      : '+str(validation['score'])+' / 100','Mode       : '+str(plan['mode']),'Operations : '+str(len(plan['operations'])),'','Dosyalar:',str(snapshot),str(dashboard),str(report)]
        report.write_text('\n'.join(lines), encoding='utf-8')
        return {'payload':payload,'paths':{'snapshot':str(snapshot),'dashboard':str(dashboard),'state':str(state),'report':str(report)}}
