"""Parallel independent fold-seed processes inside one CQ resource allocation."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import json
import os
from queue import Queue
from pathlib import Path
import subprocess
import sys
import time


def execute(task,dataset,output,device,epochs,engineering=False,protocol=Path('configs/010-preregistered.json'),runner='cascade',gpu_id=None):
    regime,fold,seed=task
    dest=output/f'{fold}-s{seed}'
    dest.mkdir(parents=True,exist_ok=True)
    command=[sys.executable,'-m','lobbench.cascade_run','--dataset',str(dataset),'--output',str(dest),
             '--regimes',regime,'--folds',fold,'--seeds',str(seed),'--epochs',str(epochs),'--device',device,'--protocol',str(protocol)]
    if runner=='direct':
        command=[sys.executable,'-m','lobbench.direct_run','--dataset',str(dataset),'--output',str(dest),
                 '--regime',regime,'--fold',fold,'--seed',str(seed),'--device',device,'--protocol',str(protocol)]
    if engineering:command.append('--engineering')
    start=time.monotonic()
    env={**os.environ,'OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'}
    if gpu_id is not None:env['CUDA_VISIBLE_DEVICES']=str(gpu_id)
    with (dest/'run.log').open('w') as log:
        result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=env)
    return dict(regime=regime,fold=fold,seed=seed,returncode=result.returncode,seconds=time.monotonic()-start,folder=str(dest.name),gpu_id=gpu_id)


def leased_execute(devices,*args):
    """Hold one device until the whole child exits, including its CPU stages."""
    gpu_id=devices.get()
    try:return execute(*args,gpu_id=gpu_id)
    finally:devices.put(gpu_id)


def main(dataset,output,regimes,seeds,workers,device,epochs,engineering=False,protocol=Path('configs/010-preregistered.json'),runner='cascade',folds=None):
    if not os.environ.get('CQ_JOB_ID') and not engineering:raise RuntimeError('CQ required')
    if workers>4 or workers<1:raise ValueError('Unqualified worker allocation')
    devices=None
    if device=='cuda':
        import torch
        count=torch.cuda.device_count()
        if workers>min(2,count):raise ValueError('At most two qualified GPUs, one worker per device')
        visible=os.environ.get('CUDA_VISIBLE_DEVICES')
        ids=visible.split(',') if visible else list(range(count))
        devices=Queue()
        for gpu_id in ids[:workers]:devices.put(gpu_id)
    output.mkdir(parents=True,exist_ok=True)
    stocks=['KGHM','PEKAO','PKNORLEN','PKOBP','PZU']
    tasks=[(regime,fold,seed) for regime in regimes for fold in ([regime] if regime in ('date','style') else [regime+'-'+s for s in stocks]) for seed in seeds]
    if folds is not None:tasks=[t for t in tasks if t[1] in folds]
    if not tasks:raise ValueError('No registered tasks selected')
    reports=[]
    (output/'progress.txt').write_text(f'0/{len(tasks)} started\n')
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(leased_execute,devices,t,dataset,output,device,epochs,engineering,protocol,runner) if devices is not None
                 else pool.submit(execute,t,dataset,output,device,epochs,engineering,protocol,runner) for t in tasks]
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
    p.add_argument('--protocol',type=Path,default=Path('configs/010-preregistered.json'))
    p.add_argument('--runner',choices=['cascade','direct'],default='cascade');p.add_argument('--folds',nargs='+')
    a=p.parse_args();main(a.dataset,a.output,a.regimes,a.seeds,a.workers,a.device,a.epochs,a.engineering,a.protocol,a.runner,a.folds)
