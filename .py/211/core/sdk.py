from .config import *
from .utils import now_text, now_stamp, ensure_dirs, safe_json, write_json, append_jsonl
class LearningSDK:
    def __init__(self, name='211.0 Learning SDK'): self.name=name
    def load(self):
        return {'healing_snapshot':safe_json(HEALING_SNAPSHOT),'healing_dashboard':safe_json(HEALING_DASHBOARD),'autonomous_dashboard':safe_json(AUTONOMOUS_DASHBOARD),'automation_dashboard':safe_json(AUTOMATION_DASHBOARD),'execution_dashboard':safe_json(EXECUTION_DASHBOARD),'scheduler_dashboard':safe_json(SCHEDULER_DASHBOARD)}
    def build_context(self, raw):
        healing=raw.get('healing_snapshot',{}) or {}; validation=healing.get('validation',{}) or {}; plan=healing.get('plan',{}) or {}; actions=plan.get('actions',[]) or []
        execution=raw.get('execution_dashboard',{}) or {}; automation=raw.get('automation_dashboard',{}) or {}; autonomous=raw.get('autonomous_dashboard',{}) or {}; healing_dash=raw.get('healing_dashboard',{}) or {}; scheduler=raw.get('scheduler_dashboard',{}) or {}
        risk=healing_dash.get('risk') or autonomous.get('risk') or automation.get('risk') or execution.get('risk') or scheduler.get('risk')
        signals=[]
        if validation.get('score') is not None: signals.append({'type':'HEALING_SCORE','value':validation.get('score')})
        if actions: signals.append({'type':'HEALING_ACTION_COUNT','value':len(actions)})
        if execution.get('assignment_count') is not None: signals.append({'type':'EXECUTION_ASSIGNMENT_COUNT','value':execution.get('assignment_count')})
        if automation.get('trigger_count') is not None: signals.append({'type':'AUTOMATION_TRIGGER_COUNT','value':automation.get('trigger_count')})
        if autonomous.get('operation_count') is not None: signals.append({'type':'AUTONOMOUS_OPERATION_COUNT','value':autonomous.get('operation_count')})
        return {'created_at':now_text(),'risk':risk,'signal_count':len(signals),'signals':signals,'learning_ready':len(signals)>0 and risk in (None,'LOW')}
    def validate(self, context):
        errors=[]; warnings=[]
        if context.get('signal_count',0)==0: warnings.append('Learning için sinyal bulunamadı.')
        if context.get('risk')=='HIGH': errors.append('Risk HIGH; learning kontrollü moda alınmalı.')
        if not context.get('learning_ready'): warnings.append('Learning ready durumu tam değil.')
        score=100-min(60,len(errors)*20)-min(30,len(warnings)*5)
        decision='LEARNING CONTEXT READY' if not errors else 'LEARNING CONTEXT BLOCKED'
        return {'score':score,'decision':decision,'errors':errors,'warnings':warnings}
    def plan(self, context, validation):
        if validation['errors']: return {'learning_mode':'PAUSED','patterns':[],'message':'Learning blocked by validation errors.'}
        patterns=[{'pattern':'OBSERVE_'+s['type'],'value':s.get('value'),'status':'LEARNED'} for s in context.get('signals',[])]
        if not patterns: patterns.append({'pattern':'NO_PATTERN_AVAILABLE','status':'PLANNED'})
        patterns.append({'pattern':'UPDATE_RECOMMENDATION_MEMORY','status':'PLANNED'}); patterns.append({'pattern':'LEARNING_AUDIT_LOG','status':'PLANNED'})
        return {'learning_mode':'CONTROLLED_LEARNING','patterns':patterns,'message':str(len(patterns))+' learning pattern planned.'}
    def export(self, payload, name='211_0_learning_sdk'):
        ensure_dirs(LEARNING_DIR, REPORT_DIR, STATE_DIR); ts=now_stamp(); state=STATE_DIR/f'{name}_state_{ts}.json'; report=REPORT_DIR/f'{name}_raporu_{ts}.txt'
        write_json(LEARNING_SNAPSHOT,payload); write_json(state,payload); append_jsonl(LEARNING_HISTORY,payload)
        dash={'learning_status':payload['validation']['decision'],'learning_mode':payload['plan']['learning_mode'],'pattern_count':len(payload['plan']['patterns']),'risk':payload['context'].get('risk'),'signal_count':payload['context'].get('signal_count')}
        write_json(LEARNING_DASHBOARD,dash)
        lines=['='*80,'211.0 LEARNING SDK','='*80,'Validation : '+str(payload['validation']['decision']),'Score      : '+str(payload['validation']['score']),'Mode       : '+str(payload['plan']['learning_mode']),'Patterns   : '+str(len(payload['plan']['patterns'])),'','Message:',str(payload['plan']['message']),'','Dosyalar:',str(LEARNING_SNAPSHOT),str(LEARNING_DASHBOARD),str(state),str(report)]
        report.write_text('\\n'.join(lines), encoding='utf-8')
        return {'snapshot':str(LEARNING_SNAPSHOT),'dashboard':str(LEARNING_DASHBOARD),'state':str(state),'report':str(report)}
    def run(self):
        raw=self.load(); context=self.build_context(raw); validation=self.validate(context); plan=self.plan(context,validation); payload={'module':self.name,'created_at':now_text(),'context':context,'validation':validation,'plan':plan}; return {'payload':payload,'paths':self.export(payload)}
