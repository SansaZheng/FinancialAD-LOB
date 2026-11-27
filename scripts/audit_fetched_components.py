"""Bounded sequential local verification after explicit CQ-fetch receipts."""
import argparse,json,os,subprocess,sys,time
from pathlib import Path

def main(jobs,watches,dataset,output):
 done=set();output.mkdir(parents=True,exist_ok=True);status=output/'local-audit-watch.json'
 env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
 while len(done)<len(jobs):
  fetched=set()
  for p in watches:
   if p.exists():
    try:fetched.update(json.loads(p.read_text()).get('fetched',[]))
    except json.JSONDecodeError:pass
  for job in jobs:
   if job in done or job not in fetched:continue
   root=Path('results/cq-013')/job/'batch';b=json.loads((root/'batch.json').read_text())
   if b['status']!='complete':raise ValueError('Completed CQ batch required')
   for module,label in [('scripts.reload_components','mac-reload'),('scripts.verify_components','verification')]:
    dest=output/(job+'-'+label+'.json');args=[sys.executable,'-m',module,'--dataset',str(dataset),'--root',str(root),'--output',str(dest)]
    if label=='verification':args+=['--protocol','configs/013-preregistered.json']
    with (output/(job+'-'+label+'.log')).open('w') as log:subprocess.run(args,env=env,stdout=log,stderr=subprocess.STDOUT,check=True)
    if not json.loads(dest.read_text())['passed']:raise ValueError('Audit did not pass')
   done.add(job);status.write_text(json.dumps(dict(verified_jobs=sorted(done),pending=sorted(set(jobs)-done)),indent=2)+'\n');print(job,'Mac reload and independent audit passed',flush=True)
  if len(done)<len(jobs):time.sleep(45)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jobs',nargs='+',required=True);p.add_argument('--watches',type=Path,nargs='+',required=True);p.add_argument('--dataset',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();main(a.jobs,a.watches,a.dataset,a.output)
