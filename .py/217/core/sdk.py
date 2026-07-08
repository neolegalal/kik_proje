from .config import *
from .utils import now_text, now_stamp, ensure_dirs, safe_json, write_json, append_jsonl
class LargeScaleProductionSDK:
    def __init__(self, name='217.0 Large Scale Production SDK'): self.name=name
    def load(self):
        return {'cluster':safe_json(CLUSTER_DASHBOARD),'enterprise':safe_json(ENTERPRISE_DASHBOARD),'improvement':safe_json(IMPROVEMENT_DASHBOARD)}
    def build_context(self, raw):
        primary=raw.get('cluster',{}) or {}
        secondary=raw.get('enterprise',{}) or {}
        risk=primary.get('risk') or secondary.get('risk')
        source_count=sum(1 for v in raw.values() if v)
        signals=[]
        for k,v in raw.items():
            if isinstance(v, dict) and v:
                signals.append({'source':k,'keys':len(v),'status':'OBSERVED'})
        return {'created_at':now_text(),'risk':risk,'source_count':source_count,'signals':signals,'layer_ready':source_count>0 and risk in (None,'LOW')}
    def validate(self, context):
        errors=[]; warnings=[]
        if context.get('source_count',0)==0: warnings.append('Kaynak dashboard bulunamadı.')
        if context.get('risk')=='HIGH': errors.append('Risk HIGH; kontrollü moda alınmalı.')
        if not context.get('layer_ready'): warnings.append('Layer ready durumu tam değil.')
        score=100-min(60,len(errors)*20)-min(30,len(warnings)*5)
        decision='LARGE SCALE PRODUCTION CONTEXT READY' if not errors else 'LARGE SCALE PRODUCTION CONTEXT BLOCKED'
        return {'score':score,'decision':decision,'errors':errors,'warnings':warnings}
    def plan(self, context, validation):
        if validation['errors']: return {'mode':'PAUSED','operations':[],'message':'Large Scale Production blocked by validation errors.'}
        operations=[]
        for sig in context.get('signals',[]): operations.append({'operation':'PROCESS_'+sig['source'].upper(),'status':'PLANNED'})
        if not operations: operations.append({'operation':'NO_SOURCE_AVAILABLE','status':'PLANNED'})
        operations.append({'operation':'LARGE_SCALE_PRODUCTION_AUDIT_LOG','status':'PLANNED'})
        return {'mode':'CONTROLLED_LARGE_SCALE_PRODUCTION','operations':operations,'message':str(len(operations))+' large scale operation planned.'}
    def export(self,payload,name=None):
        name=name or '217_0_large_scale_production_sdk'
        ensure_dirs(LARGE_SCALE_PRODUCTION_DIR, REPORT_DIR, STATE_DIR); ts=now_stamp(); state=STATE_DIR/f'{name}_state_{ts}.json'; report=REPORT_DIR/f'{name}_raporu_{ts}.txt'
        write_json(LARGE_SCALE_PRODUCTION_SNAPSHOT,payload); write_json(state,payload); append_jsonl(LARGE_SCALE_PRODUCTION_HISTORY,payload)
        dash={'status':payload['validation']['decision'],'mode':payload['plan']['mode'],'operation_count':len(payload['plan']['operations']),'risk':payload['context'].get('risk'),'source_count':payload['context'].get('source_count')}
        write_json(LARGE_SCALE_PRODUCTION_DASHBOARD,dash)
        lines=['='*80,'217.0 Large Scale Production SDK'.upper(),'='*80,'Validation : '+str(payload['validation']['decision']),'Score      : '+str(payload['validation']['score']),'Mode       : '+str(payload['plan']['mode']),'Operations : '+str(len(payload['plan']['operations'])),'','Message:',str(payload['plan']['message']),'','Dosyalar:',str(LARGE_SCALE_PRODUCTION_SNAPSHOT),str(LARGE_SCALE_PRODUCTION_DASHBOARD),str(state),str(report)]
        report.write_text('\\n'.join(lines), encoding='utf-8')
        return {'snapshot':str(LARGE_SCALE_PRODUCTION_SNAPSHOT),'dashboard':str(LARGE_SCALE_PRODUCTION_DASHBOARD),'state':str(state),'report':str(report)}
    def run(self):
        raw=self.load(); context=self.build_context(raw); validation=self.validate(context); plan=self.plan(context,validation); payload={'module':self.name,'created_at':now_text(),'context':context,'validation':validation,'plan':plan}; return {'payload':payload,'paths':self.export(payload)}
