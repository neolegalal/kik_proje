from .config import *
from .utils import now_text, now_stamp, ensure_dirs, safe_json, write_json, append_jsonl

class NeolegalKernelSDK:
    def __init__(self, name="305.0 NeoLegal Kernel SDK"):
        self.name = name

    def load(self):
        return {'primary': safe_json(PRIMARY_SOURCE), 'secondary': safe_json(SECONDARY_SOURCE), 'tertiary': safe_json(TERTIARY_SOURCE)}

    def build_context(self, raw):
        signals=[]; risk=None
        for key,value in raw.items():
            if isinstance(value, dict) and value:
                signals.append({'source':key,'keys':len(value),'status':'OBSERVED'})
                if risk is None: risk=value.get('risk')
        return {'created_at':now_text(),'risk':risk,'source_count':len(signals),'signals':signals,'layer_ready':len(signals)>0 and risk in (None,'LOW')}

    def validate(self, context):
        errors=[]; warnings=[]
        if context.get('source_count',0)==0: warnings.append('Kaynak dashboard bulunamadı.')
        if context.get('risk')=='HIGH': errors.append('Risk HIGH; kontrollü moda alınmalı.')
        if not context.get('layer_ready'): warnings.append('Layer ready durumu tam değil.')
        score=100-min(60,len(errors)*20)-min(30,len(warnings)*5)
        decision="NEOLEGAL KERNEL CONTEXT READY" if not errors else "NEOLEGAL KERNEL CONTEXT BLOCKED"
        return {'score':score,'decision':decision,'errors':errors,'warnings':warnings}

    def plan(self, context, validation):
        if validation['errors']: return {'mode':'PAUSED','operations':[],'message':'NeoLegal Kernel blocked by validation errors.'}
        operations=[]
        for sig in context.get('signals',[]): operations.append({'operation':'PROCESS_'+sig['source'].upper(),'status':'PLANNED'})
        if not operations: operations.append({'operation':'NO_SOURCE_AVAILABLE','status':'PLANNED'})
        operations.append({'operation':'NEOLEGAL_KERNEL_AUDIT_LOG','status':'PLANNED'})
        return {'mode':'CONTROLLED_NEOLEGAL_KERNEL','operations':operations,'message':str(len(operations))+' neolegal kernel operation planned.'}

    def export(self, payload, name=None):
        name=name or '305_0_neolegal_kernel_sdk'
        ensure_dirs(NEOLEGAL_KERNEL_DIR, REPORT_DIR, STATE_DIR)
        ts=now_stamp(); state=STATE_DIR/f'{name}_state_{ts}.json'; report=REPORT_DIR/f'{name}_raporu_{ts}.txt'
        write_json(NEOLEGAL_KERNEL_SNAPSHOT, payload); write_json(state, payload); append_jsonl(NEOLEGAL_KERNEL_HISTORY, payload)
        dash={'status':payload['validation']['decision'],'mode':payload['plan']['mode'],'operation_count':len(payload['plan']['operations']),'risk':payload['context'].get('risk'),'source_count':payload['context'].get('source_count')}
        write_json(NEOLEGAL_KERNEL_DASHBOARD, dash)
        lines=['='*80,'305.0 NeoLegal Kernel SDK'.upper(),'='*80,'Validation : '+str(payload['validation']['decision']),'Score      : '+str(payload['validation']['score']),'Mode       : '+str(payload['plan']['mode']),'Operations : '+str(len(payload['plan']['operations'])),'','Message:',str(payload['plan']['message']),'','Dosyalar:',str(NEOLEGAL_KERNEL_SNAPSHOT),str(NEOLEGAL_KERNEL_DASHBOARD),str(report)]
        report.write_text('\\n'.join(lines), encoding='utf-8')
        return {'snapshot':str(NEOLEGAL_KERNEL_SNAPSHOT),'dashboard':str(NEOLEGAL_KERNEL_DASHBOARD),'state':str(state),'report':str(report)}

    def run(self):
        raw=self.load(); context=self.build_context(raw); validation=self.validate(context); plan=self.plan(context,validation)
        payload={'module':self.name,'created_at':now_text(),'context':context,'validation':validation,'plan':plan}
        return {'payload':payload,'paths':self.export(payload)}
