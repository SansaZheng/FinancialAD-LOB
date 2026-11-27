"""Watch explicitly listed FinancialAD CQ jobs and fetch completed archives.

No submit/retry/cancel actions. Used only while the active research task runs.
"""
import argparse,json,subprocess,time
from pathlib import Path

def watch(jobs,state,root,cq,interval):
 if root.is_absolute() or '..' in root.parts or not str(root).startswith('results/'):raise ValueError('Use a project results subdirectory')
 fetched=set();previous=None
 if state.exists():fetched=set(json.loads(state.read_text()).get('fetched',[]))
 while True:
  statuses=[]
  for job in jobs:
   r=json.loads(subprocess.check_output([cq,'--json','show',job],text=True))
   if r['work']!='FinancialAD-LOB':raise ValueError('Foreign project job')
   statuses.append({k:r.get(k) for k in ['id','state','reason','started','finished']})
   if r['state']=='done' and (job not in fetched or not (root/job).exists()):
    subprocess.run(['git','sparse-checkout','add','--skip-checks',str(root/job)],check=True)
    subprocess.run([cq,'fetch',job,'--to',str(root)],check=True);fetched.add(job)
  report=dict(jobs=statuses,fetched=sorted(fetched));state.parent.mkdir(parents=True,exist_ok=True);state.write_text(json.dumps(report,indent=2)+'\n')
  if report!=previous:print(json.dumps(report),flush=True);previous=report
  if all(j in fetched for j in jobs):return
  if any(r['state'] in ['failed','cancelled','lost'] for r in statuses):raise RuntimeError('Requested job needs inspection; no automatic retry')
  time.sleep(interval)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--jobs',nargs='+',required=True);p.add_argument('--state',type=Path,required=True);p.add_argument('--root',type=Path,default=Path('results/cq-013'));p.add_argument('--cq',default='cq');p.add_argument('--interval',type=float,default=45);a=p.parse_args();watch(a.jobs,a.state,a.root,a.cq,a.interval)
