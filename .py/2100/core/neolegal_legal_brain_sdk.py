
# -*- coding: utf-8 -*-
import json,re
from pathlib import Path
from datetime import datetime

BASE=Path(r"C:\Users\MSI\Desktop\kik_proje")
PY=BASE/".py"
STATE=BASE/"production_state"
REPORTS=BASE/"raporlar"
BRAIN_DIR=STATE/"neolegal_legal_brain"
UDP_DIR=STATE/"unified_decision_processor"
VALIDATION_DIR=STATE/"validation_benchmark_platform"
SUPPORT_IDS=["2050","1990","1980","1970","1950","1900","1800","1700","1600","1500","1400","1300","1100"]

def ts(): return datetime.now().strftime("%Y%m%d_%H%M%S")
def nt(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def wj(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding="utf-8")

class BrainState:
    def __init__(self,case_text,source_record=None):
        self.case_text=case_text
        self.source_record=source_record or {}
        self.memory={}
        self.thinking={}
        self.outcomes={}
        self.judge={}
        self.opposition={}
        self.hearing={}
        self.negotiation={}
        self.copilot={}
        self.reflection={}
        self.certificate={}
    def as_dict(self):
        return self.__dict__

class NeoLegalLegalBrainSDK:
    def __init__(self,name="2100 NeoLegal Legal Brain SDK",case_text=None,master_record_path=None,execute=False):
        self.name=name
        self.case_text=case_text or "İş deneyim belgesinin benzer işe uygun olmadığı gerekçesiyle değerlendirme dışı bırakılan isteklinin yeterlik, eşit muamele, rekabet ve başvuru süresi yönlerinden hukuki durumu değerlendirilmelidir."
        self.master_record_path=Path(master_record_path) if master_record_path else None
        self.execute=bool(execute)

    def support_modules(self):
        return [{"module_id":m,"found":bool(list(PY.glob(m+"*.py"))),"count":len(list(PY.glob(m+"*.py")))} for m in SUPPORT_IDS]

    def latest_master(self):
        if self.master_record_path and self.master_record_path.exists(): return self.master_record_path
        xs=sorted(UDP_DIR.glob("1950_master_record_*.json"),reverse=True)
        return xs[0] if xs else None

    def load_json(self,p):
        try:
            return json.loads(Path(p).read_text(encoding="utf-8")) if p and Path(p).exists() else {}
        except Exception:
            return {}

    def legal_memory(self,s):
        topics=s.source_record.get("topic_records",[])
        if not topics:
            labels=[]
            low=s.case_text.lower()
            for k,v in [("iş deneyim","İş deneyim belgesi"),("benzer iş","Benzer iş"),("yeterlik","Yeterlik kriteri"),("eşit muamele","Eşit muamele"),("rekabet","Rekabet"),("süre","Başvuru süresi")]:
                if k in low: labels.append(v)
            topics=[{"topic_id":i+1,"topic":x,"confidence":80,"success_probability":60} for i,x in enumerate(labels or ["Genel ihale uyuşmazlığı"])]
        val=self.load_json(VALIDATION_DIR/"2050_validation_benchmark_snapshot.json")
        s.memory={"status":"READY","active_topics":[x.get("topic") for x in topics],"topic_records":topics,"validation_reference":val.get("accuracy",{}),"memory_size":len(topics),"source":str(self.latest_master()) if self.latest_master() else "synthetic"}

    def legal_thinking(self,s):
        chain=[]; strengths=[]; weaknesses=[]
        for t in s.memory["topic_records"]:
            topic=t.get("topic","Konu")
            chain.append({"issue":topic,"rule":"İhale dokümanı, somut belge ve 4734 sayılı Kanun m.5 birlikte uygulanır.","application":topic+" yönünden belge-doküman bağlantısı değerlendirilir.","conclusion":topic+" bakımından ayrı hukuki sonuç kurulmalıdır."})
            (strengths if t.get("confidence",0)>=80 else weaknesses).append(topic)
        s.thinking={"status":"READY","reasoning_chain":chain,"strengths":strengths,"weaknesses":weaknesses or ["Kritik eksiklik yok"],"thinking_score":min(98,75+len(chain)*3)}

    def outcomes(self,s):
        p=60
        if any("süre" in str(x).lower() for x in s.memory["active_topics"]): p-=10
        if any("eşit muamele" in str(x).lower() or "rekabet" in str(x).lower() for x in s.memory["active_topics"]): p+=10
        s.outcomes={"status":"READY","base_probability":p,"scenarios":[
            {"scenario":"Mevcut deliller","probability":p},
            {"scenario":"Güçlü emsal eklendi","probability":min(95,p+15)},
            {"scenario":"Süre sorunu","probability":max(5,p-30)},
            {"scenario":"Kritik belge eksik","probability":max(5,p-20)}]}

    def judge(self,s):
        p=s.outcomes["base_probability"]
        if p>=70: lean="Başvurucu lehine"; why="Belge, doküman ve temel ilkeler hukuka aykırılık ihtimalini güçlendiriyor."
        elif p>=45: lean="Dengeli / belirsiz"; why="Sonuç, belge ve usul koşullarına bağlı."
        else: lean="İdare lehine"; why="Usul veya belge eksikliği esasa üstün gelebilir."
        s.judge={"status":"READY","judicial_leaning":lean,"simulated_probability":p,"likely_reasoning":why,"critical_questions":["Doküman hükmü açık mı?","Belge kriteri karşılıyor mu?","Süre korunmuş mu?","Eşit muamele ihlali somut mu?"]}

    def opposition(self,s):
        s.opposition={"status":"READY","arguments":[{"topic":x,"opposition_argument":"İdare, "+str(x)+" yönünden dokümanın açık ve işlemin eşit uygulandığını savunabilir.","reply":"Somut belge, tutanak ve emsal kararlarla cevap verilmelidir."} for x in s.memory["active_topics"]]}
        s.opposition["argument_count"]=len(s.opposition["arguments"])

    def hearing(self,s):
        s.hearing={"status":"READY","opening_statement":"Uyuşmazlık, doküman ile somut belge ilişkisinin temel ilkeler çerçevesinde değerlendirilmesine ilişkindir.","questions":s.judge["critical_questions"],"best_answers":["Doküman ve belge birebir karşılaştırılmalıdır.","Gerekçe somut ve denetlenebilir olmalıdır.","Eşit muamele benzer isteklilerle gösterilmelidir.","Süre tarihleri belgelenmelidir."]}

    def negotiation(self,s):
        p=s.outcomes["base_probability"]
        posture="Güçlü pozisyon" if p>=75 else "Kontrollü müzakere" if p>=50 else "Risk azaltma"
        s.negotiation={"status":"READY","posture":posture,"acceptable_outcomes":["Düzeltici işlem","Yeniden değerlendirme","Gerekçeli ret işleminin kaldırılması"],"red_lines":["Süre kaybı","Hak kaybı doğuran feragat","Belgesiz kabul"]}

    def copilot(self,s):
        s.copilot={"status":"READY","summary":"Dosyada "+", ".join(s.memory["active_topics"])+" başlıkları öne çıkmaktadır.","recommended_action":"Önce süre/usul, sonra belge-doküman, ardından temel ilkeler ve emsal karar analizi yapılmalıdır.","next_questions":["Tebliğ tarihi nedir?","İlgili kriterin tam metni nedir?","Ret gerekçesi aynen nedir?","Benzer durumda kabul edilen başka istekli var mı?"],"judge_view":s.judge["judicial_leaning"],"opposition_count":s.opposition["argument_count"],"negotiation_posture":s.negotiation["posture"]}

    def reflect(self,s):
        issues=[]; conf=90
        if s.outcomes["base_probability"]<50: issues.append("Alternatif strateji güçlendirilmeli."); conf-=10
        if s.memory["memory_size"]<2: issues.append("Ek belge veya emsal gerekli."); conf-=8
        if not s.opposition["arguments"]: issues.append("Karşı argüman üretilemedi."); conf-=15
        s.reflection={"status":"PASS" if conf>=80 else "WARN","confidence":max(0,conf),"criticisms":issues or ["Kritik tutarsızlık yok"],"revised_recommendation":"Nihai görüş insan uzman ve somut belgelerle kesinleştirilmelidir."}

    def certificate(self,s):
        s.certificate={"certificate_id":"LB-"+ts(),"status":s.reflection["status"],"thinking_score":s.thinking["thinking_score"],"base_probability":s.outcomes["base_probability"],"judge_view":s.judge["judicial_leaning"],"reflection_confidence":s.reflection["confidence"],"issued_at":nt()}

    def audit(self,s):
        keys=["memory","thinking","outcomes","judge","opposition","hearing","negotiation","copilot","reflection","certificate"]
        score=100; warnings=[]
        d=s.as_dict()
        for k in keys:
            if not d.get(k): score-=10; warnings.append(k+" missing")
        if s.reflection.get("status")=="WARN": score-=8; warnings.append("self reflection warning")
        return {"score":max(score,0),"status":"PASS" if score>=85 else "WARN" if score>=65 else "FAIL","warnings":warnings}

    def run(self):
        BRAIN_DIR.mkdir(parents=True,exist_ok=True); REPORTS.mkdir(parents=True,exist_ok=True)
        modules=self.support_modules()
        mp=self.latest_master(); master=self.load_json(mp)
        s=BrainState(re.sub(r"\s+"," ",self.case_text).strip(),master)
        self.legal_memory(s); self.legal_thinking(s); self.outcomes(s); self.judge(s); self.opposition(s); self.hearing(s); self.negotiation(s); self.copilot(s); self.reflect(s); self.certificate(s)
        audit=self.audit(s)
        support=round(sum(1 for x in modules if x["found"])/len(modules)*100,2) if modules else 100
        final=round(support*.15+audit["score"]*.35+s.thinking["thinking_score"]*.20+s.reflection["confidence"]*.15+s.outcomes["base_probability"]*.15,2)
        decision="NEOLEGAL LEGAL BRAIN READY" if audit["status"]!="FAIL" and support>=60 else "NEOLEGAL LEGAL BRAIN BLOCKED"
        stamp=ts()
        snap=BRAIN_DIR/"2100_neolegal_legal_brain_snapshot.json"
        brain=BRAIN_DIR/("2100_brain_state_"+stamp+".json")
        dash=BRAIN_DIR/"2100_neolegal_legal_brain_dashboard.json"
        state=BRAIN_DIR/("2100_neolegal_legal_brain_state_"+stamp+".json")
        rep=REPORTS/("2100_neolegal_legal_brain_sdk_raporu_"+stamp+".txt")
        payload={"brain_state":s.as_dict(),"audit":audit,"modules":modules,"master_record_path":str(mp) if mp else None,"validation":{"score":final,"support_score":support,"decision":decision,"errors":[] if decision.endswith("READY") else ["blocked"],"warnings":audit["warnings"]}}
        wj(snap,payload); wj(state,payload); wj(brain,s.as_dict()); wj(dash,{"status":decision,"score":final,"thinking_score":s.thinking["thinking_score"],"base_probability":s.outcomes["base_probability"],"judge_view":s.judge["judicial_leaning"],"reflection_confidence":s.reflection["confidence"],"audit":audit["status"]})
        lines=["="*80,"2100 NEOLEGAL LEGAL BRAIN SDK","="*80,"Validation            : "+decision,"Score                 : "+str(final)+" / 100","Thinking Score        : "+str(s.thinking["thinking_score"])+" / 100","Base Probability      : "+str(s.outcomes["base_probability"])+" / 100","Judge View            : "+s.judge["judicial_leaning"],"Reflection Confidence : "+str(s.reflection["confidence"])+" / 100","Audit                 : "+audit["status"],"","Dosyalar:",str(snap),str(brain),str(dash),str(rep)]
        rep.write_text("\n".join(lines),encoding="utf-8")
        return {"payload":payload,"paths":{"snapshot":str(snap),"brain_state":str(brain),"dashboard":str(dash),"state":str(state),"report":str(rep)}}
