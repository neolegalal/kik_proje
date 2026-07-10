# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "900"
sys.path.insert(0, str(PACKAGE_DIR))
from core.production_master_sdk import ProductionMasterSDK
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--target', type=int, default=100000); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()
    res=ProductionMasterSDK(target=args.target,batch_size=args.batch_size,dry_run=not args.execute).run(); v=res['payload']['validation']
    print('='*80); print('900 PRODUCTION MASTER SDK TAMAMLANDI'); print('='*80)
    print('Validation : '+str(v['decision']))
    print('Score      : '+str(v['score'])+' / 100')
    print('Errors     : '+str(len(v['errors'])))
    print('Warnings   : '+str(len(v['warnings'])))
    print('')
    print('Dosyalar:')
    print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['report'])
    raise SystemExit(1 if v['errors'] else 0)
if __name__=='__main__': main()
