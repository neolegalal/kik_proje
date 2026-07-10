# -*- coding: utf-8 -*-
import argparse, sys
from pathlib import Path
PACKAGE_DIR = Path(__file__).resolve().parent / "1000"
sys.path.insert(0, str(PACKAGE_DIR))
from core.production_operations_sdk import ProductionOperationsSDK
def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--target', type=int, default=100000); parser.add_argument('--batch-size', type=int, default=10); parser.add_argument('--execute', action='store_true'); args=parser.parse_args()
    res=ProductionOperationsSDK(target=args.target,batch_size=args.batch_size,execute=args.execute).run(); v=res['payload']['validation']
    print(res['payload']['executive_summary'])
    print('')
    print('Files:')
    print(res['paths']['snapshot']); print(res['paths']['dashboard']); print(res['paths']['kpi']); print(res['paths']['report'])
    raise SystemExit(1 if v['errors'] else 0)
if __name__=='__main__': main()
