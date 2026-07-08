# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "700"
sys.path.insert(0, str(PACKAGE_DIR))
from core.pilot_production_launcher_sdk import PilotProductionLauncherSDK
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()
    res=PilotProductionLauncherSDK(batch_size=args.batch_size, dry_run=not args.execute).run(); v=res['payload']['validation']; p=res['payload']['plan']
    print('='*80); print('700 PILOT PRODUCTION LAUNCHER SDK TAMAMLANDI'); print('='*80)
    print('Validation : '+str(v['decision']))
    print('Score      : '+str(v['score'])+' / 100')
    print('Errors     : '+str(len(v['errors'])))
    print('Warnings   : '+str(len(v['warnings'])))
    print('Mode       : '+str(p['mode']))
    print('Batch Size : '+str(p['batch_size']))
    print('')
    print('Dosyalar:')
    print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['queue']); print(res['paths']['report'])
if __name__=='__main__': main()
