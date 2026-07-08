import argparse
from modules.neolegal_platform_os_planner.engine import NeolegalPlatformOsPlannerModule
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--run', action='store_true'); parser.add_argument('--status', action='store_true'); args=parser.parse_args()
    res=NeolegalPlatformOsPlannerModule().run(); r=res['result']
    print('='*80); print('309.4 NeoLegal Platform OS Planner'.upper()+' TAMAMLANDI'); print('='*80)
    print('Score    : '+str(r['score'])+' / 100'); print('Decision : '+str(r['decision'])); print('Risk     : '+str(r['risk'])); print(''); print('Recommendation:'); print(r['recommendation']); print(''); print('Dosyalar:'); print(res['paths']['output']); print(res['paths']['report'])
if __name__=='__main__': main()
