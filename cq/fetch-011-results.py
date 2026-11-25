import concurrent.futures,json,subprocess,time
from pathlib import Path
jobs={'j-1125-5788a5':'stock','j-1125-58fc68':'combined'}
tasks=[]
for job,regime in jobs.items():
 for stock in ['KGHM','PEKAO','PKNORLEN','PKOBP','PZU']:
  for seed in range(5):
   folder=f'batch/{regime}-{stock}-s{seed}'
   dest=Path('results/cq-011')/job/folder
   if len(list(dest.rglob('*-predictions.npz')))==11 and len(list(dest.rglob('*.pt')))==7:continue
   tasks.append((job,folder))
 for name in ['batch/batch.json','batch/progress.txt','progress.txt','cq-threads.json']:tasks.append((job,name))
def fetch(task):
 job,folder=task
 for attempt in range(3):
  try:
   r=subprocess.run(['/Users/zyy/.local/bin/cq','fetch',job,'--path',folder,'--to','results/cq-011'],capture_output=True,text=True,timeout=300)
   if r.returncode==0:return dict(job=job,path=folder,ok=True,message=r.stdout.strip())
   error=(r.stderr+r.stdout)[-1000:]
  except subprocess.TimeoutExpired:error='Fetch timed out after 300 seconds'
  time.sleep(2)
 return dict(job=job,path=folder,ok=False,error=error)
reports=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 for r in pool.map(fetch,tasks):
  reports.append(r);print(json.dumps(r),flush=True)
Path('results/engineering/cascade-011/fetch-receipt.json').write_text(json.dumps(reports,indent=2)+'\n')
if any(not r['ok'] for r in reports):raise SystemExit(1)
