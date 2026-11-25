"""Parallel independent fold-seed processes inside one CQ resource allocation."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def execute(task,dataset,output,device,epochs,engineering=False):
    regime,fold,seed=task
    dest=output/f'{fold}-s{seed}'
    dest.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,'-m','lobbench.cascade_run','--dataset',str(dataset),'--output',str(dest),
             '--regimes',regime,'--folds',fold,'--seeds',str(seed),'--epochs',str(epochs),'--device',device]
    if engineering:command.append('--engineering')
    start=time.monotonic()
    with (dest/'run.log').open('w') as log:
        result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
    return dict(regime=regime,fold=fold,seed=seed,returncode=result.returncode,seconds=time.monotonic()-start,folder=str(dest.name))


def main(dataset,output,regimes,seeds,workers,device,epochs,engineering=False):
    if not os.environ.get('CQ_JOB_ID') and not engineering:raise RuntimeError('CQ required')
    if workers>4 or workers<1 or (device=='cuda' and workers!=1):raise ValueError('Unqualified worker/device allocation')
    output.mkdir(parents=True,exist_ok=True)
    stocks=['KGHM','PEKAO','PKNORLEN','PKOBP','PZU']
    tasks=[(regime,fold,seed) for regime in regimes for fold in ([regime] if regime in ('date','style') else [regime+'-'+s for s in stocks]) for seed in seeds]
    reports=[]
    (output/'progress.txt').write_text(f'0/{len(tasks)} started\n')
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(execute,t,dataset,output,device,epochs,engineering) for t in tasks]
        for future in as_completed(futures):
            report=future.result();reports.append(report)
            print(json.dumps(report),flush=True)
            (output/'batch.json').write_text(json.dumps(dict(status='partial',tasks=reports,total=len(tasks)),indent=2)+'\n')
            (output/'progress.txt').write_text(f'{len(reports)}/{len(tasks)} completed\n')
    okay=all(r['returncode']==0 for r in reports)
    (output/'batch.json').write_text(json.dumps(dict(status='complete' if okay else 'failed',tasks=reports,total=len(tasks)),indent=2)+'\n')
    if not okay:raise RuntimeError('Some fold-seed workers failed; retain partial outputs and inspect logs')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dataset',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--regimes',nargs='+',choices=['date','stock','combined','style'],required=True);p.add_argument('--seeds',nargs='+',type=int,default=[0,1,2,3,4])
    p.add_argument('--workers',type=int,default=1);p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--epochs',type=int,default=10);p.add_argument('--engineering',action='store_true')
    a=p.parse_args();main(a.dataset,a.output,a.regimes,a.seeds,a.workers,a.device,a.epochs,a.engineering)
