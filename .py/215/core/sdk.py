from .config import *
from .utils import now_text, now_stamp, ensure_dirs, safe_json, write_json, append_jsonl
class EnterprisePlatformSDK:
    def __init__(self, name='215.0 Enterprise Platform SDK'): self.name=name
    def load(self):
        return {'improvement':safe_json(IMPROVEMENT_DASHBOARD),'graph':safe_json(GRAPH_DASHBOARD),'ai':safe_json(AI_DASHBOARD)}
    def build_context(self, raw):
        primary=raw.get('improvement',{}) or {}
        secondary=raw.get('graph',{}) or {}
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
        decision='ENTERPRISE PLATFORM CONTEXT READY' if not errors else 'ENTERPRISE PLATFORM CONTEXT BLOCKED'
        return {'score':score,'decision':decision,'errors':errors,'warnings':warnings}
    def plan(self, context, validation):
        if validation['errors']: return {'mode':'PAUSED','operations':[],'message':'Enterprise Platform blocked by validation errors.'}
        operations=[]
        for sig in context.get('signals',[]): operations.append({'operation':'PROCESS_'+sig['source'].upper(),'status':'PLANNED'})
        if not operations: operations.append({'operation':'NO_SOURCE_AVAILABLE','status':'PLANNED'})
        operations.append({'operation':'ENTERPRISE_PLATFORM_AUDIT_LOG','status':'PLANNED'})
        return {'mode':'CONTROLLED_ENTERPRISE_PLATFORM','operations':operations,'message':str(len(operations))+' enterprise operation planned.'}
    def export(self,payload,name=None):
        name=name or '215_0_enterprise_platform_sdk'
        ensure_dirs(ENTERPRISE_PLATFORM_DIR, REPORT_DIR, STATE_DIR); ts=now_stamp(); state=STATE_DIR/f'{name}_state_{ts}.json'; report=REPORT_DIR/f'{name}_raporu_{ts}.txt'
        write_json(ENTERPRISE_PLATFORM_SNAPSHOT,payload); write_json(state,payload); append_jsonl(ENTERPRISE_PLATFORM_HISTORY,payload)
        dash={'status':payload['validation']['decision'],'mode':payload['plan']['mode'],'operation_count':len(payload['plan']['operations']),'risk':payload['context'].get('risk'),'source_count':payload['context'].get('source_count')}
        write_json(ENTERPRISE_PLATFORM_DASHBOARD,dash)
        lines=['='*80,'215.0 Enterprise Platform SDK'.upper(),'='*80,'Validation : '+str(payload['validation']['decision']),'Score      : '+str(payload['validation']['score']),'Mode       : '+str(payload['plan']['mode']),'Operations : '+str(len(payload['plan']['operations'])),'','Message:',str(payload['plan']['message']),'','Dosyalar:',str(ENTERPRISE_PLATFORM_SNAPSHOT),str(ENTERPRISE_PLATFORM_DASHBOARD),str(state),str(report)]
        report.write_text('\\n'.join(lines), encoding='utf-8')
        return {'snapshot':str(ENTERPRISE_PLATFORM_SNAPSHOT),'dashboard':str(ENTERPRISE_PLATFORM_DASHBOARD),'state':str(state),'report':str(report)}
    def run(self):
        raw=self.load(); context=self.build_context(raw); validation=self.validate(context); plan=self.plan(context,validation); payload={'module':self.name,'created_at':now_text(),'context':context,'validation':validation,'plan':plan}; return {'payload':payload,'paths':self.export(payload)}
