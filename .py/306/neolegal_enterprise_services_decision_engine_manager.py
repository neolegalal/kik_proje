import argparse
from modules.neolegal_enterprise_services_decision_engine.engine import NeolegalEnterpriseServicesDecisionEngineModule
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--run', action='store_true'); parser.add_argument('--status', action='store_true'); args=parser.parse_args()
    res=NeolegalEnterpriseServicesDecisionEngineModule().run(); r=res['result']
    print('='*80); print('306.8 NeoLegal Enterprise Services Decision Engine'.upper()+' TAMAMLANDI'); print('='*80)
    print('Score    : '+str(r['score'])+' / 100'); print('Decision : '+str(r['decision'])); print('Risk     : '+str(r['risk'])); print(''); print('Recommendation:'); print(r['recommendation']); print(''); print('Dosyalar:'); print(res['paths']['output']); print(res['paths']['report'])
if __name__=='__main__': main()
